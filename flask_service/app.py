"""
Microservicio Flask — Strangler Pattern.

Expone endpoints de consulta de equipos desacoplados del monolito Django.
Nginx enruta /api/equipos/ hacia este servicio.
"""

from __future__ import annotations

from flask import Flask, jsonify

app = Flask(__name__)

# Datos mock de equipos disponibles (catálogo ligero del microservicio).
_EQUIPOS_DISPONIBLES = [
    {
        "id": 1,
        "nombre": "Laptop Gamer",
        "disponible": True,
        "precio_dia": 120000,
    },
    {
        "id": 2,
        "nombre": "Tablet Pro",
        "disponible": True,
        "precio_dia": 45000,
    },
    {
        "id": 3,
        "nombre": "Proyector 4K",
        "disponible": True,
        "precio_dia": 80000,
    },
]


@app.get("/health")
def health() -> tuple[dict, int]:
    """Comprobación de vida para Docker healthcheck y orquestación."""
    return jsonify({"status": "ok"}), 200


@app.get("/api/equipos/disponibles")
def equipos_disponibles() -> tuple[list, int]:
    """Lista equipos disponibles (mock) — ruta consumida vía API Gateway."""
    return jsonify(_EQUIPOS_DISPONIBLES), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
