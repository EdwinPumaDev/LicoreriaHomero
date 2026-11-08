
from functools import wraps

from django.core.exceptions import PermissionDenied

from apps.usuarios.models import PerfilUsuario


# ==========================================================
# OBTENER Y VALIDAR EL CARGO DEL USUARIO
# ==========================================================

def obtener_cargo(usuario):

    if not usuario.is_authenticated:
        return None

    # El superusuario principal tiene acceso total.
    if usuario.is_superuser:
        return PerfilUsuario.Cargo.ADMINISTRADOR

    perfil = getattr(usuario, "perfil", None)

    if perfil is None or not perfil.activo:
        return None

    if not usuario.is_active:
        return None

    return perfil.cargo


# ==========================================================
# COMPROBAR SI ES ADMINISTRADOR
# ==========================================================

def es_administrador(usuario):

    return (
        usuario.is_authenticated
        and (
            usuario.is_superuser
            or (
                usuario.is_active
                and usuario.is_staff
                and obtener_cargo(usuario)
                == PerfilUsuario.Cargo.ADMINISTRADOR
            )
        )
    )


# ==========================================================
# COMPROBAR SI ES ENCARGADO
# ==========================================================

def es_encargado(usuario):

    return (
        usuario.is_authenticated
        and usuario.is_active
        and obtener_cargo(usuario)
        == PerfilUsuario.Cargo.ENCARGADO
    )


# ==========================================================
# COMPROBAR SI ES VENDEDOR
# ==========================================================

def es_vendedor(usuario):

    return (
        usuario.is_authenticated
        and usuario.is_active
        and obtener_cargo(usuario)
        == PerfilUsuario.Cargo.VENDEDOR
    )


# ==========================================================
# DECORADOR PARA CONTROLAR EL ACCESO POR CARGO
# ==========================================================

def requiere_cargo(*cargos_permitidos):

    def decorador(vista):

        @wraps(vista)
        def envoltura(request, *args, **kwargs):

            usuario = request.user

            if not usuario.is_authenticated:
                raise PermissionDenied(
                    "Debes iniciar sesión para acceder."
                )

            # El administrador principal siempre tiene acceso.
            if usuario.is_superuser:
                return vista(request, *args, **kwargs)

            if not usuario.is_active:
                raise PermissionDenied(
                    "Tu cuenta se encuentra desactivada."
                )

            cargo = obtener_cargo(usuario)

            if cargo not in cargos_permitidos:
                raise PermissionDenied(
                    "No tienes permisos para acceder a este módulo."
                )

            return vista(request, *args, **kwargs)

        return envoltura

    return decorador


# ==========================================================
# ACCESO EXCLUSIVO PARA ADMINISTRADORES
# ==========================================================

def solo_administrador(vista):

    return requiere_cargo(
        PerfilUsuario.Cargo.ADMINISTRADOR
    )(vista)


# ==========================================================
# ACCESO PARA ADMINISTRADORES Y ENCARGADOS
# ==========================================================

def administrador_o_encargado(vista):

    return requiere_cargo(
        PerfilUsuario.Cargo.ADMINISTRADOR,
        PerfilUsuario.Cargo.ENCARGADO,
    )(vista)


# ==========================================================
# ACCESO PARA LOS TRES CARGOS
# ==========================================================

def todos_los_cargos(vista):

    return requiere_cargo(
        PerfilUsuario.Cargo.ADMINISTRADOR,
        PerfilUsuario.Cargo.ENCARGADO,
        PerfilUsuario.Cargo.VENDEDOR,
    )(vista)
