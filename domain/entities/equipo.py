from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from domain.enums import EquipoEstado


@dataclass(slots=True)
class Equipo:
    id: int | None
    nombre: str
    categoria: str
    precio_por_dia: Decimal
    estado: EquipoEstado

