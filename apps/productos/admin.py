from django.contrib import admin
from django.utils.html import format_html

from apps.productos.models import Categoria, Marca, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo", "total_productos", "creado_en")
    list_filter = ("activo",)
    search_fields = ("nombre", "descripcion")

    @admin.display(description="Total de productos")
    def total_productos(self, obj):
        return obj.productos.count()


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo", "total_productos", "creado_en")
    list_filter = ("activo",)
    search_fields = ("nombre", "descripcion")

    @admin.display(description="Total de productos")
    def total_productos(self, obj):
        return obj.productos.count()


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "categoria",
        "marca",
        "unidad_medida",
        "costo",
        "precio_venta",
        "stock",
        "stock_minimo",
        "alerta_reposicion",
        "activo",
    )
    list_filter = ("categoria", "marca", "unidad_medida", "activo")
    search_fields = ("codigo", "codigo_barras", "nombre")
    list_editable = ("precio_venta", "stock_minimo", "activo")
    readonly_fields = ("creado_en", "actualizado_en")
    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "codigo",
                    "codigo_barras",
                    "nombre",
                    "descripcion",
                    "imagen",
                )
            },
        ),
        (
            "Clasificación",
            {"fields": ("categoria", "marca", "unidad_medida")},
        ),
        (
            "Precios y Costos (Bs)",
            {"fields": ("costo", "precio_venta")},
        ),
        (
            "Control de Stock",
            {"fields": ("stock", "stock_minimo")},
        ),
        (
            "Estado y Trazabilidad",
            {"fields": ("activo", "creado_en", "actualizado_en")},
        ),
    )

    @admin.display(description="Reposición")
    def alerta_reposicion(self, obj):
        if obj.necesita_reposicion:
            return format_html(
                '<span style="color: #b26a25; font-weight: bold; background: #fff0e3; padding: 2px 8px; border-radius: 4px;">⚠️ Reabastecer</span>'
            )
        return format_html(
            '<span style="color: #367f5a; background: #e9f4ee; padding: 2px 8px; border-radius: 4px;">✓ Normal</span>'
        )
