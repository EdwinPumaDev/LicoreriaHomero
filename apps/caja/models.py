
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class IngresoCaja(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        QR = "QR", "QR"
        TARJETA = "TARJETA", "Tarjeta"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
        OTRO = "OTRO", "Otro"

    venta = models.OneToOneField(
        "ventas.Venta",
        on_delete=models.PROTECT,
        related_name="ingreso_caja",
        verbose_name="Venta relacionada",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ingresos_caja",
        verbose_name="Usuario responsable",
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
        default=MetodoPago.EFECTIVO,
        verbose_name="Método de pago",
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto recibido",
    )
    referencia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Referencia de pago",
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de ingreso",
    )

    class Meta:
        db_table = "ingresos_caja"
        ordering = ["-fecha"]
        verbose_name = "Ingreso de caja"
        verbose_name_plural = "Ingresos de caja"

    def __str__(self):
        return f"Ingreso de Bs {self.monto} - Venta {self.venta.numero}"
