from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from apps.configuracion.models import ConfiguracionSistema
from apps.configuracion.forms import ConfiguracionSistemaForm
from apps.usuarios.permisos import solo_administrador


@login_required
@solo_administrador
def personalizacion(request):

    configuracion, creada = ConfiguracionSistema.objects.get_or_create(
        pk=1,
        defaults={
            "nombre_comercial": "Licorería Homero",
            "nombre_sistema": "Licorería Homero",
        }
    )

    if request.method == "POST":
        formulario = ConfiguracionSistemaForm(
            request.POST,
            request.FILES,
            instance=configuracion
        )

        if formulario.is_valid():
            formulario.save()
            messages.success(
                request,
                "La personalización del sistema se guardó correctamente."
            )
            return redirect("configuracion:personalizacion")

        messages.error(
            request,
            "No se pudieron guardar los cambios. Revisa los campos."
        )

    else:
        formulario = ConfiguracionSistemaForm(instance=configuracion)

    contexto = {
        "formulario": formulario,
        "configuracion": configuracion,
    }

    return render(
        request,
        "configuracion/personalizacion.html",
        contexto
    )