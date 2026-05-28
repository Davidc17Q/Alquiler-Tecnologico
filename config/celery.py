"""
Configuración Celery — broker Redis y autodiscovery de tareas.

Se importa desde config/__init__.py para que Django cargue la app Celery
al arrancar (patrón recomendado en despliegues con workers).
"""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("alquiler_tecnologico")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
