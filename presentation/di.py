"""
Composition root — cableado de servicios e infraestructura (DIP).
"""

from __future__ import annotations

from django.conf import settings

from application.services.admin_dashboard_service import AdminDashboardService
from application.services.admin_gestion_service import AdminGestionService
from application.services.alquiler_service import AlquilerService
from application.services.auth_service import AuthService
from application.services.cliente_resumen_service import ClienteResumenService
from application.services.currency_conversion_service import CurrencyConversionService
from application.services.equipo_service import EquipoService
from application.services.info_sistema_service import InfoSistemaService
from application.services.usuario_service import UsuarioService
from infrastructure.adapters.currency_adapter import ExchangeRateAdapter
from infrastructure.repositories.django_repositories import (
    DjangoAlquilerRepository,
    DjangoEquipoRepository,
    DjangoPagoRepository,
    DjangoUsuarioRepository,
)


def build_auth_service() -> AuthService:
    return AuthService(usuario_repository=DjangoUsuarioRepository())


def build_cliente_resumen_service() -> ClienteResumenService:
    return ClienteResumenService(alquiler_repository=DjangoAlquilerRepository())


def build_alquiler_service() -> AlquilerService:
    return AlquilerService(
        usuario_repository=DjangoUsuarioRepository(),
        equipo_repository=DjangoEquipoRepository(),
        alquiler_repository=DjangoAlquilerRepository(),
    )


def build_equipo_service() -> EquipoService:
    return EquipoService(equipo_repository=DjangoEquipoRepository())


def build_usuario_service() -> UsuarioService:
    return UsuarioService(usuario_repository=DjangoUsuarioRepository())


def build_info_sistema_service() -> InfoSistemaService:
    return InfoSistemaService(
        equipo_repository=DjangoEquipoRepository(),
        alquiler_repository=DjangoAlquilerRepository(),
    )


def build_currency_conversion_service() -> CurrencyConversionService:
    return CurrencyConversionService(
        currency_service=ExchangeRateAdapter(timeout_seconds=settings.EXCHANGE_RATE_TIMEOUT)
    )


def build_admin_dashboard_service() -> AdminDashboardService:
    return AdminDashboardService(
        usuario_repository=DjangoUsuarioRepository(),
        equipo_repository=DjangoEquipoRepository(),
        alquiler_repository=DjangoAlquilerRepository(),
        pago_repository=DjangoPagoRepository(),
    )


def build_admin_gestion_service() -> AdminGestionService:
    return AdminGestionService(
        usuario_repository=DjangoUsuarioRepository(),
        equipo_repository=DjangoEquipoRepository(),
        alquiler_repository=DjangoAlquilerRepository(),
        pago_repository=DjangoPagoRepository(),
    )
