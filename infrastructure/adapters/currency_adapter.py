"""
Adaptador de tasas de cambio — patrón Adapter + inversión de dependencias.

La capa de aplicación depende de ICurrencyService; esta implementación
concreta encapsula la comunicación HTTP con exchangerate-api.com.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import requests

logger = logging.getLogger(__name__)

# URL pública de tasas basadas en USD
EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"


class ICurrencyService(ABC):
    """Puerto abstracto para obtener tasas de cambio."""

    @abstractmethod
    def get_rate(self, currency: str) -> float:
        """Devuelve la tasa de conversión desde USD hacia la moneda indicada."""
        raise NotImplementedError


class ExchangeRateAdapter(ICurrencyService):
    """Implementación concreta que consume la API externa de tipos de cambio."""

    def __init__(
        self,
        api_url: str = EXCHANGE_RATE_API_URL,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._api_url = api_url
        self._timeout = timeout_seconds

    def get_rate(self, currency: str) -> float:
        moneda = currency.strip().upper()
        if not moneda:
            raise ValueError("La moneda destino no puede estar vacía.")

        try:
            response = requests.get(self._api_url, timeout=self._timeout)
            response.raise_for_status()
        except requests.Timeout as exc:
            logger.error("Timeout al consultar API de cambio: %s", exc)
            raise ConnectionError("Tiempo de espera agotado al consultar tasas de cambio.") from exc
        except requests.RequestException as exc:
            logger.error("Error HTTP al consultar API de cambio: %s", exc)
            raise ConnectionError("No fue posible obtener tasas de cambio.") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error("Respuesta JSON inválida de la API de cambio.")
            raise ValueError("La API de cambio devolvió un formato inválido.") from exc

        rates = payload.get("rates")
        if not isinstance(rates, dict):
            raise ValueError("La respuesta no contiene el campo 'rates' esperado.")

        rate = rates.get(moneda)
        if rate is None:
            raise ValueError(f"Moneda no soportada o no encontrada: {moneda}")

        try:
            return float(rate)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Tasa inválida para {moneda}.") from exc
