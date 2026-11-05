
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventario.models import MovimientoInventario
from apps.productos.models import Producto


@transaction.atomic
def registrar_movimiento(
    *,
    producto_id,
    usuario,
    tipo,
    cantidad,
    motivo="",
    compra=None,
    venta=None,
):
    """
    Registra un movimiento de inventario y actualiza las existencias
    dentro de una única transacción de PostgreSQL.
    """

    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        raise ValidationError("La cantidad debe ser un número entero.")

    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser mayor que cero.")

    tipos_entrada = {
        MovimientoInventario.Tipo.ENTRADA_COMPRA,
        MovimientoInventario.Tipo.AJUSTE_ENTRADA,
        MovimientoInventario.Tipo.DEVOLUCION,
    }

    tipos_salida = {
        MovimientoInventario.Tipo.SALIDA_VENTA,
        MovimientoInventario.Tipo.AJUSTE_SALIDA,
        MovimientoInventario.Tipo.ANULACION,
    }

    if tipo not in tipos_entrada | tipos_salida:
        raise ValidationError("El tipo de movimiento no es válido.")

    if tipo == MovimientoInventario.Tipo.ENTRADA_COMPRA and compra is None:
        raise ValidationError("La entrada por compra requiere una compra relacionada.")

    if tipo == MovimientoInventario.Tipo.SALIDA_VENTA and venta is None:
        raise ValidationError("La salida por venta requiere una venta relacionada.")

    producto = (
        Producto.objects
        .select_for_update()
        .get(pk=producto_id)
    )

    stock_anterior = producto.stock

    if tipo in tipos_entrada:
        stock_posterior = stock_anterior + cantidad
    else:
        if stock_anterior < cantidad:
            raise ValidationError(
                f"Stock insuficiente para '{producto.nombre}'. "
                f"Disponible: {stock_anterior}. Solicitado: {cantidad}."
            )

        stock_posterior = stock_anterior - cantidad

    producto.stock = stock_posterior
    producto.save(update_fields=["stock", "actualizado_en"])

    movimiento = MovimientoInventario.objects.create(
        producto=producto,
        usuario=usuario,
        tipo=tipo,
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_posterior=stock_posterior,
        motivo=motivo,
        compra=compra,
        venta=venta,
    )

    return movimiento


@transaction.atomic
def registrar_ajuste(
    *,
    producto_id,
    usuario,
    cantidad,
    tipo,
    motivo,
):
    """
    Registra un ajuste manual de inventario.
    """

    if not motivo or not motivo.strip():
        raise ValidationError(
            "Debes indicar el motivo del ajuste de inventario."
        )

    tipos_ajuste = {
        MovimientoInventario.Tipo.AJUSTE_ENTRADA,
        MovimientoInventario.Tipo.AJUSTE_SALIDA,
    }

    if tipo not in tipos_ajuste:
        raise ValidationError("El tipo de ajuste no es válido.")

    return registrar_movimiento(
        producto_id=producto_id,
        usuario=usuario,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo.strip(),
    )
