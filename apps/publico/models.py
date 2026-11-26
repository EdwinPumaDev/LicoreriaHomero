
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator


class Pedido(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ACEPTADO = "ACEPTADO", "Aceptado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    nombre_cliente = models.CharField(
        max_length=150,
        verbose_name="Nombre del cliente"
    )

    telefono = models.CharField(
        max_length=30,
        verbose_name="Teléfono"
    )

    direccion = models.CharField(
        max_length=250,
        verbose_name="Dirección"
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name="Estado del pedido"
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Total del pedido"
    )

    venta = models.OneToOneField(
        "ventas.Venta",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="pedido_publico",
        verbose_name="Venta generada"
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del pedido"
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    class Meta:
        db_table = "pedidos_publicos"
        ordering = ["-creado_en"]
        verbose_name = "Pedido público"
        verbose_name_plural = "Pedidos públicos"
        constraints = [
            models.CheckConstraint(
                condition=Q(total__gte=0),
                name="pedido_total_no_neg",
            ),
        ]

    def __str__(self):
        return f"Pedido #{self.pk} - {self.nombre_cliente}"


class DetallePedido(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
        verbose_name="Pedido"
    )

    producto = models.ForeignKey(
        "productos.Producto",
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
        verbose_name="Producto"
    )

    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad"
    )

    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio unitario"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Subtotal"
    )

    class Meta:
        db_table = "detalles_pedido"
        verbose_name = "Detalle del pedido"
        verbose_name_plural = "Detalles de pedido"
        constraints = [
            models.CheckConstraint(
                condition=Q(precio_unitario__gte=0),
                name="detpedido_precio_no_neg",
            ),
            models.CheckConstraint(
                condition=Q(subtotal__gte=0),
                name="detpedido_subtotal_no_neg",
            ),
        ]

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"
