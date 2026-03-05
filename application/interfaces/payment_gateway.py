from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Mapping


class PaymentGateway(ABC):
    """Abstracción de pasarela de pagos.

    La capa de aplicación depende de esta interfaz y no de una
    implementación concreta, cumpliendo el Principio de Inversión
    de Dependencias (DIP). La selección de la implementación
    concreta se delega a una Factory en la capa de infraestructura.
    """

    @abstractmethod
    def charge(
        self,
        amount: Decimal,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        """Intenta cobrar el monto indicado.

        Devuelve un identificador de transacción si el cobro
        fue exitoso o lanza una excepción en caso contrario.
        """
        raise NotImplementedError

