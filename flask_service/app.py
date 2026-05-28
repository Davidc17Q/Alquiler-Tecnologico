"""
Microservicio Flask — Strangler Pattern (catálogo de equipos).

Lee equipos disponibles desde la BD SQLite compartida con el monolito Django.
Nginx enruta /api/equipos/ hacia este servicio.
"""

from __future__ import annotations

from flask import Flask, jsonify

from sqlite_store import list_equipos_disponibles

app = Flask(__name__)


@app.get("/health")
def health() -> tuple[dict, int]:
    return jsonify({"status": "ok", "service": "flask-equipos"}), 200


@app.get("/api/equipos/disponibles")
def equipos_disponibles() -> tuple[list, int]:
    try:
        data = list_equipos_disponibles()
    except Exception as exc:  # noqa: BLE001
        return jsonify({"detail": f"Error al leer catálogo: {exc}"}), 503
    return jsonify(data), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
