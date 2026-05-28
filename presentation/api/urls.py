from __future__ import annotations

from django.urls import path

from presentation.api.auth_views import (
    AuthLoginView,
    AuthLogoutView,
    AuthMeView,
    AuthRegistroView,
)
from presentation.api.views import (
    AlquilerCreateView,
    EquipoListView,
    MisAlquileresView,
    UsuarioCreateView,
)

urlpatterns = [
    path("auth/registro/", AuthRegistroView.as_view(), name="auth-registro"),
    path("auth/login/", AuthLoginView.as_view(), name="auth-login"),
    path("auth/logout/", AuthLogoutView.as_view(), name="auth-logout"),
    path("auth/me/", AuthMeView.as_view(), name="auth-me"),
    path("mis-alquileres/", MisAlquileresView.as_view(), name="mis-alquileres"),
    path("usuarios/", UsuarioCreateView.as_view(), name="usuario-create"),
    path("equipos/", EquipoListView.as_view(), name="equipo-list"),
    path("alquileres/", AlquilerCreateView.as_view(), name="alquiler-create"),
]

