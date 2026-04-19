from __future__ import annotations

from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.exceptions import (
    ApplicationError,
    BusinessRuleViolation,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from application.services.alquiler_service import AlquilerService
from application.services.equipo_service import EquipoService
from application.services.usuario_service import UsuarioService
from infrastructure.repositories.django_repositories import (
    DjangoAlquilerRepository,
    DjangoEquipoRepository,
    DjangoUsuarioRepository,
)
from presentation.api.mappers import (
    alquiler_to_dict,
    equipo_to_dict,
    usuario_to_dict,
)
from presentation.api.serializers import (
    AlquilerCreateSerializer,
    AlquilerSerializer,
    EquipoSerializer,
    UsuarioCreateSerializer,
)


def _build_usuario_service() -> UsuarioService:
    return UsuarioService(usuario_repository=DjangoUsuarioRepository())


def _build_equipo_service() -> EquipoService:
    return EquipoService(equipo_repository=DjangoEquipoRepository())


def _build_alquiler_service() -> AlquilerService:
    return AlquilerService(
        usuario_repository=DjangoUsuarioRepository(),
        equipo_repository=DjangoEquipoRepository(),
        alquiler_repository=DjangoAlquilerRepository(),
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
    def post(self, request: HttpRequest) -> Response:
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = _build_usuario_service()
        usuario = service.crear_usuario(
            nombre=serializer.validated_data["nombre"],
            email=serializer.validated_data["email"],
        )
        data = usuario_to_dict(usuario)
        return Response(data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class EquipoListView(APIView):
    def get(self, request: HttpRequest) -> Response:
        service = _build_equipo_service()
        equipos = service.listar_equipos()
        data = [equipo_to_dict(e) for e in equipos]
        serializer = EquipoSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class AlquilerCreateView(APIView):
    def post(self, request: HttpRequest) -> Response:
        serializer = AlquilerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = _build_alquiler_service()

        try:
            alquiler = service.crear_alquiler(
                usuario_id=serializer.validated_data["usuario_id"],
                equipo_id=serializer.validated_data["equipo_id"],
                fecha_inicio=serializer.validated_data["fecha_inicio"],
                fecha_fin=serializer.validated_data["fecha_fin"],
            )
        except ApplicationError as exc:
            return _handle_application_error(exc)

        data = alquiler_to_dict(alquiler)
        response_serializer = AlquilerSerializer(data=data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

