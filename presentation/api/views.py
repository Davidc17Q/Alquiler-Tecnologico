from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.exceptions import (
    ApplicationError,
    AuthenticationError,
    BusinessRuleViolation,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from application.tasks import (
    enviar_notificacion,
    generar_reporte_alquileres,
    notificar_alquiler_creado,
    notificar_pago_confirmado,
)
from presentation.api.mappers import alquiler_detalle_to_dict, equipo_to_dict, usuario_to_dict
from presentation.api.serializers import AlquilerCreateSerializer, UsuarioCreateSerializer
from presentation.api.session_auth import handle_auth_error, requiere_sesion
from presentation.di import (
    build_alquiler_service,
    build_auth_service,
    build_currency_conversion_service,
    build_equipo_service,
    build_info_sistema_service,
    build_usuario_service,
)


def _handle_application_error(exc: ApplicationError) -> Response:
    if isinstance(exc, NotFoundError):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, (ValidationError, BusinessRuleViolation)):
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, ConflictError):
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class UsuarioCreateView(APIView):
    """Legacy — preferir /api/v1/auth/registro/."""

    def post(self, request: HttpRequest) -> Response:
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth = build_auth_service()
        try:
            usuario = auth.registrar(
                nombre=serializer.validated_data["nombre"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except ApplicationError as exc:
            return handle_auth_error(exc)
        return Response(usuario_to_dict(usuario), status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class EquipoListView(APIView):
    def get(self, request: HttpRequest) -> Response:
        service = build_equipo_service()
        equipos = service.listar_equipos()
        data = [equipo_to_dict(e) for e in equipos]
        return Response(data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class AlquilerCreateView(APIView):
    def post(self, request: HttpRequest) -> Response:
        try:
            usuario_id = requiere_sesion(request)
        except AuthenticationError as exc:
            return handle_auth_error(exc)

        serializer = AlquilerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = build_alquiler_service()

        try:
            alquiler = service.crear_alquiler(
                usuario_id=usuario_id,
                equipo_id=serializer.validated_data["equipo_id"],
                fecha_inicio=serializer.validated_data["fecha_inicio"],
                fecha_fin=serializer.validated_data["fecha_fin"],
            )
        except ApplicationError as exc:
            return _handle_application_error(exc)

        notificar_alquiler_creado.delay(
            alquiler.id,
            usuario_id,
            alquiler.equipo.nombre,
        )
        return Response(alquiler_detalle_to_dict(alquiler), status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class MisAlquileresView(APIView):
    def get(self, request: HttpRequest) -> Response:
        try:
            usuario_id = requiere_sesion(request)
        except AuthenticationError as exc:
            return handle_auth_error(exc)

        service = build_alquiler_service()
        try:
            alquileres = service.listar_por_usuario(usuario_id)
        except ApplicationError as exc:
            return _handle_application_error(exc)

        data = [alquiler_detalle_to_dict(a) for a in alquileres]
        return Response(data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class NotificarPagoView(APIView):
    """POST /api/v1/notificar-pago/ — encola tarea Celery tras pago en microservicio."""

    def post(self, request: HttpRequest) -> Response:
        try:
            usuario_id = requiere_sesion(request)
        except AuthenticationError as exc:
            return handle_auth_error(exc)
        alquiler_id = int(request.data.get("alquiler_id", 0))
        monto = str(request.data.get("monto", "0"))
        if alquiler_id < 1:
            return Response({"detail": "alquiler_id inválido"}, status=400)
        notificar_pago_confirmado.delay(alquiler_id, usuario_id, monto)
        return Response(
            {"detail": str(_("Notificación de pago encolada."))},
            status=status.HTTP_202_ACCEPTED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class InfoSistemaView(APIView):
    def get(self, request: HttpRequest) -> Response:
        service = build_info_sistema_service()
        return Response(service.obtener_informacion(), status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class PrecioConversionView(APIView):
    def get(self, request: HttpRequest) -> Response:
        precio_param = request.query_params.get("precio_usd")
        try:
            precio_usd = float(precio_param) if precio_param is not None else settings.PRECIO_USD_DEFAULT
        except (TypeError, ValueError):
            return Response(
                {"detail": str(_("El parámetro precio_usd debe ser numérico."))},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = build_currency_conversion_service()
        try:
            resultado = service.convertir_precio_usd_a_cop(precio_usd)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectionError as exc:
            return Response(
                {"detail": str(_("No fue posible obtener la tasa de cambio."))},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(resultado, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class CeleryDemoView(APIView):
    def post(self, request: HttpRequest) -> Response:
        usuario_id = int(request.data.get("usuario_id", 1))
        mensaje = request.data.get("mensaje", str(_("Alquiler confirmado")))
        generar_reporte_alquileres.delay()
        enviar_notificacion.delay(usuario_id, mensaje)
        return Response(
            {"detail": str(_("Tareas encoladas correctamente."))},
            status=status.HTTP_202_ACCEPTED,
        )
