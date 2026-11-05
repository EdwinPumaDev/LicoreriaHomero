
from django.urls import path
from apps.compras import views

app_name = "compras"

urlpatterns = [
    path("", views.lista_compras, name="lista"),
    path("crear/", views.crear_compra, name="crear"),
    path("<int:pk>/", views.detalle_compra, name="detalle"),
    path(
        "<int:pk>/confirmar/",
        views.confirmar_compra_view,
        name="confirmar",
    ),
    path(
        "<int:pk>/anular/",
        views.anular_compra_view,
        name="anular",
    ),
]
