from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from application.exceptions import ConflictError, NotFoundError, PaymentError
from application.interfaces.payment_gateway import PaymentGateway
from application.interfaces.notification_gateway import NotificationGateway
from application.interfaces.repositories import AlquilerRepository, PagoRepository
from domain.entities.pago import Pago
from domain.enums import AlquilerEstado, MetodoPago, PagoEstado


class PagoService:
    """Service Layer para pagos.

    Este servicio depende de la abstracción `PaymentGateway` en
    lugar de una implementación concreta. La Factory en la capa
    de infraestructura decide qué implementación instanciar según
    configuración, lo que demuestra el uso del patrón Factory y
    el cumplimiento de DIP.
    """

    def __init__(
        self,
        pago_repository: PagoRepository,
        alquiler_repository: AlquilerRepository,
        payment_gateway: PaymentGateway,
        notification_gateway: NotificationGateway | None = None,
    ) -> None:
        self._pagos = pago_repository
        self._alquileres = alquiler_repository
        self._payment_gateway = payment_gateway
        self._notification_gateway = notification_gateway

    def crear_pago(
        self,
        alquiler_id: int,
        monto: Decimal,
        metodo: MetodoPago,
    ) -> Pago:
        alquiler = self._alquileres.get_by_id(alquiler_id)
        if alquiler is None:
            raise NotFoundError("Alquiler no encontrado.")

        if alquiler.estado != AlquilerEstado.PENDIENTE:
            raise ConflictError("Solo se pueden pagar alquileres en estado PENDIENTE.")

        try:
            transaction_id = self._payment_gateway.charge(
                amount=monto,
                metadata={"alquiler_id": alquiler_id, "metodo": metodo.value},
            )
        except Exception as exc:  # noqa: BLE001
            raise PaymentError(f"Error al procesar el pago: {exc}") from exc

        pago = Pago(
            id=None,
            alquiler=alquiler,
            monto=monto,
            metodo=metodo,
            estado=PagoEstado.CONFIRMADO,
            fecha_pago=datetime.now(timezone.utc),
        )

        pago_creado = self._pagos.create(pago)

        # El pago confirma el alquiler: cambiamos estado a PAGADO
        alquiler.estado = AlquilerEstado.PAGADO
        self._alquileres.save(alquiler)

        # Enviamos notificación de confirmación si hay pasarela configurada.
        if self._notification_gateway and alquiler.usuario.email:
            subject = "Confirmación de pago de alquiler - TechRent"
            body = (
                f"Hola {alquiler.usuario.nombre},\n\n"
                f"Tu pago por el alquiler del equipo '{alquiler.equipo.nombre}' "
                f"ha sido confirmado.\n"
                f"Fechas: {alquiler.fecha_inicio} al {alquiler.fecha_fin}\n"
                f"Monto pagado: {monto}\n\n"
                "Gracias por utilizar TechRent."
            )
            self._notification_gateway.send_email(
                to=alquiler.usuario.email,
                subject=subject,
                body=body,
            )

        # Podríamos guardar el transaction_id en una entidad ampliada
        # o en una tabla de auditoría, pero para esta versión basta
        # con devolver el pago confirmado.
        return pago_creado

