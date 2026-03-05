from __future__ import annotations

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-techrent-placeholder-key"

DEBUG = True

ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    # Capa de infraestructura (modelos y repositorios)
    "infrastructure.apps.InfrastructureConfig",
    # Capa de presentación (API)
    "presentation.apps.PresentationConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Se incluye explícitamente el directorio de templates del proyecto
        # además de los templates de cada app (APP_DIRS=True).
        "DIRS": [
            BASE_DIR / "presentation" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = []

LANGUAGE_CODE = "es-es"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Configuración de pasarela de pagos
# ---------------------------------------------------------------------------
# Este flag permite seleccionar dinámicamente la implementación de pasarela
# de pagos concreta sin acoplar la capa de aplicación a detalles de
# infraestructura. La Factory leerá este valor para decidir qué instancia
# concreta construir. Esto ilustra el Principio de Inversión de Dependencias.
PAYMENT_GATEWAY_BACKEND = os.getenv("PAYMENT_GATEWAY_BACKEND", "fake")

# ---------------------------------------------------------------------------
# Configuración de notificaciones (email real)
# ---------------------------------------------------------------------------
# Para enviar correos reales configuramos el backend SMTP estándar de Django.
# Las credenciales se leen desde variables de entorno para no acoplar
# el código a datos sensibles.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@techrent.local")

# La pasarela de notificaciones usará email por defecto.
NOTIFICATION_GATEWAY_BACKEND = os.getenv("NOTIFICATION_GATEWAY_BACKEND", "email")

