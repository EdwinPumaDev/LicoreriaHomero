
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect

from apps.inventario.models import MovimientoInventario
from apps.inventario.forms import AjusteInventarioForm
from apps.inventario.services import registrar_ajuste
from apps.usuarios.permisos import (
    todos_los_cargos,
    administrador_o_encargado,
)


@login_required
@todos_los_cargos
def lista_movimientos(request):
    q = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "").strip()

    movimientos = MovimientoInventario.objects.select_related(
        "producto",
        "usuario",
        "compra",
        "venta",
    ).all()

    if q:
        movimientos = movimientos.filter(
            Q(producto__nombre__icontains=q)
            | Q(usuario__username__icontains=q)
            | Q(motivo__icontains=q)
            | Q(compra__id__icontains=q)
            | Q(venta__id__icontains=q)
        )

    if tipo:
        movimientos = movimientos.filter(tipo=tipo)

    movimientos = movimientos.order_by("-fecha", "-id")

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

    paginator = Paginator(movimientos, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

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


@login_required
@administrador_o_encargado
def crear_ajuste(request):
    if request.method == "POST":
        form = AjusteInventarioForm(request.POST)

        if form.is_valid():
            try:
                registrar_ajuste(
                    producto_id=form.cleaned_data["producto"].pk,
                    usuario=request.user,
                    cantidad=form.cleaned_data["cantidad"],
                    tipo=form.cleaned_data["tipo"],
                    motivo=form.cleaned_data["motivo"],
                )

                return redirect("inventario:lista")

            except ValidationError as error:
                for mensaje in error.messages:
                    form.add_error(None, mensaje)

    else:
        form = AjusteInventarioForm()

    return render(
        request,
        "inventario/ajuste.html",
        {"form": form},
    )
