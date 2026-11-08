
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.auditoria.models import RegistroAuditoria
from apps.usuarios.permisos import solo_administrador


# ==========================================================
# INICIO DE SESIÓN CON AUDITORÍA
# ==========================================================

class LoginAuditoriaView(auth_views.LoginView):

    def form_valid(self, form):
        respuesta = super().form_valid(form)

        usuario = form.get_user()

        RegistroAuditoria.objects.create(
            usuario=usuario,
            tipo_accion=RegistroAuditoria.TipoAccion.INICIO_SESION,
            modulo="Autenticación",
            descripcion=f"El usuario {usuario.username} inició sesión.",
            direccion_ip=self.obtener_ip(),
        )

        return respuesta

    def obtener_ip(self):
        x_forwarded_for = self.request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        return self.request.META.get("REMOTE_ADDR")


# ==========================================================
# CIERRE DE SESIÓN CON AUDITORÍA
# ==========================================================

class LogoutAuditoriaView(auth_views.LogoutView):

    def post(self, request, *args, **kwargs):
        usuario = request.user

        if usuario.is_authenticated:

            x_forwarded_for = request.META.get(
                "HTTP_X_FORWARDED_FOR"
            )

            if x_forwarded_for:
                direccion_ip = x_forwarded_for.split(",")[0].strip()
            else:
                direccion_ip = request.META.get("REMOTE_ADDR")

            RegistroAuditoria.objects.create(
                usuario=usuario,
                tipo_accion=RegistroAuditoria.TipoAccion.CIERRE_SESION,
                modulo="Autenticación",
                descripcion=f"El usuario {usuario.username} cerró sesión.",
                direccion_ip=direccion_ip,
            )

        return super().post(request, *args, **kwargs)


# ==========================================================
# HISTORIAL DE AUDITORÍA
# ==========================================================

@login_required
@solo_administrador
def lista_auditoria(request):

    registros = (
        RegistroAuditoria.objects
        .select_related("usuario")
        .order_by("-fecha_hora")
    )

    contexto = {
        "registros": registros,
        "total_registros": registros.count(),
    }

    return render(
        request,
        "auditoria/lista.html",
        contexto,
    )
