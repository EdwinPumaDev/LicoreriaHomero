
from django.urls import path

from apps.inventario import views


app_name = "inventario"

urlpatterns = [
    path("", views.lista_movimientos, name="lista"),
    path("ajuste/", views.crear_ajuste, name="crear_ajuste"),
]
