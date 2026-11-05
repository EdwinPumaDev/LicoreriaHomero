from django.urls import path
from apps.proveedores import views

app_name = "proveedores"

urlpatterns = [
    path("", views.lista_proveedores, name="lista"),
    path("crear/", views.crear_proveedor, name="crear"),
    path("<int:pk>/editar/", views.editar_proveedor, name="editar"),
    path("<int:pk>/eliminar/", views.eliminar_proveedor, name="eliminar"),
]