from __future__ import annotations

from django.urls import path

from presentation.api.views import (
    AlquilerCreateView,
    EquipoListView,
    UsuarioCreateView,
)

urlpatterns = [
    path("usuarios/", UsuarioCreateView.as_view(), name="usuario-create"),
    path("equipos/", EquipoListView.as_view(), name="equipo-list"),
    path("alquileres/", AlquilerCreateView.as_view(), name="alquiler-create"),
]

