from __future__ import annotations

from abc import ABC, abstractmethod


class NotificationGateway(ABC):
    """Abstracción para el envío de notificaciones (ej. email).

    La capa de aplicación solo conoce esta interfaz, no cómo se
    envía realmente el correo (SMTP, servicio externo, etc.),
    respetando el Principio de Inversión de Dependencias.
    """

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> None:
        """Envía un mensaje de notificación al destinatario."""
        raise NotImplementedError

