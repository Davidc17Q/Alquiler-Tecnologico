from __future__ import annotations

from typing import Sequence

from application.exceptions import NotFoundError
from application.interfaces.repositories import EquipoRepository
from domain.entities.equipo import Equipo


class EquipoService:
    """Service Layer para equipos.

    Centraliza la lógica relacionada con equipos (por ejemplo,
    futuras reglas de disponibilidad o filtrado avanzado) sin
    contaminar modelos ni vistas.
    """

    def __init__(self, equipo_repository: EquipoRepository) -> None:
        self._equipos = equipo_repository

    def listar_equipos(self) -> Sequence[Equipo]:
        return self._equipos.list_all()

    def obtener_equipo(self, equipo_id: int) -> Equipo:
        equipo = self._equipos.get_by_id(equipo_id)
        if equipo is None:
            raise NotFoundError("Equipo no encontrado.")
        return equipo

