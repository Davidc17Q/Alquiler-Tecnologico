"""Vistas de autenticación por sesión Django — capa de presentación."""

from __future__ import annotations

from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.exceptions import ApplicationError
from presentation.api.mappers import usuario_to_dict
from presentation.api.serializers import AuthLoginSerializer, UsuarioCreateSerializer
from presentation.api.session_auth import establecer_sesion, handle_auth_error, requiere_sesion
from presentation.di import build_auth_service, build_cliente_resumen_service


@method_decorator(csrf_exempt, name="dispatch")
class AuthRegistroView(APIView):
    def post(self, request: HttpRequest) -> Response:
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = build_auth_service()
        try:
            usuario = service.registrar(
                nombre=serializer.validated_data["nombre"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except ApplicationError as exc:
            return handle_auth_error(exc)
        establecer_sesion(request, usuario.id)
        return Response(usuario_to_dict(usuario), status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class AuthLoginView(APIView):
    def post(self, request: HttpRequest) -> Response:
        serializer = AuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = build_auth_service()
        try:
            usuario = service.iniciar_sesion(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except ApplicationError as exc:
            return handle_auth_error(exc)
        establecer_sesion(request, usuario.id)
        return Response(usuario_to_dict(usuario), status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class AuthLogoutView(APIView):
    def post(self, request: HttpRequest) -> Response:
        request.session.flush()
        from django.utils.translation import gettext_lazy as _

        return Response({"detail": str(_("Sesión cerrada correctamente."))}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class AuthMeView(APIView):
    def get(self, request: HttpRequest) -> Response:
        try:
            usuario_id = requiere_sesion(request)
        except ApplicationError as exc:
            return handle_auth_error(exc)
        auth = build_auth_service()
        resumen_svc = build_cliente_resumen_service()
        try:
            usuario = auth.obtener_usuario(usuario_id)
            resumen = resumen_svc.obtener_resumen(usuario)
        except ApplicationError as exc:
            return handle_auth_error(exc)
        return Response(
            {"usuario": usuario_to_dict(usuario), "resumen": resumen},
            status=status.HTTP_200_OK,
        )
