from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.usuarios.views import dashboard
from apps.auditoria.views import LoginAuditoriaView, LogoutAuditoriaView


urlpatterns = [
    path("admin/", admin.site.urls),

    # PÁGINA PÚBLICA
    path("", include("apps.publico.urls")),

    # ACCESO ADMINISTRATIVO
    path(
        "acceso/",
        LoginAuditoriaView.as_view(
            template_name="usuarios/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    path("dashboard/", dashboard, name="dashboard"),

    # MÓDULOS ADMINISTRATIVOS
    path("usuarios/", include("apps.usuarios.urls")),
    path("productos/", include("apps.productos.urls")),
    path("proveedores/", include("apps.proveedores.urls")),
    path("compras/", include("apps.compras.urls")),
    path("inventario/", include("apps.inventario.urls")),
    path("ventas/", include("apps.ventas.urls")),
    path("caja/", include("apps.caja.urls")),
    path("reportes/", include("apps.reportes.urls")),
    path("auditoria/", include("apps.auditoria.urls")),

    path(
        "personalizacion/",
        include("apps.configuracion.urls"),
    ),

    path(
        "cerrar-sesion/",
        LogoutAuditoriaView.as_view(),
        name="logout",
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )