"""
Gestión administrativa de clientes y equipos.
"""

from __future__ import annotations

from decimal import Decimal

from django.utils.translation import gettext_lazy as _

from application.exceptions import BusinessRuleViolation, NotFoundError
from application.interfaces.repositories import (
    AlquilerRepository,
    EquipoRepository,
    PagoRepository,
    UsuarioRepository,
)
from domain.entities.equipo import Equipo
from domain.entities.usuario import Usuario
from domain.enums import EquipoEstado, RolUsuario


class AdminGestionService:
    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        equipo_repository: EquipoRepository,
        alquiler_repository: AlquilerRepository,
        pago_repository: PagoRepository,
    ) -> None:
        self._usuarios = usuario_repository
        self._equipos = equipo_repository
        self._alquileres = alquiler_repository
        self._pagos = pago_repository

    def listar_clientes(self, busqueda: str = "") -> list[Usuario]:
        usuarios = [u for u in self._usuarios.list_all() if u.rol == RolUsuario.CLIENTE]
        if busqueda:
            term = busqueda.strip().lower()
            usuarios = [
                u for u in usuarios if term in u.nombre.lower() or term in u.email.lower()
            ]
        return usuarios

    def actualizar_cliente(
        self,
        usuario_id: int,
        *,
        nombre: str | None = None,
        activo: bool | None = None,
    ) -> Usuario:
        usuario = self._usuarios.get_by_id(usuario_id)
        if usuario is None or usuario.rol != RolUsuario.CLIENTE:
            raise NotFoundError(_("Cliente no encontrado."))
        if nombre is not None:
            usuario.nombre = nombre.strip()
        if activo is not None:
            usuario.activo = activo
        return self._usuarios.save(usuario)

    def alquileres_de_cliente(self, usuario_id: int):
        return self._alquileres.list_by_usuario_id(usuario_id)

    def pagos_de_cliente(self, usuario_id: int):
        return self._pagos.list_by_usuario_id(usuario_id)

    def listar_equipos(self) -> list[Equipo]:
        return list(self._equipos.list_all())

    def guardar_equipo(
        self,
        *,
        equipo_id: int | None,
        nombre: str,
        categoria: str,
        precio_por_dia: Decimal,
        estado: EquipoEstado,
    ) -> Equipo:
        equipo = Equipo(
            id=equipo_id,
            nombre=nombre.strip(),
            categoria=categoria.strip(),
            precio_por_dia=precio_por_dia,
            estado=estado,
        )
        return self._equipos.save(equipo)

    def eliminar_equipo(self, equipo_id: int) -> None:
        if self._equipos.get_by_id(equipo_id) is None:
            raise NotFoundError(_("Equipo no encontrado."))
        self._equipos.delete_by_id(equipo_id)

    def listar_alquileres(self):
        return self._alquileres.list_all()
