
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from apps.usuarios.views import dashboard


urlpatterns = [
    path("admin/", admin.site.urls),

    # Inicio de sesión
    path(
        "",
        auth_views.LoginView.as_view(
            template_name="usuarios/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    # Panel principal protegido
    path("dashboard/", dashboard, name="dashboard"),

    # Cerrar sesión
    path(
        "cerrar-sesion/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
