
from django.conf import settings
from django.db import models


class PerfilUsuario(models.Model):
    class Cargo(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        ENCARGADO = "ENCARGADO", "Encargado"
        VENDEDOR = "VENDEDOR", "Vendedor"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario del sistema",
    )
    cargo = models.CharField(
        max_length=20,
        choices=Cargo.choices,
        default=Cargo.VENDEDOR,
        verbose_name="Cargo",
    )
    telefono = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Teléfono",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Perfil activo",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "perfiles_usuario"
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self):
        return f"{self.usuario.username} - {self.get_cargo_display()}"


# Señal para crear o sincronizar automáticamente el perfil de usuario
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_o_guardar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        cargo = (
            PerfilUsuario.Cargo.ADMINISTRADOR
            if instance.is_superuser
            else PerfilUsuario.Cargo.VENDEDOR
        )
        PerfilUsuario.objects.get_or_create(usuario=instance, defaults={"cargo": cargo})
    elif hasattr(instance, "perfil"):
        instance.perfil.save()

