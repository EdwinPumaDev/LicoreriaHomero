from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from apps.inventario.models import MovimientoInventario


@login_required
def lista_movimientos(request):
    q = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "").strip()

    movimientos = MovimientoInventario.objects.select_related(
        "producto",
        "usuario",
        "compra",
        "venta",
    ).all()

    # Buscador
    if q:
        movimientos = movimientos.filter(
            Q(producto__nombre__icontains=q)
            | Q(usuario__username__icontains=q)
            | Q(motivo__icontains=q)
            | Q(compra__id__icontains=q)
            | Q(venta__id__icontains=q)
        )

    # Filtro por tipo de movimiento
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)

    movimientos = movimientos.order_by("-fecha", "-id")

    # Indicadores generales
    total_movimientos = MovimientoInventario.objects.count()

    total_entradas = MovimientoInventario.objects.filter(
        tipo__in=[
            MovimientoInventario.Tipo.ENTRADA_COMPRA,
            MovimientoInventario.Tipo.AJUSTE_ENTRADA,
            MovimientoInventario.Tipo.DEVOLUCION,
        ]
    ).count()

    total_salidas = MovimientoInventario.objects.filter(
        tipo__in=[
            MovimientoInventario.Tipo.SALIDA_VENTA,
            MovimientoInventario.Tipo.AJUSTE_SALIDA,
            MovimientoInventario.Tipo.ANULACION,
        ]
    ).count()

    # Paginación
    paginator = Paginator(movimientos, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "inventario/lista.html",
        {
            "page_obj": page_obj,
            "movimientos": page_obj.object_list,
            "q": q,
            "tipo": tipo,
            "tipos": MovimientoInventario.Tipo.choices,
            "total_movimientos": total_movimientos,
            "total_entradas": total_entradas,
            "total_salidas": total_salidas,
        },
    )