from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Iterator


@dataclass(frozen=True, slots=True)
class AlquilerRow:
    id: int
    estado: str
    fecha_inicio: date
    fecha_fin: date
    usuario_nombre: str
    usuario_email: str
    equipo_nombre: str


def _db_path() -> str:
    return os.environ.get("SQLITE_PATH", "db.sqlite3")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_db_path(), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
    finally:
        conn.close()


def fetch_alquiler_para_pago(alquiler_id: int) -> AlquilerRow | None:
    sql = """
        SELECT
            a.id,
            a.estado,
            a.fecha_inicio,
            a.fecha_fin,
            u.nombre AS usuario_nombre,
            u.email AS usuario_email,
            e.nombre AS equipo_nombre
        FROM alquiler a
        INNER JOIN usuario u ON u.id = a.usuario_id
        INNER JOIN equipo e ON e.id = a.equipo_id
        WHERE a.id = ?
    """
    with get_connection() as conn:
        row = conn.execute(sql, (alquiler_id,)).fetchone()
    if row is None:
        return None
    return AlquilerRow(
        id=row["id"],
        estado=row["estado"],
        fecha_inicio=date.fromisoformat(str(row["fecha_inicio"])),
        fecha_fin=date.fromisoformat(str(row["fecha_fin"])),
        usuario_nombre=row["usuario_nombre"],
        usuario_email=row["usuario_email"],
        equipo_nombre=row["equipo_nombre"],
    )


def insert_pago_y_marcar_alquiler_pagado(
    alquiler_id: int,
    monto: Decimal,
    metodo: str,
    fecha_pago: datetime,
) -> int:
    """Inserta el pago confirmado y actualiza el alquiler a PAGADO en una transacción."""
    fecha_sql = fecha_pago.strftime("%Y-%m-%d %H:%M:%S.%f")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO pago (alquiler_id, monto, metodo, estado, fecha_pago)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                alquiler_id,
                str(monto),
                metodo,
                "CONFIRMADO",
                fecha_sql,
            ),
        )
        pago_id = int(cur.lastrowid)
        cur.execute(
            "UPDATE alquiler SET estado = ? WHERE id = ?",
            ("PAGADO", alquiler_id),
        )
        conn.commit()
    return pago_id


def fetch_pago(pago_id: int) -> dict | None:
    sql = """
        SELECT id, alquiler_id, monto, metodo, estado, fecha_pago
        FROM pago
        WHERE id = ?
    """
    with get_connection() as conn:
        row = conn.execute(sql, (pago_id,)).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "alquiler_id": row["alquiler_id"],
        "monto": Decimal(str(row["monto"])),
        "metodo": row["metodo"],
        "estado": row["estado"],
        "fecha_pago": row["fecha_pago"],
    }
