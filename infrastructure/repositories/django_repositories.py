from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from application.interfaces.repositories import (
    AlquilerRepository,
    EquipoRepository,
    PagoRepository,
    PenalizacionRepository,
    UsuarioRepository,
)
from domain.entities.alquiler import Alquiler
from domain.entities.equipo import Equipo
from domain.entities.pago import Pago
from domain.entities.penalizacion import Penalizacion
from domain.entities.usuario import Usuario
from domain.enums import AlquilerEstado, EquipoEstado, MetodoPago, PagoEstado, RolUsuario
from infrastructure.models import (
    AlquilerModel,
    EquipoModel,
    PagoModel,
    PenalizacionModel,
    UsuarioModel,
)


def _map_usuario_model_to_entity(model: UsuarioModel) -> Usuario:
    return Usuario(
        id=model.pk,
        nombre=model.nombre,
        email=model.email,
        fecha_registro=model.fecha_registro,
        rol=RolUsuario(model.rol),
        activo=model.activo,
    )


def _map_equipo_model_to_entity(model: EquipoModel) -> Equipo:
    return Equipo(
        id=model.pk,
        nombre=model.nombre,
        categoria=model.categoria,
        precio_por_dia=model.precio_por_dia,
        estado=EquipoEstado(model.estado),
    )


def _map_alquiler_model_to_entity(model: AlquilerModel) -> Alquiler:
    return Alquiler(
        id=model.pk,
        usuario=_map_usuario_model_to_entity(model.usuario),
        equipo=_map_equipo_model_to_entity(model.equipo),
        fecha_inicio=model.fecha_inicio,
        fecha_fin=model.fecha_fin,
        estado=AlquilerEstado(model.estado),
        costo_total=model.costo_total,
    )


def _map_pago_model_to_entity(model: PagoModel, alquiler_entity: Alquiler | None = None) -> Pago:
    alquiler = alquiler_entity or _map_alquiler_model_to_entity(model.alquiler)
    return Pago(
        id=model.pk,
        alquiler=alquiler,
        monto=model.monto,
        metodo=MetodoPago(model.metodo),
        estado=PagoEstado(model.estado),
        fecha_pago=model.fecha_pago,
    )


def _map_penalizacion_model_to_entity(model: PenalizacionModel, alquiler_entity: Alquiler | None = None) -> Penalizacion:
    alquiler = alquiler_entity or _map_alquiler_model_to_entity(model.alquiler)
    return Penalizacion(
        id=model.pk,
        alquiler=alquiler,
        motivo=model.motivo,
        monto=model.monto,
    )


class DjangoUsuarioRepository(UsuarioRepository):
    def get_by_id(self, usuario_id: int) -> Usuario | None:
        try:
            model = UsuarioModel.objects.get(pk=usuario_id)
        except UsuarioModel.DoesNotExist:
            return None
        return _map_usuario_model_to_entity(model)

    def create(self, usuario: Usuario, password_hash: str = "") -> Usuario:
        model = UsuarioModel.objects.create(
            nombre=usuario.nombre,
            email=usuario.email,
            fecha_registro=usuario.fecha_registro,
            rol=usuario.rol.value,
            activo=usuario.activo,
            password=password_hash,
        )
        return _map_usuario_model_to_entity(model)

    def get_password_hash(self, usuario_id: int) -> str:
        return UsuarioModel.objects.values_list("password", flat=True).get(pk=usuario_id)

    def update_password_hash(self, usuario_id: int, password_hash: str) -> None:
        UsuarioModel.objects.filter(pk=usuario_id).update(password=password_hash)

    def list_all(self):
        return [_map_usuario_model_to_entity(m) for m in UsuarioModel.objects.order_by("-fecha_registro")]

    def save(self, usuario: Usuario) -> Usuario:
        model = UsuarioModel.objects.get(pk=usuario.id)
        model.nombre = usuario.nombre
        model.email = usuario.email
        model.rol = usuario.rol.value
        model.activo = usuario.activo
        model.save(update_fields=["nombre", "email", "rol", "activo"])
        return _map_usuario_model_to_entity(model)

    def count_all(self) -> int:
        return UsuarioModel.objects.count()

    def count_clientes_activos(self) -> int:
        desde = timezone.now() - timedelta(days=90)
        return (
            UsuarioModel.objects.filter(rol=RolUsuario.CLIENTE.value)
            .filter(alquileres__fecha_inicio__gte=desde.date())
            .distinct()
            .count()
        )

    def get_by_email(self, email: str) -> Usuario | None:
        try:
            model = UsuarioModel.objects.get(email__iexact=email.strip())
        except UsuarioModel.DoesNotExist:
            return None
        return _map_usuario_model_to_entity(model)

    def exists_by_email(self, email: str) -> bool:
        return UsuarioModel.objects.filter(email__iexact=email.strip()).exists()


