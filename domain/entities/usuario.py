from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.enums import RolUsuario


@dataclass(slots=True)
class Usuario:
    id: int | None
    nombre: str
    email: str
    fecha_registro: datetime
    rol: RolUsuario = RolUsuario.CLIENTE
    activo: bool = True

