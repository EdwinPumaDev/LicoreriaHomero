
from django.urls import path
from apps.usuarios import views

app_name = "usuarios"

urlpatterns = [
    # Lista de usuarios
    path("", views.lista_usuarios, name="lista"),

    # Registrar usuario
    path("registrar/", views.registrar_usuario, name="registrar"),

    # Editar usuario
    path(
        "<int:usuario_id>/editar/",
        views.editar_usuario,
        name="editar",
    ),

    # Cambiar contraseña
    path(
        "<int:usuario_id>/cambiar-password/",
        views.cambiar_password_usuario,
        name="cambiar_password",
    ),

    # Activar o desactivar usuario
    path(
        "<int:usuario_id>/cambiar-estado/",
        views.cambiar_estado_usuario,
        name="cambiar_estado",
    ),

    # Eliminar usuario
    path(
        "<int:usuario_id>/eliminar/",
        views.eliminar_usuario,
        name="eliminar",
    ),
]
