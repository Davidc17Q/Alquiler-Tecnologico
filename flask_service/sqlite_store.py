"""Acceso SQLite compartido — catálogo de equipos (Strangler Pattern)."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator


def _db_path() -> str:
    return os.environ.get("SQLITE_PATH", "/data/db.sqlite3")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_db_path(), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
    finally:
        conn.close()


def list_equipos_disponibles() -> list[dict]:
    sql = """
        SELECT id, nombre, categoria, precio_por_dia, estado
        FROM equipo
        WHERE estado = 'DISPONIBLE'
        ORDER BY categoria, nombre
    """
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [
        {
            "id": row["id"],
            "nombre": row["nombre"],
            "categoria": row["categoria"],
            "precio_por_dia": str(row["precio_por_dia"]),
            "estado": row["estado"],
            "disponible": True,
            "fuente": "flask-ms",
        }
        for row in rows
    ]