class DjangoEquipoRepository(EquipoRepository):
    def get_by_id(self, equipo_id: int) -> Equipo | None:
        try:
            model = EquipoModel.objects.get(pk=equipo_id)
        except EquipoModel.DoesNotExist:
            return None
        return _map_equipo_model_to_entity(model)

    def list_all(self):
        return [_map_equipo_model_to_entity(e) for e in EquipoModel.objects.all()]

    def count_all(self) -> int:
        return EquipoModel.objects.count()

    def save(self, equipo: Equipo) -> Equipo:
        if equipo.id:
            model = EquipoModel.objects.get(pk=equipo.id)
            model.nombre = equipo.nombre
            model.categoria = equipo.categoria
            model.precio_por_dia = equipo.precio_por_dia
            model.estado = equipo.estado.value
            model.save(update_fields=["nombre", "categoria", "precio_por_dia", "estado"])
        else:
            model = EquipoModel.objects.create(
                nombre=equipo.nombre,
                categoria=equipo.categoria,
                precio_por_dia=equipo.precio_por_dia,
                estado=equipo.estado.value,
            )
        return _map_equipo_model_to_entity(model)

    def delete_by_id(self, equipo_id: int) -> None:
        EquipoModel.objects.filter(pk=equipo_id).delete()

    def count_alquilados_ahora(self) -> int:
        estados = [AlquilerEstado.PENDIENTE.value, AlquilerEstado.PAGADO.value]
        return (
            AlquilerModel.objects.filter(estado__in=estados)
            .values("equipo_id")
            .distinct()
            .count()
        )


class DjangoAlquilerRepository(AlquilerRepository):
    def get_by_id(self, alquiler_id: int) -> Alquiler | None:
        try:
            model = AlquilerModel.objects.select_related("usuario", "equipo").get(pk=alquiler_id)
        except AlquilerModel.DoesNotExist:
            return None
        return _map_alquiler_model_to_entity(model)

    def create(self, alquiler: Alquiler) -> Alquiler:
        usuario_model = UsuarioModel.objects.get(pk=alquiler.usuario.id)
        equipo_model = EquipoModel.objects.get(pk=alquiler.equipo.id)
        model = AlquilerModel.objects.create(
            usuario=usuario_model,
            equipo=equipo_model,
            fecha_inicio=alquiler.fecha_inicio,
            fecha_fin=alquiler.fecha_fin,
            estado=alquiler.estado.value,
            costo_total=alquiler.costo_total,
        )
        return _map_alquiler_model_to_entity(model)

    def save(self, alquiler: Alquiler) -> Alquiler:
        model = AlquilerModel.objects.get(pk=alquiler.id)
        model.estado = alquiler.estado.value
        model.costo_total = alquiler.costo_total
        model.save(update_fields=["estado", "costo_total"])
        return _map_alquiler_model_to_entity(model)

    def exists_overlapping_for_equipo(
        self,
        equipo_id: int,
        fecha_inicio: date,
        fecha_fin: date,
    ) -> bool:
        return AlquilerModel.objects.filter(
            equipo_id=equipo_id,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).exists()

    def count_activos(self) -> int:
        estados_activos = [AlquilerEstado.PENDIENTE.value, AlquilerEstado.PAGADO.value]
        return AlquilerModel.objects.filter(estado__in=estados_activos).count()

    def list_by_usuario_id(self, usuario_id: int):
        qs = (
            AlquilerModel.objects.filter(usuario_id=usuario_id)
            .select_related("usuario", "equipo")
            .order_by("-fecha_inicio", "-id")
        )
        return [_map_alquiler_model_to_entity(m) for m in qs]

    def list_all(self):
        qs = AlquilerModel.objects.select_related("usuario", "equipo").order_by("-fecha_inicio", "-id")
        return [_map_alquiler_model_to_entity(m) for m in qs]

    def count_pendientes(self) -> int:
        return AlquilerModel.objects.filter(estado=AlquilerEstado.PENDIENTE.value).count()

    def ingresos_por_mes(self, meses: int = 6):
        desde = timezone.now() - timedelta(days=meses * 31)
        qs = (
            PagoModel.objects.filter(
                estado="CONFIRMADO",
                fecha_pago__gte=desde,
            )
            .annotate(mes=TruncMonth("fecha_pago"))
            .values("mes")
            .annotate(total=Sum("monto"))
            .order_by("mes")
        )
        return [{"mes": row["mes"].strftime("%Y-%m"), "total": float(row["total"] or 0)} for row in qs]

    def alquileres_por_categoria(self):
        qs = (
            AlquilerModel.objects.values("equipo__categoria")
            .annotate(total=Count("id"))
            .order_by("-total")[:12]
        )
        return [{"categoria": row["equipo__categoria"], "total": row["total"]} for row in qs]

    def equipos_mas_alquilados(self, limite: int = 8):
        qs = (
            AlquilerModel.objects.values("equipo__id", "equipo__nombre", "equipo__categoria")
            .annotate(total=Count("id"))
            .order_by("-total")[:limite]
        )
        return [
            {
                "equipo_id": row["equipo__id"],
                "nombre": row["equipo__nombre"],
                "categoria": row["equipo__categoria"],
                "total": row["total"],
            }
            for row in qs
        ]

    def actividad_usuarios_por_mes(self, meses: int = 6):
        desde = timezone.now() - timedelta(days=meses * 31)
        qs = (
            AlquilerModel.objects.filter(fecha_inicio__gte=desde.date())
            .annotate(mes=TruncMonth("fecha_inicio"))
            .values("mes")
            .annotate(usuarios=Count("usuario_id", distinct=True))
            .order_by("mes")
        )
        return [{"mes": row["mes"].strftime("%Y-%m"), "usuarios": row["usuarios"]} for row in qs]


