from django.contrib import admin

from apps.ventas.models import Venta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    autocomplete_fields = ["producto"]
    fields = (
        "producto",
        "cantidad",
        "precio_unitario",
        "costo_unitario",
        "descuento",
        "subtotal",
    )


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "usuario",
        "metodo_pago",
        "total",
        "estado",
        "fecha",
    )
    list_filter = ("estado", "metodo_pago", "fecha")
    search_fields = (
        "numero",
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
    )
    inlines = [DetalleVentaInline]
    readonly_fields = ("fecha", "creado_en", "actualizado_en")

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.usuario_id:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)
