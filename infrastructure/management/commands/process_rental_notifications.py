from __future__ import annotations

from datetime import date

from django.core.management.base import BaseCommand

from application.services.penalizacion_service import PenalizacionService
from infrastructure.notifications.factory import NotificationGatewayFactory
from infrastructure.repositories.django_repositories import (
    DjangoAlquilerRepository,
    DjangoPenalizacionRepository,
)
from infrastructure.models import AlquilerModel


class Command(BaseCommand):
    help = (
        "Procesa advertencias y penalizaciones de alquileres según fecha_fin.\n"
        "- Envía advertencia un día antes de la fecha_fin.\n"
        "- Genera penalización y avisa si la fecha_fin ya pasó."
    )

    def handle(self, *args, **options) -> None:
        hoy = date.today()
        notification_gateway = NotificationGatewayFactory.from_settings()
        service = PenalizacionService(
            alquiler_repository=DjangoAlquilerRepository(),
            penalizacion_repository=DjangoPenalizacionRepository(),
            notification_gateway=notification_gateway,
        )

        alquileres = AlquilerModel.objects.select_related("usuario", "equipo").all()

        advertencias = 0
        penalizaciones = 0

        for alquiler in alquileres:
            # Advertencia un día antes
            if (alquiler.fecha_fin - hoy).days == 1:
                service.enviar_advertencia_vencimiento(alquiler.id)
                advertencias += 1

            # Penalización si ya se pasó la fecha de fin
            if hoy > alquiler.fecha_fin:
                creada = service.generar_penalizacion_por_retraso(alquiler.id)
                if creada is not None:
                    penalizaciones += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Notificaciones procesadas. Advertencias: {advertencias}, Penalizaciones creadas: {penalizaciones}."
            )
        )

