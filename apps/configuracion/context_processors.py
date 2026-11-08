
from apps.configuracion.models import ConfiguracionSistema


def configuracion_global(request):
    configuracion = ConfiguracionSistema.objects.filter(pk=1).first()

    return {
        "configuracion_sistema": configuracion,
    }
