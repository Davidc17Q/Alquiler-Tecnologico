"""Tests unitarios — capa de aplicación."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from application.exceptions import ValidationError
from application.services.alquiler_service import AlquilerService
from domain.entities.equipo import Equipo
from domain.entities.usuario import Usuario
from domain.enums import EquipoEstado, RolUsuario


@pytest.fixture
def alquiler_service():
    usuarios = MagicMock()
    equipos = MagicMock()
    alquileres = MagicMock()
    usuarios.get_by_id.return_value = Usuario(
        id=1,
        nombre="Test",
        email="t@test.com",
        fecha_registro=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        rol=RolUsuario.CLIENTE,
        activo=True,
    )
    equipos.get_by_id.return_value = Equipo(
        id=1,
        nombre="Laptop",
        categoria="Laptop",
        precio_por_dia=Decimal("100"),
        estado=EquipoEstado.DISPONIBLE,
    )
    alquileres.exists_overlapping_for_equipo.return_value = False
    alquileres.create.side_effect = lambda a: a
    return AlquilerService(usuarios, equipos, alquileres)


def test_crear_alquiler_fechas_invalidas(alquiler_service):
    with pytest.raises(ValidationError):
        alquiler_service.crear_alquiler(
            usuario_id=1,
            equipo_id=1,
            fecha_inicio=date(2026, 6, 10),
            fecha_fin=date(2026, 6, 5),
        )


def test_crear_alquiler_ok(alquiler_service):
    alquiler = alquiler_service.crear_alquiler(
        usuario_id=1,
        equipo_id=1,
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 5),
    )
    assert alquiler.costo_total == Decimal("400")
