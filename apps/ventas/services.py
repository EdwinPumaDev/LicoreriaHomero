
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.ventas.models import Venta
from apps.productos.models import Producto
from apps.inventario.models import MovimientoInventario
from apps.inventario.services import registrar_movimiento
from apps.caja.models import IngresoCaja


# ==========================================================
# CALCULAR TOTALES DE UNA VENTA
# ==========================================================

@transaction.atomic
def calcular_totales(venta):

    venta = Venta.objects.select_for_update().get(
        pk=venta.pk
    )

    detalles = venta.detalles.all()

    subtotal_general = Decimal("0.00")

    for detalle in detalles:

        if detalle.cantidad <= 0:
            raise ValidationError(
                "La cantidad de un producto debe ser mayor que cero."
            )

        if detalle.precio_unitario < 0:
            raise ValidationError(
                f"El precio de '{detalle.producto.nombre}' no es válido."
            )

        importe = (
            Decimal(detalle.cantidad)
            * detalle.precio_unitario
        )

        if detalle.descuento < 0 or detalle.descuento > importe:
            raise ValidationError(
                f"El descuento de '{detalle.producto.nombre}' no es válido."
            )

        detalle.subtotal = importe - detalle.descuento

        detalle.save(
            update_fields=["subtotal"]
        )

        subtotal_general += detalle.subtotal

    descuento_general = venta.descuento or Decimal("0.00")

    if descuento_general < 0 or descuento_general > subtotal_general:
        raise ValidationError(
            "El descuento general de la venta no es válido."
        )

    venta.subtotal = subtotal_general
    venta.total = subtotal_general - descuento_general

    venta.save(
        update_fields=[
            "subtotal",
            "total",
            "actualizado_en",
        ]
    )

    return venta


# ==========================================================
# CONFIRMAR VENTA, DESCONTAR INVENTARIO Y REGISTRAR CAJA
# ==========================================================

@transaction.atomic
def confirmar_venta(venta, usuario):

    venta = Venta.objects.select_for_update().get(
        pk=venta.pk
    )

    if venta.estado == Venta.Estado.CONFIRMADA:
        raise ValidationError(
            "Esta venta ya fue confirmada anteriormente."
        )

    if venta.estado == Venta.Estado.ANULADA:
        raise ValidationError(
            "No se puede confirmar una venta anulada."
        )

    detalles = list(
        venta.detalles.select_related("producto").all()
    )

    if not detalles:
        raise ValidationError(
            "No se puede confirmar una venta sin productos."
        )

    productos_ids = sorted({
        detalle.producto_id
        for detalle in detalles
    })

    productos = {
        producto.pk: producto
        for producto in (
            Producto.objects
            .select_for_update()
            .filter(pk__in=productos_ids)
            .order_by("pk")
        )
    }

    cantidades_por_producto = {}

    for detalle in detalles:

        producto = productos.get(detalle.producto_id)

        if producto is None:
            raise ValidationError(
                "Uno de los productos de la venta ya no existe."
            )

        if not producto.activo:
            raise ValidationError(
                f"El producto '{producto.nombre}' está inactivo."
            )

        if detalle.cantidad <= 0:
            raise ValidationError(
                f"La cantidad de '{producto.nombre}' no es válida."
            )

        if detalle.precio_unitario < 0 or detalle.costo_unitario < 0:
            raise ValidationError(
                f"El precio o costo de '{producto.nombre}' no es válido."
            )

        importe = (
            Decimal(detalle.cantidad)
            * detalle.precio_unitario
        )

        if detalle.descuento < 0 or detalle.descuento > importe:
            raise ValidationError(
                f"El descuento de '{producto.nombre}' no es válido."
            )

        cantidades_por_producto[producto.pk] = (
            cantidades_por_producto.get(producto.pk, 0)
            + detalle.cantidad
        )

    # Comprobar existencias.
    for producto_id, cantidad_total in cantidades_por_producto.items():

        producto = productos[producto_id]

        if producto.stock < cantidad_total:
            raise ValidationError(
                f"Stock insuficiente para '{producto.nombre}'. "
                f"Disponible: {producto.stock}. "
                f"Solicitado: {cantidad_total}."
            )

    # Actualizar los importes.
    calcular_totales(venta)

    # Registrar las salidas de inventario.
    for detalle in detalles:

        registrar_movimiento(
            producto_id=detalle.producto_id,
            usuario=usuario,
            tipo=MovimientoInventario.Tipo.SALIDA_VENTA,
            cantidad=detalle.cantidad,
            motivo=f"Salida por Venta #{venta.numero}",
            venta=venta,
        )

    # Confirmar la venta.
    venta.estado = Venta.Estado.CONFIRMADA

    venta.save(
        update_fields=[
            "estado",
            "actualizado_en",
        ]
    )

    # Registrar automáticamente el ingreso en Caja.
    IngresoCaja.objects.get_or_create(
        venta=venta,
        defaults={
            "usuario": usuario,
            "metodo_pago": venta.metodo_pago,
            "monto": venta.total,
            "observaciones": (
                f"Ingreso automático por la venta #{venta.numero}"
            ),
        },
    )

    return venta


