from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping
from uuid import uuid4

from application.interfaces.payment_gateway import PaymentGateway


@dataclass
class StripePaymentGateway(PaymentGateway):
    """Implementación simulada de Stripe.

    En un entorno real, aquí se orquestarían las llamadas HTTP a la
    API de Stripe. Mantener esta lógica en infraestructura permite
    cambiar de proveedor sin tocar la capa de aplicación.
    """

    api_key: str | None = None

    def charge(
        self,
        amount: Decimal,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        # Simulación de cobro exitoso.
        return f"stripe_{uuid4()}"


class FakePaymentGateway(PaymentGateway):
    """Implementación falsa utilizada por defecto en desarrollo y pruebas."""

    def charge(
        self,
        amount: Decimal,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        return f"fake_{uuid4()}"

