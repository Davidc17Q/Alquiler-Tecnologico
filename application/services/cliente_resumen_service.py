"""Resumen de alquileres del cliente autenticado."""

from __future__ import annotations

from typing import Any

from application.interfaces.repositories import AlquilerRepository
from domain.enums import AlquilerEstado, RolUsuario
from domain.entities.usuario import Usuario


class ClienteResumenService:
    def __init__(self, alquiler_repository: AlquilerRepository) -> None:
        self._alquileres = alquiler_repository

    def obtener_resumen(self, usuario: Usuario) -> dict[str, Any] | None:
        if usuario.rol != RolUsuario.CLIENTE:
            return None
        alquileres = self._alquileres.list_by_usuario_id(usuario.id)
        activos = sum(
            1
            for a in alquileres
            if a.estado in (AlquilerEstado.PENDIENTE, AlquilerEstado.PAGADO)
        )
        pendientes_pago = sum(1 for a in alquileres if a.estado == AlquilerEstado.PENDIENTE)
        finalizados = sum(1 for a in alquileres if a.estado == AlquilerEstado.FINALIZADO)
        return {
            "total_alquileres": len(alquileres),
            "activos": activos,
            "pendientes_pago": pendientes_pago,
            "finalizados": finalizados,
        }
