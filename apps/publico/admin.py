from django.contrib import admin

from apps.publico.models import Pedido, DetallePedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = (
        "producto",
        "cantidad",
        "precio_unitario",
        "subtotal",
    )
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombre_cliente",
        "telefono",
        "total",
        "estado",
        "creado_en",
    )

    list_filter = (
        "estado",
        "creado_en",
    )

    search_fields = (
        "nombre_cliente",
        "telefono",
        "direccion",
    )

    readonly_fields = (
        "nombre_cliente",
        "telefono",
        "direccion",
        "observaciones",
        "total",
        "creado_en",
        "actualizado_en",
    )

    inlines = [DetallePedidoInline]

    ordering = ("-creado_en",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False