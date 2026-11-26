
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator


class MovimientoInventario(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA_COMPRA = "ENTRADA_COMPRA", "Entrada por compra"
        SALIDA_VENTA = "SALIDA_VENTA", "Salida por venta"
        AJUSTE_ENTRADA = "AJUSTE_ENTRADA", "Ajuste de entrada"
        AJUSTE_SALIDA = "AJUSTE_SALIDA", "Ajuste de salida"
        DEVOLUCION = "DEVOLUCION", "Devolución"
        ANULACION = "ANULACION", "Reversión por anulación"

    producto = models.ForeignKey(
        "productos.Producto",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
        verbose_name="Producto",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
        verbose_name="Usuario responsable",
    )
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        verbose_name="Tipo de movimiento",
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad movida",
    )
    stock_anterior = models.PositiveIntegerField(
        verbose_name="Stock anterior",
    )
    stock_posterior = models.PositiveIntegerField(
        verbose_name="Stock posterior",
    )
    motivo = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Motivo",
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del movimiento",
    )

    compra = models.ForeignKey(
        "compras.Compra",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
        null=True,
        blank=True,
        verbose_name="Compra relacionada",
    )
    venta = models.ForeignKey(
        "ventas.Venta",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
        null=True,
        blank=True,
        verbose_name="Venta relacionada",
    )

    class Meta:
        db_table = "movimientos_inventario"
        ordering = ["-fecha"]
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad__gte=1),
                name="inv_cantidad_min_1",
            ),
            models.CheckConstraint(
                condition=Q(stock_anterior__gte=0),
                name="inv_stock_ant_no_neg",
            ),
            models.CheckConstraint(
                condition=Q(stock_posterior__gte=0),
                name="inv_stock_post_no_neg",
            ),
        ]

    def __str__(self):
        return (
            f"{self.producto.nombre} - "
            f"{self.get_tipo_display()} - {self.cantidad}"
        )
