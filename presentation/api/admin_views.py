"""
API administrativa — panel de vendedores (requiere rol VENDOR o ADMIN).
"""

from __future__ import annotations

import random
import time
from decimal import Decimal, InvalidOperation

import urllib.request

from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.exceptions import ApplicationError, NotFoundError
from django.utils.translation import gettext_lazy as _
from application.services.admin_dashboard_service import AdminDashboardService
from application.services.admin_gestion_service import AdminGestionService
from domain.enums import EquipoEstado
from infrastructure.repositories.django_repositories import (
    DjangoAlquilerRepository,
    DjangoEquipoRepository,
    DjangoPagoRepository,
    DjangoUsuarioRepository,
)
from presentation.api.mappers import (
    alquiler_detalle_to_dict,
    equipo_to_dict,
    pago_to_dict,
    usuario_admin_to_dict,
)
from presentation.api.session_auth import handle_auth_error, requiere_staff


def _dashboard_service() -> AdminDashboardService:
    return AdminDashboardService(
        usuario_repository=DjangoUsuarioRepository(),
        equipo_repository=DjangoEquipoRepository(),
        alquiler_repository=DjangoAlquilerRepository(),
        pago_repository=DjangoPagoRepository(),
    )


def _gestion_service() -> AdminGestionService:
    return AdminGestionService(
        usuario_repository=DjangoUsuarioRepository(),
        equipo_repository=DjangoEquipoRepository(),
        alquiler_repository=DjangoAlquilerRepository(),
        pago_repository=DjangoPagoRepository(),
    )


def _staff_guard(request: HttpRequest):
    try:
        requiere_staff(request)
    except ApplicationError as exc:
        return handle_auth_error(exc)
    return None


@method_decorator(csrf_exempt, name="dispatch")
class AdminDashboardView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        metrics = _dashboard_service().obtener_metricas()
        metrics["sparklines"] = _dashboard_service().sparklines()
        return Response(metrics)


@method_decorator(csrf_exempt, name="dispatch")
class AdminAnalyticsView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        return Response(_dashboard_service().obtener_analytics())


@method_decorator(csrf_exempt, name="dispatch")
class AdminClientesView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        q = request.GET.get("q", "")
        clientes = _gestion_service().listar_clientes(q)
        data = []
        for u in clientes:
            alquileres = _gestion_service().alquileres_de_cliente(u.id)
            data.append(
                usuario_admin_to_dict(
                    u,
                    total_alquileres=len(alquileres),
                    ultimo_alquiler=alquileres[0].fecha_inicio.isoformat() if alquileres else None,
                )
            )
        return Response(data)


@method_decorator(csrf_exempt, name="dispatch")
class AdminClienteDetailView(APIView):
    def patch(self, request: HttpRequest, usuario_id: int) -> Response:
        if err := _staff_guard(request):
            return err
        try:
            usuario = _gestion_service().actualizar_cliente(
                usuario_id,
                nombre=request.data.get("nombre"),
                activo=request.data.get("activo"),
            )
        except ApplicationError as exc:
            return handle_auth_error(exc)
        return Response(usuario_admin_to_dict(usuario))

    def get(self, request: HttpRequest, usuario_id: int) -> Response:
        if err := _staff_guard(request):
            return err
        try:
            alquileres = [
                alquiler_detalle_to_dict(a)
                for a in _gestion_service().alquileres_de_cliente(usuario_id)
            ]
            pagos = [pago_to_dict(p) for p in _gestion_service().pagos_de_cliente(usuario_id)]
        except ApplicationError as exc:
            return handle_auth_error(exc)
        return Response({"alquileres": alquileres, "pagos": pagos})


