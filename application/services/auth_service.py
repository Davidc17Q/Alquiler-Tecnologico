"""
Servicio de autenticación por sesión — capa de aplicación.

Gestiona registro e inicio de sesión usando el agregado Usuario
sin acoplar la lógica a request.session (eso vive en presentación).
"""

from __future__ import annotations

from datetime import datetime, timezone

from django.utils.translation import gettext_lazy as _

from application.exceptions import ConflictError, NotFoundError
from application.interfaces.repositories import UsuarioRepository
from domain.entities.usuario import Usuario


class AuthService:
    """Casos de uso de registro e identificación de clientes."""

    def __init__(self, usuario_repository: UsuarioRepository) -> None:
        self._usuarios = usuario_repository

    def registrar(self, nombre: str, email: str) -> Usuario:
        email_normalizado = email.strip().lower()
        if self._usuarios.exists_by_email(email_normalizado):
            raise ConflictError(_("Ya existe una cuenta registrada con ese correo."))
        usuario = Usuario(
            id=None,
            nombre=nombre.strip(),
            email=email_normalizado,
            fecha_registro=datetime.now(timezone.utc),
        )
        return self._usuarios.create(usuario)

    def iniciar_sesion(self, email: str) -> Usuario:
        email_normalizado = email.strip().lower()
        usuario = self._usuarios.get_by_email(email_normalizado)
        if usuario is None:
            raise NotFoundError(_("No hay cuenta con ese correo. Regístrate primero."))
        return usuario

    def obtener_usuario(self, usuario_id: int) -> Usuario:
        usuario = self._usuarios.get_by_id(usuario_id)
        if usuario is None:
            raise NotFoundError(_("La sesión ya no es válida. Inicia sesión de nuevo."))
        return usuario
