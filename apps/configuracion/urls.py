from django.urls import path

from apps.configuracion import views


app_name = "configuracion"

urlpatterns = [
    path(
        "",
        views.personalizacion,
        name="personalizacion",
    ),
]