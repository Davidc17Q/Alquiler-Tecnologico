"""
Vistas de autenticación por sesión Django — capa de presentación.

Persiste usuario_id en request.session; la lógica de negocio
permanece en AuthService.
"""

from __future__ import annotations

from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.exceptions import ApplicationError, AuthenticationError, ConflictError, NotFoundError
from application.services.auth_service import AuthService
from domain.enums import AlquilerEstado
from infrastructure.repositories.django_repositories import (
    DjangoAlquilerRepository,
    DjangoUsuarioRepository,
)
from presentation.api.mappers import usuario_to_dict
from presentation.api.serializers import AuthLoginSerializer, UsuarioCreateSerializer

SESSION_USUARIO_KEY = "usuario_id"


def _build_auth_service() -> AuthService:
    return AuthService(usuario_repository=DjangoUsuarioRepository())


def _usuario_id_en_sesion(request: HttpRequest) -> int | None:
    raw = request.session.get(SESSION_USUARIO_KEY)
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _establecer_sesion(request: HttpRequest, usuario_id: int) -> None:
    request.session[SESSION_USUARIO_KEY] = usuario_id
    request.session.modified = True


def _requiere_sesion(request: HttpRequest) -> int:
    usuario_id = _usuario_id_en_sesion(request)
    if usuario_id is None:
        raise AuthenticationError(_("Debes iniciar sesión para continuar."))
    return usuario_id


def _handle_auth_error(exc: ApplicationError) -> Response:
    if isinstance(exc, AuthenticationError):
        return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)
    if isinstance(exc, NotFoundError):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, ConflictError):
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class AuthRegistroView(APIView):
    """POST /api/v1/auth/registro/ — crea cuenta e inicia sesión."""

    def post(self, request: HttpRequest) -> Response:
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = _build_auth_service()
        try:
            usuario = service.registrar(
                nombre=serializer.validated_data["nombre"],
                email=serializer.validated_data["email"],
            )
        except ApplicationError as exc:
            return _handle_auth_error(exc)
        _establecer_sesion(request, usuario.id)
        return Response(usuario_to_dict(usuario), status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class AuthLoginView(APIView):
    """POST /api/v1/auth/login/ — inicia sesión por correo."""

    def post(self, request: HttpRequest) -> Response:
        serializer = AuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = _build_auth_service()
        try:
            usuario = service.iniciar_sesion(email=serializer.validated_data["email"])
        except ApplicationError as exc:
            return _handle_auth_error(exc)
        _establecer_sesion(request, usuario.id)
        return Response(usuario_to_dict(usuario), status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class AuthLogoutView(APIView):
    """POST /api/v1/auth/logout/ — cierra la sesión."""

    def post(self, request: HttpRequest) -> Response:
        request.session.flush()
        return Response({"detail": str(_("Sesión cerrada correctamente."))}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class AuthMeView(APIView):
    """GET /api/v1/auth/me/ — usuario de la sesión activa y resumen de alquileres."""

    def get(self, request: HttpRequest) -> Response:
        try:
            usuario_id = _requiere_sesion(request)
        except AuthenticationError as exc:
            return _handle_auth_error(exc)
        service = _build_auth_service()
        try:
            usuario = service.obtener_usuario(usuario_id)
        except ApplicationError as exc:
            return _handle_auth_error(exc)

        alquileres = DjangoAlquilerRepository().list_by_usuario_id(usuario_id)
        activos = sum(
            1
            for a in alquileres
            if a.estado in (AlquilerEstado.PENDIENTE, AlquilerEstado.PAGADO)
        )
        pendientes_pago = sum(1 for a in alquileres if a.estado == AlquilerEstado.PENDIENTE)
        finalizados = sum(1 for a in alquileres if a.estado == AlquilerEstado.FINALIZADO)

        return Response(
            {
                "usuario": usuario_to_dict(usuario),
                "resumen": {
                    "total_alquileres": len(alquileres),
                    "activos": activos,
                    "pendientes_pago": pendientes_pago,
                    "finalizados": finalizados,
                },
            },
            status=status.HTTP_200_OK,
        )
