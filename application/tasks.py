"""
Tareas asíncronas Celery — capa de aplicación.

Simulan procesos de larga duración (reportes, notificaciones) desacoplados
del ciclo request/response HTTP.
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@shared_task(name="application.tasks.generar_reporte_alquileres")
def generar_reporte_alquileres() -> str:
    """Simula la generación de un reporte de alquileres en segundo plano."""
    mensaje = str(_("Reporte de alquileres generado correctamente."))
    logger.info(mensaje)
    print(f"[CELERY] {mensaje}")
    return mensaje


@shared_task(name="application.tasks.enviar_notificacion")
def enviar_notificacion(usuario_id: int, mensaje: str) -> str:
    """Simula el envío de una notificación a un usuario."""
    registro = str(
        _("Notificación enviada al usuario %(usuario_id)s: %(mensaje)s")
        % {"usuario_id": usuario_id, "mensaje": mensaje}
    )
    logger.info(registro)
    print(f"[CELERY] {registro}")
    return registro
