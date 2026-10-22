
from django.db import models


class Proveedor(models.Model):
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre o razón social",
    )
    nit = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        verbose_name="NIT",
    )
    persona_contacto = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Persona de contacto",
    )
    telefono = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Teléfono",
    )
    correo = models.EmailField(
        blank=True,
        verbose_name="Correo electrónico",
    )
    direccion = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Dirección",
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "proveedores"
        ordering = ["nombre"]
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.nombre
