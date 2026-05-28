"""Adaptadores de infraestructura para servicios externos (patrón Adapter)."""

from infrastructure.adapters.currency_adapter import (
    ExchangeRateAdapter,
    ICurrencyService,
)

__all__ = ["ICurrencyService", "ExchangeRateAdapter"]
