from django.contrib import admin

from apps.caja.models import IngresoCaja


@admin.register(IngresoCaja)
class IngresoCajaAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "venta",
        "monto",
        "metodo_pago",
        "referencia",
        "usuario",
    )
    list_filter = ("metodo_pago", "fecha")
    search_fields = (
        "venta__numero",
        "referencia",
        "usuario__username",
    )
    readonly_fields = ("fecha",)
