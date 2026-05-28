"""
Tareas asíncronas Celery — capa de aplicación.
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@shared_task(name="application.tasks.generar_reporte_alquileres")
def generar_reporte_alquileres() -> str:
    mensaje = str(_("Reporte de alquileres generado correctamente."))
    logger.info(mensaje)
    return mensaje


@shared_task(name="application.tasks.enviar_notificacion")
def enviar_notificacion(usuario_id: int, mensaje: str) -> str:
    registro = str(
        _("Notificación enviada al usuario %(usuario_id)s: %(mensaje)s")
        % {"usuario_id": usuario_id, "mensaje": mensaje}
    )
    logger.info(registro)
    return registro


@shared_task(name="application.tasks.notificar_alquiler_creado")
def notificar_alquiler_creado(alquiler_id: int, usuario_id: int, equipo_nombre: str) -> str:
    mensaje = str(
        _("Alquiler #%(id)s registrado para el equipo «%(equipo)s». Pendiente de pago.")
        % {"id": alquiler_id, "equipo": equipo_nombre}
    )
    enviar_notificacion.delay(usuario_id, mensaje)
    logger.info("notificar_alquiler_creado: %s", mensaje)
    return mensaje


@shared_task(name="application.tasks.notificar_pago_confirmado")
def notificar_pago_confirmado(alquiler_id: int, usuario_id: int, monto: str) -> str:
    mensaje = str(
        _("Pago confirmado para alquiler #%(id)s por %(monto)s.")
        % {"id": alquiler_id, "monto": monto}
    )
    enviar_notificacion.delay(usuario_id, mensaje)
    logger.info("notificar_pago_confirmado: %s", mensaje)
    return mensaje
