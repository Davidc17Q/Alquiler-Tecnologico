"""
Servicio de conversión de precios — capa de aplicación.

Depende del puerto ICurrencyService (inyectado), no de requests ni de
detalles HTTP de la API externa.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.utils.translation import gettext_lazy as _

from application.interfaces.currency_service import ICurrencyService


class CurrencyConversionService:
    """Convierte un precio en USD a COP usando la tasa vigente."""

    def __init__(self, currency_service: ICurrencyService) -> None:
        self._currency_service = currency_service

    def convertir_precio_usd_a_cop(self, precio_usd: float) -> dict[str, Any]:
        if precio_usd < 0:
            raise ValueError(_("El precio en USD debe ser mayor o igual a cero."))

        tasa_cop = self._currency_service.get_rate("COP")
        precio_cop = (Decimal(str(precio_usd)) * Decimal(str(tasa_cop))).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
        return {
            "precio_usd": precio_usd,
            "precio_cop": int(precio_cop),
        }
