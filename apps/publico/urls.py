from django.urls import path
from apps.publico import views

app_name = "publico"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("carrito/", views.ver_carrito, name="carrito"),
    path("carrito/agregar/<int:producto_id>/", views.agregar_carrito, name="agregar_carrito"),
    path("carrito/actualizar/<int:producto_id>/", views.actualizar_carrito, name="actualizar_carrito"),
    path("carrito/eliminar/<int:producto_id>/", views.eliminar_del_carrito, name="eliminar_carrito"),
]