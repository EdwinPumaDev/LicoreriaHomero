from django.contrib import admin
from apps.configuracion.models import ConfiguracionSistema


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_comercial",
        "nombre_sistema",
        "tema",
        "actualizado_en",
    )

    fieldsets = (
        ("Identidad del negocio", {
            "fields": (
                "nombre_comercial",
                "nombre_sistema",
                "logo",
                "favicon",
                "propietario",
                "nit",
                "direccion",
                "telefono",
            )
        }),
        ("Apariencia del sistema", {
            "fields": (
                "color_principal",
                "color_secundario",
                "color_fondo",
                "color_texto",
                "tipografia",
                "tema",
            )
        }),
    )

    def has_add_permission(self, request):
        return not ConfiguracionSistema.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False