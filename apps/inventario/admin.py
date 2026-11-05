from django.contrib import admin

from apps.inventario.models import MovimientoInventario


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "producto",
        "tipo",
        "cantidad",
        "stock_anterior",
        "stock_posterior",
        "usuario",
        "motivo",
    )
    list_filter = ("tipo", "fecha")
    search_fields = (
        "producto__nombre",
        "producto__codigo",
        "usuario__username",
        "motivo",
    )
    readonly_fields = (
        "fecha",
        "producto",
        "usuario",
        "tipo",
        "cantidad",
        "stock_anterior",
        "stock_posterior",
        "compra",
        "venta",
    )

    def has_add_permission(self, request):
        # Los movimientos de inventario deben generarse por transacciones de compras, ventas o ajustes
        return False
