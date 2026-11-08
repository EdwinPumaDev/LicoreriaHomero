
from django.db import models


class ConfiguracionSistema(models.Model):

    # IDENTIDAD DEL NEGOCIO
    nombre_comercial = models.CharField(
        max_length=150,
        default="Licorería Homero",
        verbose_name="Nombre comercial",
    )

    nombre_sistema = models.CharField(
        max_length=150,
        default="Licorería Homero",
        verbose_name="Nombre del sistema",
    )

    logo = models.ImageField(
        upload_to="configuracion/logos/",
        blank=True,
        null=True,
        verbose_name="Logo del negocio",
    )

    favicon = models.ImageField(
        upload_to="configuracion/favicon/",
        blank=True,
        null=True,
        verbose_name="Favicon",
    )

    propietario = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Propietario",
    )

    nit = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="NIT",
    )

    direccion = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Dirección",
    )

    telefono = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Teléfono",
    )

    # APARIENCIA DEL SISTEMA
    color_principal = models.CharField(
        max_length=7,
        default="#701E32",
        verbose_name="Color principal",
    )

    color_secundario = models.CharField(
        max_length=7,
        default="#D4AF37",
        verbose_name="Color secundario",
    )

    color_fondo = models.CharField(
        max_length=7,
        default="#F5F5F5",
        verbose_name="Color de fondo",
    )

    color_texto = models.CharField(
        max_length=7,
        default="#333333",
        verbose_name="Color del texto",
    )

    tipografia = models.CharField(
        max_length=50,
        default="Inter",
        verbose_name="Tipografía",
    )

    tema = models.CharField(
        max_length=20,
        choices=[
            ("CLARO", "Claro"),
            ("OSCURO", "Oscuro"),
        ],
        default="CLARO",
        verbose_name="Tema visual",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        db_table = "configuracion_sistema"
        verbose_name = "Configuración del sistema"
        verbose_name_plural = "Configuración del sistema"

    def __str__(self):
        return self.nombre_sistema

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
