
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.productos.models import Producto
from apps.ventas.models import Venta
from apps.usuarios.models import PerfilUsuario
from apps.usuarios.forms import (
    UsuarioCrearForm,
    UsuarioEditarForm,
    UsuarioCambiarPasswordForm,
)


# ==========================================================
# VERIFICAR PERMISOS DE ADMINISTRADOR
# ==========================================================

def es_administrador(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return (
        user.is_staff
        and hasattr(user, "perfil")
        and user.perfil.cargo == PerfilUsuario.Cargo.ADMINISTRADOR
        and user.perfil.activo
    )


# ==========================================================
# LISTA DE USUARIOS
# ==========================================================

@login_required
@user_passes_test(es_administrador)
def lista_usuarios(request):

    usuarios = User.objects.select_related(
        "perfil"
    ).order_by("username")

    contexto = {
        "usuarios": usuarios,
    }

    return render(
        request,
        "usuarios/lista.html",
        contexto,
    )


# ==========================================================
# REGISTRAR USUARIO
# ==========================================================

@login_required
@user_passes_test(es_administrador)
def registrar_usuario(request):

    if request.method == "POST":
        formulario = UsuarioCrearForm(request.POST)

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                "El usuario fue registrado correctamente.",
            )

            return redirect("usuarios:lista")

    else:
        formulario = UsuarioCrearForm()

    return render(
        request,
        "usuarios/registrar.html",
        {"formulario": formulario},
    )


# ==========================================================
# EDITAR USUARIO
# ==========================================================

@login_required
@user_passes_test(es_administrador)
def editar_usuario(request, usuario_id):

    usuario = get_object_or_404(
        User,
        pk=usuario_id,
    )

    if usuario.is_superuser:
        messages.error(
            request,
            "No se puede modificar el superusuario principal.",
        )

        return redirect("usuarios:lista")

    if request.method == "POST":

        formulario = UsuarioEditarForm(
            request.POST,
            instance=usuario,
        )

        if formulario.is_valid():

            formulario.save()

            messages.success(
                request,
                "Los datos del usuario fueron actualizados.",
            )

            return redirect("usuarios:lista")

    else:
        formulario = UsuarioEditarForm(
            instance=usuario,
        )

    return render(
        request,
        "usuarios/editar.html",
        {
            "formulario": formulario,
            "usuario": usuario,
        },
    )


# ==========================================================
# CAMBIAR CONTRASEÑA
# ==========================================================

@login_required
@user_passes_test(es_administrador)
def cambiar_password_usuario(request, usuario_id):

    usuario = get_object_or_404(
        User,
        pk=usuario_id,
    )

    if usuario.is_superuser:
        messages.error(
            request,
            "No se puede modificar la contraseña del superusuario principal desde aquí.",
        )

        return redirect("usuarios:lista")

    if request.method == "POST":

        formulario = UsuarioCambiarPasswordForm(
            request.POST,
        )

        if formulario.is_valid():

            formulario.guardar(usuario)

            messages.success(
                request,
                "La contraseña fue actualizada correctamente.",
            )

            return redirect("usuarios:lista")

    else:
        formulario = UsuarioCambiarPasswordForm()

    return render(
        request,
        "usuarios/cambiar_password.html",
        {
            "formulario": formulario,
            "usuario": usuario,
        },
    )


# ==========================================================
# ACTIVAR Y DESACTIVAR USUARIO
# ==========================================================

@login_required
@user_passes_test(es_administrador)
@require_POST
def cambiar_estado_usuario(request, usuario_id):

    usuario = get_object_or_404(
        User,
        pk=usuario_id,
    )

    if usuario.pk == request.user.pk:
        messages.error(
            request,
            "No puedes desactivar tu propio usuario.",
        )

        return redirect("usuarios:lista")

    if usuario.is_superuser:
        messages.error(
            request,
            "No puedes desactivar al superusuario principal.",
        )

        return redirect("usuarios:lista")

    perfil = PerfilUsuario.objects.filter(
        usuario=usuario
    ).first()

    if perfil is None:
        messages.error(
            request,
            "Este usuario no tiene un perfil registrado.",
        )

        return redirect("usuarios:lista")

    usuario.is_active = not usuario.is_active

    usuario.save(
        update_fields=["is_active"]
    )

    perfil.activo = usuario.is_active

    perfil.save(
        update_fields=["activo"]
    )

    if usuario.is_active:
        messages.success(
            request,
            "Usuario activado correctamente.",
        )
    else:
        messages.success(
            request,
            "Usuario desactivado correctamente.",
        )

    return redirect("usuarios:lista")


# ==========================================================
# ELIMINAR USUARIO CON CONFIRMACIÓN
# ==========================================================

@login_required
@user_passes_test(es_administrador)
def eliminar_usuario(request, usuario_id):

    usuario = get_object_or_404(
        User,
        pk=usuario_id,
    )

    if usuario.pk == request.user.pk:
        messages.error(
            request,
            "No puedes eliminar tu propia cuenta.",
        )

        return redirect("usuarios:lista")

    if usuario.is_superuser:
        messages.error(
            request,
            "No puedes eliminar al superusuario principal.",
        )

        return redirect("usuarios:lista")

    # La eliminación solamente ocurre mediante POST.
    if request.method == "POST":

        nombre_usuario = usuario.username

        try:

            usuario.delete()

            messages.success(
                request,
                f"El usuario {nombre_usuario} fue eliminado correctamente.",
            )

        except ProtectedError:

            messages.error(
                request,
                "No se puede eliminar este usuario porque tiene "
                "ventas, compras u operaciones de caja relacionadas. "
                "Puedes desactivar su cuenta.",
            )

        return redirect("usuarios:lista")

    # Mostrar confirmación antes de eliminar.
    return render(
        request,
        "usuarios/confirmar_eliminar.html",
        {
            "usuario": usuario,
        },
    )


# ==========================================================
# DASHBOARD PRINCIPAL
# ==========================================================

@login_required
def dashboard(request):

    ventas_confirmadas = Venta.objects.filter(
        estado=Venta.Estado.CONFIRMADA
    )

    total_ventas = ventas_confirmadas.count()

    ingresos = ventas_confirmadas.aggregate(
        total=Sum("total")
    )["total"] or 0

    productos_activos = Producto.objects.filter(
        activo=True
    ).count()

    productos_bajo_stock = Producto.objects.filter(
        activo=True,
        stock__lte=F("stock_minimo"),
    ).count()

    ultimas_ventas = ventas_confirmadas.order_by(
        "-fecha"
    )[:5]

    contexto = {
        "total_ventas": total_ventas,
        "ingresos": ingresos,
        "productos_activos": productos_activos,
        "productos_bajo_stock": productos_bajo_stock,
        "ultimas_ventas": ultimas_ventas,
    }

    return render(
        request,
        "usuarios/dashboard.html",
        contexto,
    )
