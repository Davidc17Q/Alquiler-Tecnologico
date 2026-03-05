from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from domain.entities.alquiler import Alquiler


@dataclass(slots=True)
class Penalizacion:
    """Entidad base de penalización.

    Se deja intencionalmente simple para permitir su
    ampliación en futuras iteraciones del dominio.
    """

    id: int | None
    alquiler: Alquiler
    motivo: str
    monto: Decimal

