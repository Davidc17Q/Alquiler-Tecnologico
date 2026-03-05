from __future__ import annotations

from enum import Enum


class EquipoEstado(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    NO_DISPONIBLE = "NO_DISPONIBLE"


class AlquilerEstado(str, Enum):
    PENDIENTE = "PENDIENTE"
    PAGADO = "PAGADO"
    FINALIZADO = "FINALIZADO"


class PagoEstado(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    FALLIDO = "FALLIDO"


class MetodoPago(str, Enum):
    TARJETA = "TARJETA"
    TRANSFERENCIA = "TRANSFERENCIA"
    EFECTIVO = "EFECTIVO"

