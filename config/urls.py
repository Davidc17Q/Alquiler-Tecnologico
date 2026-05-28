from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("presentation.web.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/", include("presentation.api.urls")),
    # Endpoints del monolito expuestos bajo /api/ (enrutados por Nginx al resto de rutas)
    path("api/", include("presentation.api.gateway_urls")),
]

