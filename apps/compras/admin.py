from django.contrib import admin

from apps.compras.models import Compra, DetalleCompra


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    autocomplete_fields = ["producto"]
    fields = ("producto", "cantidad", "costo_unitario", "subtotal")


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "proveedor",
        "numero_comprobante",
        "total",
        "estado",
        "usuario",
        "fecha",
    )
    list_filter = ("estado", "fecha")
    search_fields = (
        "numero_comprobante",
        "proveedor__nombre",
        "usuario__username",
    )
    inlines = [DetalleCompraInline]
    readonly_fields = ("fecha", "creado_en", "actualizado_en")

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)
