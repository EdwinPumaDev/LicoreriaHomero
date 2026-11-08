
from django.urls import path

from apps.ventas import views
from apps.ventas.pdf import generar_comprobante_pdf


app_name = "ventas"


urlpatterns = [

    # Listado de ventas
    path(
        "",
        views.lista_ventas,
        name="lista",
    ),

    # Crear venta
    path(
        "nueva/",
        views.crear_venta,
        name="crear",
    ),

    # Detalle de venta
    path(
        "<int:pk>/",
        views.detalle_venta,
        name="detalle",
    ),

    # Confirmar venta
    path(
        "<int:pk>/confirmar/",
        views.confirmar_venta_view,
        name="confirmar",
    ),

    # Anular venta
    path(
        "<int:pk>/anular/",
        views.anular_venta_view,
        name="anular",
    ),

    # Pantalla para visualizar el comprobante
    path(
        "<int:pk>/comprobante/ver/",
        views.ver_comprobante,
        name="ver_comprobante",
    ),

    # Generar y descargar comprobante PDF
    path(
        "<int:pk>/comprobante/",
        generar_comprobante_pdf,
        name="comprobante",
    ),
]
