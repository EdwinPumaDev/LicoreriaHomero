from django.urls import path
from apps.publico import views

app_name = "publico"

urlpatterns = [
    # Página pública
    path("", views.inicio, name="inicio"),
    path("catalogo/", views.catalogo, name="catalogo"),

    # Carrito de compras
    path("carrito/", views.ver_carrito, name="carrito"),
    path(
        "carrito/agregar/<int:producto_id>/",
        views.agregar_carrito,
        name="agregar_carrito"
    ),
    path(
        "carrito/actualizar/<int:producto_id>/",
        views.actualizar_carrito,
        name="actualizar_carrito"
    ),
    path(
        "carrito/eliminar/<int:producto_id>/",
        views.eliminar_del_carrito,
        name="eliminar_carrito"
    ),

    # Pedidos públicos
    path("pedido/", views.crear_pedido, name="crear_pedido"),

    # Gestión de pedidos desde el panel administrativo
    path("gestion-pedidos/", views.lista_pedidos, name="lista_pedidos"),
    path(
        "gestion-pedidos/<int:pk>/aceptar/",
        views.aceptar_pedido,
        name="aceptar_pedido"
    ),
    path(
        "gestion-pedidos/<int:pk>/rechazar/",
        views.rechazar_pedido,
        name="rechazar_pedido"
    ),
]