from __future__ import annotations

from datetime import date
from decimal import Decimal

from application.interfaces.notification_gateway import NotificationGateway
from application.interfaces.repositories import AlquilerRepository, PenalizacionRepository
from domain.entities.penalizacion import Penalizacion


class PenalizacionService:
    """Service Layer para penalizaciones y avisos de retraso.

    Aquí se concentran las reglas de negocio relacionadas con
    penalizaciones (cálculo de monto base, cuándo avisar, etc.),
    manteniendo las vistas y los modelos libres de esta lógica.
    """

    def __init__(
        self,
        alquiler_repository: AlquilerRepository,
        penalizacion_repository: PenalizacionRepository,
        notification_gateway: NotificationGateway,
    ) -> None:
        self._alquileres = alquiler_repository
        self._penalizaciones = penalizacion_repository
        self._notifications = notification_gateway

    def generar_penalizacion_por_retraso(self, alquiler_id: int) -> Penalizacion | None:
        alquiler = self._alquileres.get_by_id(alquiler_id)
        if alquiler is None:
            return None

        hoy = date.today()
        if hoy <= alquiler.fecha_fin:
            return None

        if self._penalizaciones.exists_for_alquiler(alquiler_id):
            return None

        dias_retraso = (hoy - alquiler.fecha_fin).days
        monto = (alquiler.equipo.precio_por_dia * Decimal(dias_retraso)).quantize(Decimal("0.01"))

        penalizacion = Penalizacion(
            id=None,
            alquiler=alquiler,
            motivo=f"Retraso de {dias_retraso} día(s) en la devolución del equipo.",
            monto=monto,
        )
        creada = self._penalizaciones.create(penalizacion)

        subject = "Aviso de penalización por retraso - TechRent"
        body = (
            f"Hola {alquiler.usuario.nombre},\n\n"
            f"Tu alquiler del equipo '{alquiler.equipo.nombre}' debía finalizar el {alquiler.fecha_fin}.\n"
            f"Se ha generado una penalización por retraso de {dias_retraso} día(s) "
            f"por un monto de {creada.monto}.\n\n"
            "Por favor, ponte en contacto con soporte de TechRent si tienes dudas."
        )
        self._notifications.send_email(
            to=alquiler.usuario.email,
            subject=subject,
            body=body,
        )

        return creada

    def enviar_advertencia_vencimiento(self, alquiler_id: int) -> None:
        alquiler = self._alquileres.get_by_id(alquiler_id)
        if alquiler is None:
            return

        hoy = date.today()
        # Enviamos advertencia solo el día anterior a la fecha de fin
        if (alquiler.fecha_fin - hoy).days != 1:
            return

        subject = "Recordatorio de vencimiento de alquiler - TechRent"
        body = (
            f"Hola {alquiler.usuario.nombre},\n\n"
            f"Te recordamos que tu alquiler del equipo '{alquiler.equipo.nombre}' "
            f"finaliza el {alquiler.fecha_fin}.\n"
            "Evita penalizaciones devolviendo el equipo a tiempo.\n\n"
            "Gracias por utilizar TechRent."
        )
        self._notifications.send_email(
            to=alquiler.usuario.email,
            subject=subject,
            body=body,
        )

