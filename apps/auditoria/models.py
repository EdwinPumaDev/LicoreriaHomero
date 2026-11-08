
from django.conf import settings
from django.db import models


class RegistroAuditoria(models.Model):

    class TipoAccion(models.TextChoices):
        INICIO_SESION = "INICIO_SESION", "Inicio de sesión"
        CIERRE_SESION = "CIERRE_SESION", "Cierre de sesión"
        CREACION = "CREACION", "Creación"
        EDICION = "EDICION", "Edición"
        ELIMINACION = "ELIMINACION", "Eliminación"
        CONFIRMACION = "CONFIRMACION", "Confirmación"
        ANULACION = "ANULACION", "Anulación"
        AJUSTE = "AJUSTE", "Ajuste"
        OTRO = "OTRO", "Otro"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros_auditoria",
        verbose_name="Usuario responsable",
    )

    tipo_accion = models.CharField(
        max_length=20,
        choices=TipoAccion.choices,
        default=TipoAccion.OTRO,
        verbose_name="Tipo de acción",
    )

    modulo = models.CharField(
        max_length=100,
        verbose_name="Módulo",
    )

    descripcion = models.TextField(
        verbose_name="Descripción",
    )

    direccion_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP",
    )

    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora",
    )

    class Meta:
        db_table = "registros_auditoria"
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"
        ordering = ["-fecha_hora"]

    def __str__(self):
        nombre_usuario = self.usuario.username if self.usuario else "Sistema"

        return (
            f"{nombre_usuario} - "
            f"{self.get_tipo_accion_display()} - "
            f"{self.modulo}"
        )
