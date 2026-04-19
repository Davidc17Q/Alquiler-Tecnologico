from __future__ import annotations

import logging

from flask import Flask, jsonify, request

from service import ClientError, crear_pago

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.get("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@app.post("/pagos/")
def crear_pago_view() -> tuple[dict, int]:
    if not request.is_json:
        return {"detail": "Se esperaba JSON (Content-Type: application/json)."}, 400
    try:
        data = crear_pago(request.get_json(force=True, silent=False) or {})
        return data, 201
    except ClientError as exc:
        return {"detail": str(exc)}, 400
    except Exception:
        logger.exception("Error interno en crear_pago")
        return {"detail": "Error interno del servicio de pagos."}, 500
