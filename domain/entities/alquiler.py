from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.entities.equipo import Equipo
from domain.entities.usuario import Usuario
from domain.enums import AlquilerEstado


@dataclass(slots=True)
class Alquiler:
    id: int | None
    usuario: Usuario
    equipo: Equipo
    fecha_inicio: date
    fecha_fin: date
    estado: AlquilerEstado
    costo_total: Decimal

