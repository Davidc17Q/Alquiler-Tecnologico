from __future__ import annotations

from django.db import models

from domain.enums import AlquilerEstado, EquipoEstado, MetodoPago, PagoEstado, RolUsuario


class UsuarioModel(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    fecha_registro = models.DateTimeField()
    rol = models.CharField(
        max_length=20,
        choices=[(r.value, r.value) for r in RolUsuario],
        default=RolUsuario.CLIENTE.value,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "usuario"

    def __str__(self) -> str:
        return f"{self.nombre} <{self.email}>"


class EquipoModel(models.Model):
    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=100)
    precio_por_dia = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=[(e.value, e.value) for e in EquipoEstado],
        default=EquipoEstado.DISPONIBLE.value,
    )

    class Meta:
        db_table = "equipo"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.categoria})"


class AlquilerModel(models.Model):
    usuario = models.ForeignKey(UsuarioModel, on_delete=models.CASCADE, related_name="alquileres")
    equipo = models.ForeignKey(EquipoModel, on_delete=models.CASCADE, related_name="alquileres")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=[(e.value, e.value) for e in AlquilerEstado],
        default=AlquilerEstado.PENDIENTE.value,
    )
    costo_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "alquiler"

    def __str__(self) -> str:
        return f"Alquiler #{self.pk} - {self.usuario} -> {self.equipo}"


class PagoModel(models.Model):
    alquiler = models.ForeignKey(AlquilerModel, on_delete=models.CASCADE, related_name="pagos")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo = models.CharField(
        max_length=20,
        choices=[(m.value, m.value) for m in MetodoPago],
    )
    estado = models.CharField(
        max_length=20,
        choices=[(e.value, e.value) for e in PagoEstado],
        default=PagoEstado.PENDIENTE.value,
    )
    fecha_pago = models.DateTimeField()

    class Meta:
        db_table = "pago"

    def __str__(self) -> str:
        return f"Pago #{self.pk} - {self.monto} ({self.metodo})"


class PenalizacionModel(models.Model):
    """Modelo base para penalizaciones.

    Se mantiene simple para reflejar que el dominio aún
    no explota todas las reglas alrededor de penalizaciones.
    """

    alquiler = models.ForeignKey(AlquilerModel, on_delete=models.CASCADE, related_name="penalizaciones")
    motivo = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "penalizacion"

    def __str__(self) -> str:
        return f"Penalización #{self.pk} - {self.motivo}"