class DjangoPagoRepository(PagoRepository):
    def get_by_id(self, pago_id: int) -> Pago | None:
        try:
            model = PagoModel.objects.select_related("alquiler", "alquiler__usuario", "alquiler__equipo").get(
                pk=pago_id
            )
        except PagoModel.DoesNotExist:
            return None
        alquiler_entity = _map_alquiler_model_to_entity(model.alquiler)
        return _map_pago_model_to_entity(model, alquiler_entity=alquiler_entity)

    def create(self, pago: Pago) -> Pago:
        alquiler_model = AlquilerModel.objects.get(pk=pago.alquiler.id)
        model = PagoModel.objects.create(
            alquiler=alquiler_model,
            monto=pago.monto,
            metodo=pago.metodo.value,
            estado=pago.estado.value,
            fecha_pago=pago.fecha_pago,
        )
        alquiler_entity = _map_alquiler_model_to_entity(alquiler_model)
        return _map_pago_model_to_entity(model, alquiler_entity=alquiler_entity)

    def save(self, pago: Pago) -> Pago:
        model = PagoModel.objects.get(pk=pago.id)
        model.estado = pago.estado.value
        model.monto = pago.monto
        model.save(update_fields=["estado", "monto"])
        alquiler_entity = _map_alquiler_model_to_entity(model.alquiler)
        return _map_pago_model_to_entity(model, alquiler_entity=alquiler_entity)

    def count_pendientes(self) -> int:
        return PagoModel.objects.filter(estado=PagoEstado.PENDIENTE.value).count()

    def ingresos_mes_actual(self) -> float:
        ahora = timezone.now()
        inicio = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total = PagoModel.objects.filter(
            fecha_pago__gte=inicio,
            estado=PagoEstado.CONFIRMADO.value,
        ).aggregate(s=Sum("monto"))["s"]
        return float(total or 0)

    def ingresos_mes_anterior(self) -> float:
        ahora = timezone.now()
        inicio_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fin_anterior = inicio_actual - timedelta(days=1)
        inicio_anterior = fin_anterior.replace(day=1)
        total = PagoModel.objects.filter(
            fecha_pago__gte=inicio_anterior,
            fecha_pago__lt=inicio_actual,
            estado=PagoEstado.CONFIRMADO.value,
        ).aggregate(s=Sum("monto"))["s"]
        return float(total or 0)

    def list_by_usuario_id(self, usuario_id: int):
        qs = PagoModel.objects.filter(alquiler__usuario_id=usuario_id).select_related(
            "alquiler", "alquiler__usuario", "alquiler__equipo"
        )
        return [_map_pago_model_to_entity(m) for m in qs]


class DjangoPenalizacionRepository(PenalizacionRepository):
    def create(self, penalizacion: Penalizacion) -> Penalizacion:
        alquiler_model = AlquilerModel.objects.get(pk=penalizacion.alquiler.id)
        model = PenalizacionModel.objects.create(
            alquiler=alquiler_model,
            motivo=penalizacion.motivo,
            monto=penalizacion.monto,
        )
        alquiler_entity = _map_alquiler_model_to_entity(alquiler_model)
        return _map_penalizacion_model_to_entity(model, alquiler_entity=alquiler_entity)

    def exists_for_alquiler(self, alquiler_id: int) -> bool:
        return PenalizacionModel.objects.filter(alquiler_id=alquiler_id).exists()

