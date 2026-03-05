from __future__ import annotations

from django.conf import settings

from application.interfaces.payment_gateway import PaymentGateway
from infrastructure.payment_gateways.gateways import FakePaymentGateway, StripePaymentGateway


class PaymentGatewayFactory:
    """Factory para crear instancias de pasarelas de pago.

    La selección de la implementación concreta depende de una
    variable de configuración (`PAYMENT_GATEWAY_BACKEND`),
    lo que permite escalar a nuevos proveedores (PayPal,
    MercadoPago, etc.) sin modificar la capa de aplicación.

    Gracias a este patrón Factory, el sistema está preparado
    para integrarse fácilmente detrás de un API Gateway que
    redirija peticiones hacia distintos servicios de pago.
    """

    @staticmethod
    def from_settings() -> PaymentGateway:
        backend = getattr(settings, "PAYMENT_GATEWAY_BACKEND", "fake").lower()
        if backend == "stripe":
            api_key = getattr(settings, "STRIPE_API_KEY", None)
            return StripePaymentGateway(api_key=api_key)
        return FakePaymentGateway()

