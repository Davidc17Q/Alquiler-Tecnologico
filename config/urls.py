from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("presentation.web.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("presentation.api.urls")),
]

