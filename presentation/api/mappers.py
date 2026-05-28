from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from domain.entities.alquiler import Alquiler
from domain.entities.equipo import Equipo
from domain.entities.pago import Pago
from domain.entities.usuario import Usuario


def usuario_to_dict(usuario: Usuario) -> Dict[str, Any]:
    """Mapea la entidad de dominio Usuario a un DTO plano."""
    data = asdict(usuario)
    data["fecha_registro"] = usuario.fecha_registro.isoformat()
    data["rol"] = usuario.rol.value
    data["activo"] = usuario.activo
    return data


def usuario_admin_to_dict(
    usuario: Usuario,
    *,
    total_alquileres: int = 0,
    ultimo_alquiler: str | None = None,
) -> Dict[str, Any]:
    data = usuario_to_dict(usuario)
    data["total_alquileres"] = total_alquileres
    data["ultimo_alquiler"] = ultimo_alquiler
    return data


def equipo_to_dict(equipo: Equipo) -> Dict[str, Any]:
    """Mapea la entidad de dominio Equipo a un DTO plano."""
    return {
        "id": equipo.id,
        "nombre": equipo.nombre,
        "categoria": equipo.categoria,
        "precio_por_dia": str(equipo.precio_por_dia),
        "estado": equipo.estado.value,
    }


def alquiler_to_dict(alquiler: Alquiler) -> Dict[str, Any]:
    """Mapea la entidad de dominio Alquiler a un DTO plano."""
    return {
        "id": alquiler.id,
        "usuario_id": alquiler.usuario.id,
        "equipo_id": alquiler.equipo.id,
        "fecha_inicio": alquiler.fecha_inicio,
        "fecha_fin": alquiler.fecha_fin,
        "estado": alquiler.estado.value,
        "costo_total": str(alquiler.costo_total),
    }


def alquiler_detalle_to_dict(alquiler: Alquiler) -> Dict[str, Any]:
    """DTO enriquecido para el panel del cliente."""
    data = alquiler_to_dict(alquiler)
    data["equipo_nombre"] = alquiler.equipo.nombre
    data["equipo_categoria"] = alquiler.equipo.categoria
    data["usuario_nombre"] = alquiler.usuario.nombre
    return data


def pago_to_dict(pago: Pago) -> Dict[str, Any]:
    """Mapea la entidad de dominio Pago a un DTO plano."""
    return {
        "id": pago.id,
        "alquiler_id": pago.alquiler.id,
        "monto": pago.monto,
        "metodo": pago.metodo.value,
        "estado": pago.estado.value,
        "fecha_pago": pago.fecha_pago,
    }

