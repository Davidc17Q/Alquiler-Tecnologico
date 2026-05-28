from __future__ import annotations

from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Frontend básico para interactuar con la API.

    Esta vista no contiene lógica de negocio: solo renderiza
    un template que, mediante JavaScript, consume los endpoints
    REST (`/api/v1/...` en Django y `/api/v2/...` en el microservicio de pagos).
    """

    template_name = "presentation/index.html"
    # El dashboard consume únicamente la API REST; sin lógica de negocio en la vista.

