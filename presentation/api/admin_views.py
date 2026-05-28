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

import os

import redis
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from application.exceptions import ApplicationError
from domain.enums import EquipoEstado
from presentation.api.mappers import (
    alquiler_detalle_to_dict,
    equipo_to_dict,
    pago_to_dict,
    usuario_admin_to_dict,
)
from presentation.api.session_auth import handle_auth_error, requiere_staff
from presentation.di import build_admin_dashboard_service, build_admin_gestion_service


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
        svc = build_admin_dashboard_service()
        metrics = svc.obtener_metricas()
        metrics["sparklines"] = svc.sparklines()
        return Response(metrics)


@method_decorator(csrf_exempt, name="dispatch")
class AdminAnalyticsView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        return Response(build_admin_dashboard_service().obtener_analytics())


@method_decorator(csrf_exempt, name="dispatch")
class AdminClientesView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        q = request.GET.get("q", "")
        gestion = build_admin_gestion_service()
        clientes = gestion.listar_clientes(q)
        data = []
        for u in clientes:
            alquileres = gestion.alquileres_de_cliente(u.id)
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
            usuario = build_admin_gestion_service().actualizar_cliente(
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
                for a in build_admin_gestion_service().alquileres_de_cliente(usuario_id)
            ]
            pagos = [pago_to_dict(p) for p in build_admin_gestion_service().pagos_de_cliente(usuario_id)]
        except ApplicationError as exc:
            return handle_auth_error(exc)
        return Response({"alquileres": alquileres, "pagos": pagos})


@method_decorator(csrf_exempt, name="dispatch")
class AdminEquiposView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        equipos = build_admin_gestion_service().listar_equipos()
        return Response([equipo_to_dict(e) for e in equipos])

    def post(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        try:
            equipo = build_admin_gestion_service().guardar_equipo(
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
        gestion = build_admin_gestion_service()
        try:
            existente = gestion.obtener_equipo(equipo_id)
        except ApplicationError as exc:
            return handle_auth_error(exc)
        try:
            equipo = gestion.guardar_equipo(
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
            build_admin_gestion_service().eliminar_equipo(equipo_id)
        except ApplicationError as exc:
            return handle_auth_error(exc)
        return Response(status=204)


@method_decorator(csrf_exempt, name="dispatch")
class AdminAlquileresView(APIView):
    def get(self, request: HttpRequest) -> Response:
        if err := _staff_guard(request):
            return err
        data = [alquiler_detalle_to_dict(a) for a in build_admin_gestion_service().listar_alquileres()]
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
            ("flask", "Flask Equipos MS", f"{base}/api/equipos/disponibles", "purple"),
            ("nginx", "Nginx Gateway", f"{base}/", "blue"),
            ("pagos", "Pagos MS", f"{base}/api/v2/health", "amber"),
        ]:
            estado, latencia = _probe(url)
            services.append(
                {
                    "id": sid,
                    "nombre": name,
                    "estado": estado,
                    "latencia_ms": latencia,
                    "metricas_simuladas": True,
                    "cpu_pct": random.randint(18, 65),
                    "memoria_pct": random.randint(32, 78),
                    "color": color,
                    "logs": [
                        f"[{estado}] GET {url}",
                        f"latency={latencia}ms (real)",
                    ],
                }
            )

        redis_estado, redis_ms = "OFFLINE", 0
        try:
            r = redis.from_url(os.environ.get("REDIS_URL", settings.CELERY_BROKER_URL))
            r.ping()
            redis_estado, redis_ms = "ONLINE", 5
        except Exception as exc:
            redis_estado = "OFFLINE"
            redis_log = str(exc)
        else:
            redis_log = "PONG"

        celery_estado = "DEGRADED"
        celery_log = "Sin workers activos detectados"
        try:
            from config.celery import app as celery_app

            insp = celery_app.control.inspect(timeout=1.0)
            activos = insp.active() if insp else None
            if activos:
                celery_estado = "ONLINE"
                celery_log = f"Workers: {', '.join(activos.keys())}"
        except Exception as exc:
            celery_log = str(exc)

        for sid, name, estado, latencia, color, log in [
            ("redis", "Redis Broker", redis_estado, redis_ms, "rose", redis_log),
            ("celery", "Celery Worker", celery_estado, 12, "emerald", celery_log),
        ]:
            services.append(
                {
                    "id": sid,
                    "nombre": name,
                    "estado": estado,
                    "latencia_ms": latencia,
                    "metricas_simuladas": sid == "celery" and celery_estado != "ONLINE",
                    "cpu_pct": random.randint(10, 40) if sid == "celery" else 25,
                    "memoria_pct": random.randint(20, 55) if sid == "redis" else 40,
                    "color": color,
                    "logs": [f"[{estado}] {log}"],
                }
            )

        online = sum(1 for s in services if s["estado"] == "ONLINE")
        return Response(
            {
                "servicios": services,
                "online": online,
                "total": len(services),
                "nota": "CPU/RAM son métricas simuladas para visualización; latencia y estado HTTP son reales.",
            }
        )
