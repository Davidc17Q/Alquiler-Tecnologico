"""Paquete de configuración principal de Django para Alquiler Tecnológico."""

from config.celery import app as celery_app

__all__ = ("celery_app",)
