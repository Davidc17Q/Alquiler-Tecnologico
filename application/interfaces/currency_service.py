"""Puerto para servicios externos de tasas de cambio."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ICurrencyService(ABC):
    """Abstracción para obtener tasas de cambio (Adapter Pattern)."""

    @abstractmethod
    def get_rate(self, currency: str) -> float:
        raise NotImplementedError
