
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render

from apps.caja.models import IngresoCaja
from apps.usuarios.permisos import (
    todos_los_cargos,
    es_vendedor,
)


@login_required
@todos_los_cargos
def lista_ingresos(request):

    ingresos = IngresoCaja.objects.select_related(
        "venta",
        "usuario",
    ).all()

    # Los vendedores solamente pueden consultar sus propios ingresos.
    if es_vendedor(request.user):
        ingresos = ingresos.filter(usuario=request.user)

    # Filtros
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")
    metodo_pago = request.GET.get("metodo_pago", "")

    if fecha_inicio:
        try:
            datetime.strptime(fecha_inicio, "%Y-%m-%d")
            ingresos = ingresos.filter(fecha__date__gte=fecha_inicio)
        except ValueError:
            fecha_inicio = ""

    if fecha_fin:
        try:
            datetime.strptime(fecha_fin, "%Y-%m-%d")
            ingresos = ingresos.filter(fecha__date__lte=fecha_fin)
        except ValueError:
            fecha_fin = ""

    if metodo_pago:
        ingresos = ingresos.filter(metodo_pago=metodo_pago)

    # Separar ingresos válidos de los anulados.
    ingresos_validos = ingresos.filter(anulado=False)
    ingresos_anulados = ingresos.filter(anulado=True)

    # Indicadores: solamente ingresos válidos.
    resumen = ingresos_validos.aggregate(
        total_ingresos=Sum("monto"),
        cantidad_ingresos=Count("id"),
    )

    contexto = {
        "ingresos": ingresos,
        "total_ingresos": (
            resumen["total_ingresos"] or Decimal("0.00")
        ),
        "cantidad_ingresos": resumen["cantidad_ingresos"],
        "cantidad_anulados": ingresos_anulados.count(),
        "cantidad_registros": ingresos.count(),
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "metodo_pago": metodo_pago,
        "metodos_pago": IngresoCaja.MetodoPago.choices,
    }

    return render(
        request,
        "caja/lista_ingresos.html",
        contexto,
    )
