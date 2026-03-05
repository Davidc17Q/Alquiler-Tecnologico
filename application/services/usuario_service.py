from __future__ import annotations

from datetime import datetime, timezone

from application.exceptions import NotFoundError
from application.interfaces.repositories import UsuarioRepository
from domain.entities.usuario import Usuario


class UsuarioService:
    """Service Layer para casos de uso de Usuario.

    El Service Layer desacopla la lógica de negocio de la
    infraestructura porque trabaja con entidades de dominio
    e interfaces de repositorio, sin conocer detalles de
    Django ORM ni HTTP. Esto facilita el testeo y el cambio
    de tecnología de persistencia.
    """

    def __init__(self, usuario_repository: UsuarioRepository) -> None:
        self._usuarios = usuario_repository

    def crear_usuario(self, nombre: str, email: str) -> Usuario:
        usuario = Usuario(
            id=None,
            nombre=nombre,
            email=email,
            fecha_registro=datetime.now(timezone.utc),
        )
        return self._usuarios.create(usuario)

    def obtener_usuario(self, usuario_id: int) -> Usuario:
        usuario = self._usuarios.get_by_id(usuario_id)
        if usuario is None:
            raise NotFoundError("Usuario no encontrado.")
        return usuario

