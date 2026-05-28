"""
Rutas expuestas en el API Gateway bajo el prefijo /api/ (Django).

El microservicio Flask atiende /api/equipos/; estas rutas permanecen
en el monolito según el Strangler Pattern.
"""

from __future__ import annotations

from django.urls import path

from presentation.api.views import (
    CeleryDemoView,
    InfoSistemaView,
    PrecioConversionView,
)

urlpatterns = [
    path("info/", InfoSistemaView.as_view(), name="api-info"),
    path("precio-conversion/", PrecioConversionView.as_view(), name="api-precio-conversion"),
    path("tareas/demo/", CeleryDemoView.as_view(), name="api-celery-demo"),
]
