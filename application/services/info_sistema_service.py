"""
Servicio de información del sistema — capa de aplicación.

Agrega estadísticas reales desde repositorios sin acoplar la presentación
a modelos Django ni a consultas SQL directas.
"""

from __future__ import annotations

import os
from typing import Any

from django.utils.translation import gettext_lazy as _

from application.interfaces.repositories import AlquilerRepository, EquipoRepository


class InfoSistemaService:
    """Expone metadatos y contadores del sistema de alquiler."""

    def __init__(
        self,
        equipo_repository: EquipoRepository,
        alquiler_repository: AlquilerRepository,
    ) -> None:
        self._equipos = equipo_repository
        self._alquileres = alquiler_repository

    def obtener_informacion(self) -> dict[str, Any]:
        version = os.environ.get("SYSTEM_VERSION", "1.0.0")
        return {
            "sistema": str(_("Alquiler Tecnológico")),
            "version": version,
            "total_equipos": self._equipos.count_all(),
            "alquileres_activos": self._alquileres.count_activos(),
        }
