from __future__ import annotations

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Frontend básico para interactuar con la API.

    Esta vista no contiene lógica de negocio: solo renderiza
    un template que, mediante JavaScript, consume los endpoints
    REST de la capa de presentación (`/api/...`).
    """

    template_name = "presentation/index.html"

