
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.compras.models import Compra
from apps.inventario.models import MovimientoInventario
from apps.inventario.services import registrar_movimiento
from apps.productos.models import Producto


@transaction.atomic
def confirmar_compra(compra: Compra, usuario):
    """
    Confirma una compra e ingresa los productos al inventario.
    """

    compra = Compra.objects.select_for_update().get(pk=compra.pk)

    if compra.estado == Compra.Estado.CONFIRMADA:
        return False, "Esta compra ya ha sido confirmada previamente."

    if compra.estado == Compra.Estado.ANULADA:
        return False, "No se puede confirmar una compra anulada."

    detalles = list(
        compra.detalles.select_related("producto").all()
    )

    if not detalles:
        return False, "No se puede confirmar una compra sin productos."

    try:
        for detalle in detalles:
            producto = Producto.objects.select_for_update().get(
                pk=detalle.producto_id
            )

            registrar_movimiento(
                producto_id=producto.pk,
                usuario=usuario,
                tipo=MovimientoInventario.Tipo.ENTRADA_COMPRA,
                cantidad=detalle.cantidad,
                motivo=(
                    f"Ingreso por Compra #{compra.pk}. "
                    f"Proveedor: {compra.proveedor.nombre}"
                ),
                compra=compra,
            )

            producto.costo = detalle.costo_unitario
            producto.save(update_fields=["costo", "actualizado_en"])

        compra.estado = Compra.Estado.CONFIRMADA
        compra.save(update_fields=["estado", "actualizado_en"])

    except (ValidationError, Producto.DoesNotExist) as error:
        return False, str(error)

    return True, (
        f"Compra #{compra.pk} confirmada e ingresada al inventario."
    )


@transaction.atomic
def anular_compra(compra: Compra, usuario, motivo: str = ""):
    """
    Anula una compra y revierte sus entradas de inventario.
    """

    compra = Compra.objects.select_for_update().get(pk=compra.pk)

    if compra.estado == Compra.Estado.ANULADA:
        return False, "Esta compra ya se encuentra anulada."

    try:
        if compra.estado == Compra.Estado.CONFIRMADA:

            detalles = list(
                compra.detalles.select_related("producto").all()
            )

            for detalle in detalles:
                producto = Producto.objects.select_for_update().get(
                    pk=detalle.producto_id
                )

                if producto.stock < detalle.cantidad:
                    raise ValidationError(
                        f"No se puede anular la compra. "
                        f"El producto '{producto.nombre}' tiene "
                        f"{producto.stock} unidades disponibles y "
                        f"se necesitan {detalle.cantidad} para revertir."
                    )

                registrar_movimiento(
                    producto_id=producto.pk,
                    usuario=usuario,
                    tipo=MovimientoInventario.Tipo.ANULACION,
                    cantidad=detalle.cantidad,
                    motivo=(
                        f"Reversión por anulación de Compra #{compra.pk}. "
                        f"Motivo: {motivo or 'No especificado'}"
                    ),
                    compra=compra,
                )

        compra.estado = Compra.Estado.ANULADA

        anotacion = (
            f"[ANULADA por {usuario.username}] "
            f"Motivo: {motivo or 'No especificado'}"
        )

        compra.observaciones = (
            f"{compra.observaciones}\n{anotacion}".strip()
            if compra.observaciones
            else anotacion
        )

        compra.save(
            update_fields=[
                "estado",
                "observaciones",
                "actualizado_en",
            ]
        )

    except (ValidationError, Producto.DoesNotExist) as error:
        return False, str(error)

    return True, (
        f"La compra #{compra.pk} fue anulada y su inventario revertido."
    )
