from __future__ import annotations

from rest_framework import serializers

from domain.enums import MetodoPago


class UsuarioCreateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150)
    email = serializers.EmailField()


class EquipoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField()
    categoria = serializers.CharField()
    precio_por_dia = serializers.DecimalField(max_digits=10, decimal_places=2)
    estado = serializers.CharField()


class AlquilerCreateSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField()
    equipo_id = serializers.IntegerField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()


class PagoCreateSerializer(serializers.Serializer):
    alquiler_id = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    metodo = serializers.ChoiceField(choices=[(m.value, m.value) for m in MetodoPago])


class AlquilerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    usuario_id = serializers.IntegerField()
    equipo_id = serializers.IntegerField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    estado = serializers.CharField()
    costo_total = serializers.DecimalField(max_digits=12, decimal_places=2)


class PagoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    alquiler_id = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    metodo = serializers.CharField()
    estado = serializers.CharField()
    fecha_pago = serializers.DateTimeField()

