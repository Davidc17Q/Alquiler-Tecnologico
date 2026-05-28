"""
Servicio de autenticación por sesión — capa de aplicación.
"""

from __future__ import annotations

from datetime import datetime, timezone

from django.contrib.auth.hashers import check_password, make_password
from django.utils.translation import gettext_lazy as _

from application.exceptions import AuthenticationError, ConflictError, NotFoundError
from application.interfaces.repositories import UsuarioRepository
from domain.entities.usuario import Usuario
from domain.enums import RolUsuario


class AuthService:
    def __init__(self, usuario_repository: UsuarioRepository) -> None:
        self._usuarios = usuario_repository

    def registrar(self, nombre: str, email: str, password: str) -> Usuario:
        email_normalizado = email.strip().lower()
        if len(password) < 6:
            raise AuthenticationError(_("La contraseña debe tener al menos 6 caracteres."))
        if self._usuarios.exists_by_email(email_normalizado):
            raise ConflictError(_("Ya existe una cuenta registrada con ese correo."))
        usuario = Usuario(
            id=None,
            nombre=nombre.strip(),
            email=email_normalizado,
            fecha_registro=datetime.now(timezone.utc),
            rol=RolUsuario.CLIENTE,
            activo=True,
        )
        return self._usuarios.create(usuario, password_hash=make_password(password))

    def iniciar_sesion(self, email: str, password: str) -> Usuario:
        email_normalizado = email.strip().lower()
        usuario = self._usuarios.get_by_email(email_normalizado)
        if usuario is None:
            raise NotFoundError(_("No hay cuenta con ese correo. Regístrate primero."))
        if not usuario.activo:
            raise AuthenticationError(_("Tu cuenta está bloqueada. Contacta al soporte."))
        stored = self._usuarios.get_password_hash(usuario.id)
        if not stored or not check_password(password, stored):
            raise AuthenticationError(_("Correo o contraseña incorrectos."))
        return usuario

    def obtener_usuario(self, usuario_id: int) -> Usuario:
        usuario = self._usuarios.get_by_id(usuario_id)
        if usuario is None:
            raise NotFoundError(_("La sesión ya no es válida. Inicia sesión de nuevo."))
        return usuario
