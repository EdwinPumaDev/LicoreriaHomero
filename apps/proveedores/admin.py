from django.contrib import admin

from apps.proveedores.models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "nit",
        "persona_contacto",
        "telefono",
        "correo",
        "total_compras",
        "activo",
    )
    list_filter = ("activo",)
    search_fields = (
        "nombre",
        "nit",
        "persona_contacto",
        "telefono",
        "correo",
    )
    list_editable = ("activo",)
    readonly_fields = ("creado_en", "actualizado_en")

    @admin.display(description="Total compras")
    def total_compras(self, obj):
        return obj.compras.count()
