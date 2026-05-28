from __future__ import annotations

from datetime import date
from typing import Sequence

from django.utils.translation import gettext_lazy as _

from application.exceptions import BusinessRuleViolation, ConflictError, NotFoundError, ValidationError
from application.interfaces.repositories import AlquilerRepository, EquipoRepository, UsuarioRepository
from domain.builders.alquiler_builder import AlquilerBuilder
from domain.entities.alquiler import Alquiler
from domain.enums import AlquilerEstado


class AlquilerService:
    """Service Layer para el flujo de alquileres.

    Orquesta la creación y gestión de alquileres combinando:
    - Entidades de dominio.
    - Builder de alquiler.
    - Repositorios abstractos.

    De esta forma, todas las reglas de negocio (validaciones de
    fechas, disponibilidad, cálculo de costo) se mantienen fuera
    de vistas, serializers y modelos.
    """

    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        equipo_repository: EquipoRepository,
        alquiler_repository: AlquilerRepository,
    ) -> None:
        self._usuarios = usuario_repository
        self._equipos = equipo_repository
        self._alquileres = alquiler_repository

    def crear_alquiler(
        self,
        usuario_id: int,
        equipo_id: int,
        fecha_inicio: date,
        fecha_fin: date,
    ) -> Alquiler:
        if fecha_inicio >= fecha_fin:
            raise ValidationError(_("La fecha de fin debe ser posterior a la fecha de inicio."))

        usuario = self._usuarios.get_by_id(usuario_id)
        if usuario is None:
            raise NotFoundError(_("Usuario no encontrado."))

        equipo = self._equipos.get_by_id(equipo_id)
        if equipo is None:
            raise NotFoundError(_("Equipo no encontrado."))

        if self._alquileres.exists_overlapping_for_equipo(
            equipo_id=equipo_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        ):
            raise ConflictError(
                _("El equipo no está disponible en el rango de fechas solicitado.")
            )

        builder = AlquilerBuilder()
        try:
            alquiler = (
                builder.set_usuario(usuario)
                .set_equipo(equipo)
                .set_fechas(fecha_inicio, fecha_fin)
                .calcular_costo()
                .build()
            )
        except ValueError as exc:
            raise BusinessRuleViolation(str(exc)) from exc

        return self._alquileres.create(alquiler)

    def listar_por_usuario(self, usuario_id: int) -> Sequence[Alquiler]:
        if self._usuarios.get_by_id(usuario_id) is None:
            raise NotFoundError(_("Usuario no encontrado."))
        return self._alquileres.list_by_usuario_id(usuario_id)

    def marcar_como_pagado(self, alquiler_id: int) -> Alquiler:
        alquiler = self._alquileres.get_by_id(alquiler_id)
        if alquiler is None:
            raise NotFoundError(_("Alquiler no encontrado."))

        if alquiler.estado != AlquilerEstado.PENDIENTE:
            raise ConflictError(_("Solo se pueden marcar como pagados alquileres pendientes."))

        alquiler.estado = AlquilerEstado.PAGADO
        return self._alquileres.save(alquiler)

    def finalizar_alquiler(self, alquiler_id: int) -> Alquiler:
        alquiler = self._alquileres.get_by_id(alquiler_id)
        if alquiler is None:
            raise NotFoundError(_("Alquiler no encontrado."))

        if alquiler.estado != AlquilerEstado.PAGADO:
            raise ConflictError(_("Solo se pueden finalizar alquileres pagados."))

        alquiler.estado = AlquilerEstado.FINALIZADO
        return self._alquileres.save(alquiler)

