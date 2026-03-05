from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.entities.alquiler import Alquiler
from domain.entities.equipo import Equipo
from domain.entities.usuario import Usuario
from domain.enums import AlquilerEstado


@dataclass
class _AlquilerDraft:
    usuario: Usuario | None = None
    equipo: Equipo | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    costo_total: Decimal | None = None
    estado: AlquilerEstado = AlquilerEstado.PENDIENTE


class AlquilerBuilder:
    """Builder para construir la entidad Alquiler paso a paso.

    El patrón Builder mejora la construcción porque:
    - Hace explícitas las dependencias necesarias (usuario, equipo, fechas).
    - Permite calcular el costo en un paso controlado, validando valores.
    - Facilita la extensión futura (ej. descuentos, cupones) sin romper
      la firma del constructor de la entidad.
    """

    def __init__(self) -> None:
        self._draft = _AlquilerDraft()

    def set_usuario(self, usuario: Usuario) -> "AlquilerBuilder":
        self._draft.usuario = usuario
        return self

    def set_equipo(self, equipo: Equipo) -> "AlquilerBuilder":
        self._draft.equipo = equipo
        return self

    def set_fechas(self, fecha_inicio: date, fecha_fin: date) -> "AlquilerBuilder":
        self._draft.fecha_inicio = fecha_inicio
        self._draft.fecha_fin = fecha_fin
        return self

    def calcular_costo(self) -> "AlquilerBuilder":
        if (
            self._draft.fecha_inicio is None
            or self._draft.fecha_fin is None
            or self._draft.equipo is None
        ):
            raise ValueError(
                "Para calcular el costo se requiere equipo y rango de fechas definido."
            )

        dias = (self._draft.fecha_fin - self._draft.fecha_inicio).days
        if dias <= 0:
            raise ValueError("El número de días de alquiler debe ser mayor a cero.")

        self._draft.costo_total = self._draft.equipo.precio_por_dia * dias
        return self

    def build(self) -> Alquiler:
        if (
            self._draft.usuario is None
            or self._draft.equipo is None
            or self._draft.fecha_inicio is None
            or self._draft.fecha_fin is None
            or self._draft.costo_total is None
        ):
            raise ValueError("El alquiler está incompleto; faltan datos obligatorios.")

        return Alquiler(
            id=None,
            usuario=self._draft.usuario,
            equipo=self._draft.equipo,
            fecha_inicio=self._draft.fecha_inicio,
            fecha_fin=self._draft.fecha_fin,
            estado=self._draft.estado,
            costo_total=self._draft.costo_total,
        )

