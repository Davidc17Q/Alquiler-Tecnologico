from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.core.mail import send_mail

from application.interfaces.notification_gateway import NotificationGateway
from django.conf import settings


class ConsoleNotificationGateway(NotificationGateway):
    """Pasarela de notificaciones que simplemente imprime en consola.

    Útil para desarrollo y pruebas sin configurar un servidor SMTP real.
    """

    def send_email(self, to: str, subject: str, body: str) -> None:
        print(f"[TechRent][NOTIFICACIÓN] To={to} | Subject={subject}\n{body}\n")  # noqa: T201


@dataclass
class DjangoEmailNotificationGateway(NotificationGateway):
    """Pasarela de notificaciones basada en el sistema de emails de Django."""

    from_email: str | None = None

    def send_email(self, to: str, subject: str, body: str) -> None:
        effective_from = self.from_email or getattr(
            settings,
            "DEFAULT_FROM_EMAIL",
            "no-reply@techrent.local",
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=effective_from,
            recipient_list=[to],
            fail_silently=True,
        )

