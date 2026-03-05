from __future__ import annotations

from django.core.management.base import BaseCommand

from infrastructure.models import EquipoModel, EquipoEstado


class Command(BaseCommand):
    help = "Crea datos de ejemplo para TechRent (equipos tecnológicos)."

    def handle(self, *args, **options) -> None:
        if EquipoModel.objects.exists():
            self.stdout.write(self.style.WARNING("Ya existen equipos en la base de datos. No se crearán duplicados."))
            return

        equipos = [
            {
                "nombre": "MacBook Pro 16\"",
                "categoria": "Laptop",
                "precio_por_dia": 80.00,
                "estado": EquipoEstado.DISPONIBLE.value,
            },
            {
                "nombre": "Dell XPS 13",
                "categoria": "Laptop",
                "precio_por_dia": 60.00,
                "estado": EquipoEstado.DISPONIBLE.value,
            },
            {
                "nombre": "iPad Pro 12.9\"",
                "categoria": "Tablet",
                "precio_por_dia": 40.00,
                "estado": EquipoEstado.DISPONIBLE.value,
            },
            {
                "nombre": "Canon EOS R5",
                "categoria": "Cámara",
                "precio_por_dia": 90.00,
                "estado": EquipoEstado.DISPONIBLE.value,
            },
            {
                "nombre": "Sony A7 IV",
                "categoria": "Cámara",
                "precio_por_dia": 85.00,
                "estado": EquipoEstado.DISPONIBLE.value,
            },
        ]

        for data in equipos:
            EquipoModel.objects.create(**data)

        self.stdout.write(self.style.SUCCESS(f"Se crearon {len(equipos)} equipos de ejemplo para TechRent."))

