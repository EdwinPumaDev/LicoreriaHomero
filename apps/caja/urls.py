from django.urls import path
from apps.caja import views

app_name = "caja"

urlpatterns = [
    path("", views.lista_ingresos, name="lista_ingresos"),
]