from __future__ import annotations

from django.urls import path

from presentation.api.auth_views import (
    AuthLoginView,
    AuthLogoutView,
    AuthMeView,
    AuthRegistroView,
)
from presentation.api.admin_views import (
    AdminAlquileresView,
    AdminAnalyticsView,
    AdminClienteDetailView,
    AdminClientesView,
    AdminDashboardView,
    AdminEquipoDetailView,
    AdminEquiposView,
    AdminInfraView,
)
from presentation.api.views import (
    AlquilerCreateView,
    EquipoListView,
    MisAlquileresView,
    NotificarPagoView,
    UsuarioCreateView,
)

urlpatterns = [
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("admin/analytics/", AdminAnalyticsView.as_view(), name="admin-analytics"),
    path("admin/clientes/", AdminClientesView.as_view(), name="admin-clientes"),
    path("admin/clientes/<int:usuario_id>/", AdminClienteDetailView.as_view(), name="admin-cliente-detail"),
    path("admin/equipos/", AdminEquiposView.as_view(), name="admin-equipos"),
    path("admin/equipos/<int:equipo_id>/", AdminEquipoDetailView.as_view(), name="admin-equipo-detail"),
    path("admin/alquileres/", AdminAlquileresView.as_view(), name="admin-alquileres"),
    path("admin/infra/", AdminInfraView.as_view(), name="admin-infra"),
    path("auth/registro/", AuthRegistroView.as_view(), name="auth-registro"),
    path("auth/login/", AuthLoginView.as_view(), name="auth-login"),
    path("auth/logout/", AuthLogoutView.as_view(), name="auth-logout"),
    path("auth/me/", AuthMeView.as_view(), name="auth-me"),
    path("mis-alquileres/", MisAlquileresView.as_view(), name="mis-alquileres"),
    path("notificar-pago/", NotificarPagoView.as_view(), name="notificar-pago"),
    path("usuarios/", UsuarioCreateView.as_view(), name="usuario-create"),
    path("equipos/", EquipoListView.as_view(), name="equipo-list"),
    path("alquileres/", AlquilerCreateView.as_view(), name="alquiler-create"),
]