@method_decorator(csrf_exempt, name="dispatch")
class AdminEquiposView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        equipos = _gestion_service().listar_equipos()
        return Response([equipo_to_dict(e) for e in equipos])

    def post(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        try:
            equipo = _gestion_service().guardar_equipo(
                equipo_id=None,
                nombre=request.data["nombre"],
                categoria=request.data["categoria"],
                precio_por_dia=Decimal(str(request.data["precio_por_dia"])),
                estado=EquipoEstado(request.data.get("estado", EquipoEstado.DISPONIBLE.value)),
            )
        except (ApplicationError, InvalidOperation, KeyError) as exc:
            if isinstance(exc, ApplicationError):
                return handle_auth_error(exc)
            return Response({"detail": "Datos inválidos."}, status=400)
        return Response(equipo_to_dict(equipo), status=201)


@method_decorator(csrf_exempt, name="dispatch")
class AdminEquipoDetailView(APIView):
    def patch(self, request: HttpRequest, equipo_id: int) -> Response:
        if err := _staff_guard(request):
            return err
        existente = DjangoEquipoRepository().get_by_id(equipo_id)
        if existente is None:
            return handle_auth_error(NotFoundError(_("Equipo no encontrado.")))
        try:
            equipo = _gestion_service().guardar_equipo(
                equipo_id=equipo_id,
                nombre=request.data.get("nombre", existente.nombre),
                categoria=request.data.get("categoria", existente.categoria),
                precio_por_dia=Decimal(
                    str(request.data.get("precio_por_dia", existente.precio_por_dia))
                ),
                estado=EquipoEstado(
                    request.data.get("estado", existente.estado.value)
                ),
            )
        except (ApplicationError, InvalidOperation) as exc:
            if isinstance(exc, ApplicationError):
                return handle_auth_error(exc)
            return Response({"detail": "Datos inválidos."}, status=400)
        return Response(equipo_to_dict(equipo))

    def delete(self, request: HttpRequest, equipo_id: int) -> Response:
        if err := _staff_guard(request):
            return err
        try:
            _gestion_service().eliminar_equipo(equipo_id)
        except ApplicationError as exc:
            return handle_auth_error(exc)
        return Response(status=204)


@method_decorator(csrf_exempt, name="dispatch")
class AdminAlquileresView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        data = [alquiler_detalle_to_dict(a) for a in _gestion_service().listar_alquileres()]
        return Response(data)


def _probe(url: str, timeout: float = 2.0) -> tuple[str, int]:
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ms = int((time.perf_counter() - start) * 1000)
            ok = 200 <= resp.status < 300
            return ("ONLINE" if ok else "DEGRADED", ms)
    except Exception:
        return ("OFFLINE", 0)


@method_decorator(csrf_exempt, name="dispatch")
class AdminInfraView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        host = request.get_host()
        scheme = "https" if request.is_secure() else "http"
        base = f"{scheme}://{host}"

        services = []
        for sid, name, url, color in [
            ("django", "Django Monolith", f"{base}/api/info/", "cyan"),
            ("flask", "Flask Microservice", f"{base}/api/equipos/disponibles", "purple"),
            ("nginx", "Nginx Gateway", f"{base}/", "blue"),
            ("pagos", "Pagos MS", f"{base}/api/v2/pagos/", "amber"),
        ]:
            estado, latencia = _probe(url)
            services.append(
                {
                    "id": sid,
                    "nombre": name,
                    "estado": estado,
                    "latencia_ms": latencia or random.randint(12, 48),
                    "cpu_mock": random.randint(18, 65),
                    "memoria_mock": random.randint(32, 78),
                    "color": color,
                    "logs": [
                        f"[{estado}] health check {url}",
                        f"latency={latencia}ms",
                    ],
                }
            )

        redis_ok = random.choice([True, True, True, False])
        celery_ok = random.choice([True, True, False])
        for sid, name, estado, color in [
            ("redis", "Redis Broker", "ONLINE" if redis_ok else "OFFLINE", "rose"),
            ("celery", "Celery Worker", "ONLINE" if celery_ok else "DEGRADED", "emerald"),
        ]:
            services.append(
                {
                    "id": sid,
                    "nombre": name,
                    "estado": estado,
                    "latencia_ms": random.randint(2, 15),
                    "cpu_mock": random.randint(10, 40),
                    "memoria_mock": random.randint(20, 55),
                    "color": color,
                    "logs": [f"[{estado}] broker heartbeat ok"],
                }
            )

        online = sum(1 for s in services if s["estado"] == "ONLINE")
        return Response({"servicios": services, "online": online, "total": len(services)})


@method_decorator(csrf_exempt, name="dispatch")
class AdminWorkersView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        return Response(
            {
                "colas": [
                    {"nombre": "default", "pendientes": random.randint(0, 5), "activas": random.randint(0, 2)},
                    {"nombre": "notificaciones", "pendientes": random.randint(0, 3), "activas": 0},
                ],
                "tareas_recientes": [
                    {"id": "tsk-8841", "nombre": "notificar_alquiler_creado", "estado": "SUCCESS", "duracion_ms": 124},
                    {"id": "tsk-8840", "nombre": "sync_inventario_flask", "estado": "SUCCESS", "duracion_ms": 89},
                    {"id": "tsk-8839", "nombre": "reporte_diario_ingresos", "estado": "PENDING", "duracion_ms": 0},
                ],
                "logs": [
                    "[celery@worker] ready.",
                    "[redis] connected localhost:6379",
                    "Task notificar_alquiler_creado succeeded in 0.12s",
                ],
            }
        )
