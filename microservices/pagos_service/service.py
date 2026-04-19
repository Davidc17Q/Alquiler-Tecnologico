from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from payment_gateway import FakePaymentGateway
from notifications import send_payment_confirmation_email
from sqlite_store import fetch_alquiler_para_pago, fetch_pago, insert_pago_y_marcar_alquiler_pagado

_METODOS = {"TARJETA", "TRANSFERENCIA", "EFECTIVO"}


class ClientError(Exception):
    """Error atribuible al cliente (respuesta HTTP 400)."""


def crear_pago(payload: dict) -> dict:
    try:
        alquiler_id = int(payload.get("alquiler_id"))
    except (TypeError, ValueError):
        raise ClientError("alquiler_id inválido.") from None

    try:
        monto = Decimal(str(payload.get("monto")))
    except (InvalidOperation, TypeError):
        raise ClientError("monto inválido.") from None

    metodo = payload.get("metodo")
    if metodo not in _METODOS:
        raise ClientError("metodo inválido. Use TARJETA, TRANSFERENCIA o EFECTIVO.")

    if monto <= 0:
        raise ClientError("El monto debe ser mayor que cero.")

    alquiler = fetch_alquiler_para_pago(alquiler_id)
    if alquiler is None:
        raise ClientError("Alquiler no encontrado.")

    if alquiler.estado != "PENDIENTE":
        raise ClientError("Solo se pueden pagar alquileres en estado PENDIENTE.")

    gateway = FakePaymentGateway()
    try:
        gateway.charge(
            amount=monto,
            metadata={"alquiler_id": alquiler_id, "metodo": metodo},
        )
    except Exception as exc:  # noqa: BLE001
        raise ClientError(f"Error al procesar el pago: {exc}") from exc

    fecha_pago = datetime.now(timezone.utc).replace(tzinfo=None)
    pago_id = insert_pago_y_marcar_alquiler_pagado(
        alquiler_id=alquiler_id,
        monto=monto,
        metodo=metodo,
        fecha_pago=fecha_pago,
    )

    if alquiler.usuario_email:
        send_payment_confirmation_email(
            to=alquiler.usuario_email,
            usuario_nombre=alquiler.usuario_nombre,
            equipo_nombre=alquiler.equipo_nombre,
            fecha_inicio=str(alquiler.fecha_inicio),
            fecha_fin=str(alquiler.fecha_fin),
            monto=str(monto),
        )

    pago = fetch_pago(pago_id)
    if pago is None:
        raise RuntimeError("No se pudo leer el pago recién creado.")

    fecha_val = pago["fecha_pago"]
    if isinstance(fecha_val, str):
        fecha_iso = fecha_val
    else:
        fecha_iso = fecha_val.isoformat()

    return {
        "id": pago["id"],
        "alquiler_id": pago["alquiler_id"],
        "monto": str(pago["monto"]),
        "metodo": pago["metodo"],
        "estado": pago["estado"],
        "fecha_pago": fecha_iso,
    }