# ==========================================================
# ANULAR VENTA, DEVOLVER INVENTARIO Y ANULAR INGRESO EN CAJA
# ==========================================================

@transaction.atomic
def anular_venta(venta, usuario, motivo=""):

    venta = Venta.objects.select_for_update().get(
        pk=venta.pk
    )

    if venta.estado == Venta.Estado.ANULADA:
        raise ValidationError(
            "Esta venta ya se encuentra anulada."
        )

    if venta.estado == Venta.Estado.BORRADOR:
        raise ValidationError(
            "No se puede anular una venta que todavía no ha sido confirmada."
        )

    # Validar el motivo antes de realizar operaciones.
    motivo_final = motivo.strip()

    if not motivo_final:
        raise ValidationError(
            "Debes indicar un motivo para anular la venta."
        )

    detalles = list(
        venta.detalles.select_related("producto").all()
    )

    if not detalles:
        raise ValidationError(
            "La venta no contiene productos para devolver."
        )

    productos_ids = sorted({
        detalle.producto_id
        for detalle in detalles
    })

    productos = {
        producto.pk: producto
        for producto in (
            Producto.objects
            .select_for_update()
            .filter(pk__in=productos_ids)
            .order_by("pk")
        )
    }

    for detalle in detalles:

        if detalle.producto_id not in productos:
            raise ValidationError(
                "No se encontró uno de los productos de la venta."
            )

    # Devolver las cantidades al inventario.
    for detalle in detalles:

        registrar_movimiento(
            producto_id=detalle.producto_id,
            usuario=usuario,
            tipo=MovimientoInventario.Tipo.DEVOLUCION,
            cantidad=detalle.cantidad,
            motivo=(
                f"Devolución por anulación de Venta #{venta.numero}. "
                f"Motivo: {motivo_final}"
            ),
            venta=venta,
        )

    # Registrar la anulación en las observaciones.
    anotacion = (
        f"[ANULADA por {usuario.username}] "
        f"Motivo: {motivo_final}"
    )

    venta.observaciones = (
        f"{venta.observaciones}\n{anotacion}".strip()
        if venta.observaciones
        else anotacion
    )

    venta.estado = Venta.Estado.ANULADA

    venta.save(
        update_fields=[
            "estado",
            "observaciones",
            "actualizado_en",
        ]
    )

    # Anular el ingreso relacionado en Caja.
    ingreso = (
        IngresoCaja.objects
        .select_for_update()
        .filter(venta=venta)
        .first()
    )

    if ingreso and not ingreso.anulado:

        ingreso.anulado = True
        ingreso.anulado_en = timezone.now()
        ingreso.motivo_anulacion = motivo_final

        ingreso.save(
            update_fields=[
                "anulado",
                "anulado_en",
                "motivo_anulacion",
            ]
        )

    return venta
