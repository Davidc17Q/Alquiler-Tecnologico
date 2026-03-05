from __future__ import annotations

from django.conf import settings

from application.interfaces.notification_gateway import NotificationGateway
from infrastructure.notifications.gateways import (
    ConsoleNotificationGateway,
    DjangoEmailNotificationGateway,
)


class NotificationGatewayFactory:
    """Factory para crear instancias de NotificationGateway.

    Permite cambiar la forma de enviar notificaciones (consola,
    email real, servicio externo) sin tocar la capa de aplicación.
    """

    @staticmethod
    def from_settings() -> NotificationGateway:
        backend = getattr(settings, "NOTIFICATION_GATEWAY_BACKEND", "console").lower()
        if backend == "email":
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            return DjangoEmailNotificationGateway(from_email=from_email)
        return ConsoleNotificationGateway()

