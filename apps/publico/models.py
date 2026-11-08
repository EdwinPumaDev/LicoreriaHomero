from django.db import models


class Pedido(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ACEPTADO = "ACEPTADO", "Aceptado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    nombre_cliente = models.CharField(
        max_length=150,
        verbose_name="Nombre del cliente",
    )

    telefono = models.CharField(
        max_length=30,
        verbose_name="Teléfono",
    )

    direccion = models.CharField(
        max_length=250,
        verbose_name="Dirección",
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name="Estado del pedido",
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Total del pedido",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del pedido",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        db_table = "pedidos_publicos"
        ordering = ["-creado_en"]
        verbose_name = "Pedido público"
        verbose_name_plural = "Pedidos públicos"

    def __str__(self):
        return f"Pedido #{self.pk} - {self.nombre_cliente}"


class DetallePedido(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
        verbose_name="Pedido",
    )

    producto = models.ForeignKey(
        "productos.Producto",
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
        verbose_name="Producto",
    )

    cantidad = models.PositiveIntegerField(
        verbose_name="Cantidad",
    )

    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Precio unitario",
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Subtotal",
    )

    class Meta:
        db_table = "detalles_pedido"
        verbose_name = "Detalle del pedido"
        verbose_name_plural = "Detalles del pedido"

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad}"