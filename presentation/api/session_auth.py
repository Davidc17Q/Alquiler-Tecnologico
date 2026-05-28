"""
Helpers de sesión y autorización por rol — presentación API.
"""

from __future__ import annotations

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from application.exceptions import ApplicationError, AuthenticationError, ForbiddenError
from application.services.auth_service import AuthService
from domain.enums import RolUsuario
from infrastructure.repositories.django_repositories import DjangoUsuarioRepository
from rest_framework import status
from rest_framework.response import Response

SESSION_USUARIO_KEY = "usuario_id"
ROLES_STAFF = frozenset({RolUsuario.VENDOR, RolUsuario.ADMIN})


def build_auth_service() -> AuthService:
    return AuthService(usuario_repository=DjangoUsuarioRepository())


_build_auth_service = build_auth_service


def usuario_id_en_sesion(request: HttpRequest) -> int | None:
    raw = request.session.get(SESSION_USUARIO_KEY)
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def establecer_sesion(request: HttpRequest, usuario_id: int) -> None:
    request.session[SESSION_USUARIO_KEY] = usuario_id
    request.session.modified = True


def requiere_sesion(request: HttpRequest) -> int:
    usuario_id = usuario_id_en_sesion(request)
    if usuario_id is None:
        raise AuthenticationError(_("Debes iniciar sesión para continuar."))
    return usuario_id


def requiere_staff(request: HttpRequest) -> int:
    usuario_id = requiere_sesion(request)
    usuario = _build_auth_service().obtener_usuario(usuario_id)
    if usuario.rol not in ROLES_STAFF:
        raise ForbiddenError(_("No tienes acceso al panel administrativo."))
    if not usuario.activo:
        raise AuthenticationError(_("Tu cuenta está desactivada."))
    return usuario_id


def handle_auth_error(exc: ApplicationError) -> Response:
    if isinstance(exc, ForbiddenError):
        return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
    if isinstance(exc, AuthenticationError):
        return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)
    from application.exceptions import ConflictError, NotFoundError

    if isinstance(exc, NotFoundError):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, ConflictError):
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
