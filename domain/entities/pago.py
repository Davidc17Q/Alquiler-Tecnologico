from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from domain.entities.alquiler import Alquiler
from domain.enums import MetodoPago, PagoEstado


@dataclass(slots=True)
class Pago:
    id: int | None
    alquiler: Alquiler
    monto: Decimal
    metodo: MetodoPago
    estado: PagoEstado
    fecha_pago: datetime

