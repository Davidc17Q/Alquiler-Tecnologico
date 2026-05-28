from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Sequence

from domain.entities.alquiler import Alquiler
from domain.entities.equipo import Equipo
from domain.entities.pago import Pago
from domain.entities.penalizacion import Penalizacion
from domain.entities.usuario import Usuario


class UsuarioRepository(ABC):
    """Puerto de persistencia para usuarios."""

    @abstractmethod
    def get_by_id(self, usuario_id: int) -> Usuario | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, usuario: Usuario) -> Usuario:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> Usuario | None:
        raise NotImplementedError

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        raise NotImplementedError


class EquipoRepository(ABC):
    """Puerto de persistencia para equipos."""

    @abstractmethod
    def get_by_id(self, equipo_id: int) -> Equipo | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> Sequence[Equipo]:
        raise NotImplementedError

    @abstractmethod
    def count_all(self) -> int:
        """Total de equipos registrados en el sistema."""
        raise NotImplementedError


class AlquilerRepository(ABC):
    """Puerto de persistencia para alquileres."""

    @abstractmethod
    def get_by_id(self, alquiler_id: int) -> Alquiler | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, alquiler: Alquiler) -> Alquiler:
        raise NotImplementedError

    @abstractmethod
    def save(self, alquiler: Alquiler) -> Alquiler:
        """Persiste cambios en un alquiler existente."""
        raise NotImplementedError

    @abstractmethod
    def exists_overlapping_for_equipo(
        self,
        equipo_id: int,
        fecha_inicio: date,
        fecha_fin: date,
    ) -> bool:
        """Indica si ya existe un alquiler que se solape con el rango
        de fechas indicado para el equipo dado.
        """
        raise NotImplementedError

    @abstractmethod
    def count_activos(self) -> int:
        """Cuenta alquileres en estado pendiente o pagado (aún activos)."""
        raise NotImplementedError

    @abstractmethod
    def list_by_usuario_id(self, usuario_id: int) -> Sequence[Alquiler]:
        """Lista todos los alquileres de un usuario, más recientes primero."""
        raise NotImplementedError


class PagoRepository(ABC):
    """Puerto de persistencia para pagos."""

    @abstractmethod
    def get_by_id(self, pago_id: int) -> Pago | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, pago: Pago) -> Pago:
        raise NotImplementedError

    @abstractmethod
    def save(self, pago: Pago) -> Pago:
        raise NotImplementedError


class PenalizacionRepository(ABC):
    """Puerto de persistencia para penalizaciones."""

    @abstractmethod
    def create(self, penalizacion: Penalizacion) -> Penalizacion:
        raise NotImplementedError

    @abstractmethod
    def exists_for_alquiler(self, alquiler_id: int) -> bool:
        raise NotImplementedError


