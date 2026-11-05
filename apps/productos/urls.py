
from django.urls import path
from apps.productos import views

app_name = "productos"

urlpatterns = [
    # Productos
    path("", views.lista_productos, name="lista"),
    path("crear/", views.crear_producto, name="crear"),
    path("<int:pk>/editar/", views.editar_producto, name="editar"),
    path("<int:pk>/eliminar/", views.eliminar_producto, name="eliminar"),

    # Categorías y marcas
    path(
        "categorias-marcas/",
        views.categorias_marcas,
        name="categorias_marcas",
    ),

    # Editar categoría y marca
    path(
        "categorias/<int:pk>/editar/",
        views.editar_categoria,
        name="editar_categoria",
    ),
    path(
        "marcas/<int:pk>/editar/",
        views.editar_marca,
        name="editar_marca",
    ),

    # Activar o desactivar categoría y marca
    path(
        "categorias/<int:pk>/estado/",
        views.cambiar_estado_categoria,
        name="cambiar_estado_categoria",
    ),
    path(
        "marcas/<int:pk>/estado/",
        views.cambiar_estado_marca,
        name="cambiar_estado_marca",
    ),
]
