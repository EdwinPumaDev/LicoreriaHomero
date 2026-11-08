
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.compras.forms import CompraForm
from apps.compras.models import Compra, DetalleCompra
from apps.compras.services import anular_compra, confirmar_compra
from apps.productos.models import Producto
from apps.proveedores.models import Proveedor
from apps.usuarios.permisos import administrador_o_encargado


@login_required
@administrador_o_encargado
def lista_compras(request):
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "")
    proveedor_id = request.GET.get("proveedor", "")

    compras = Compra.objects.select_related("proveedor", "usuario").all()

    if q:
        compras = compras.filter(
            Q(numero_comprobante__icontains=q)
            | Q(proveedor__nombre__icontains=q)
            | Q(id__icontains=q)
        )

    if estado:
        compras = compras.filter(estado=estado)

    if proveedor_id:
        compras = compras.filter(proveedor_id=proveedor_id)

    compras = compras.order_by("-fecha")

    # KPIs
    compras_confirmadas = Compra.objects.filter(
        estado=Compra.Estado.CONFIRMADA
    )

    total_invertido = (
        compras_confirmadas.aggregate(total=Sum("total"))["total"]
        or Decimal("0.00")
    )

    total_confirmadas = compras_confirmadas.count()

    total_borradores = Compra.objects.filter(
        estado=Compra.Estado.BORRADOR
    ).count()

    paginator = Paginator(compras, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    proveedores = Proveedor.objects.filter(
        activo=True
    ).order_by("nombre")

    return render(
        request,
        "compras/lista.html",
        {
            "page_obj": page_obj,
            "compras": page_obj.object_list,
            "proveedores": proveedores,
            "q": q,
            "estado": estado,
            "proveedor_id": proveedor_id,
            "total_invertido": total_invertido,
            "total_confirmadas": total_confirmadas,
            "total_borradores": total_borradores,
            "estados": Compra.Estado.choices,
        },
    )


@login_required
@administrador_o_encargado
def crear_compra(request):
    productos = Producto.objects.filter(
        activo=True
    ).order_by("nombre")

    proveedores = Proveedor.objects.filter(
        activo=True
    ).order_by("nombre")

    if request.method == "POST":
        form = CompraForm(request.POST)
        producto_ids = request.POST.getlist("producto_id[]")
        cantidades = request.POST.getlist("cantidad[]")
        costos = request.POST.getlist("costo_unitario[]")
        accion = request.POST.get("accion", "borrador")

        if form.is_valid():
            # Validar que haya al menos una línea con datos válidos
            lineas_validas = []
            total_calculado = Decimal("0.00")

            for prod_id, cant_str, costo_str in zip(
                producto_ids, cantidades, costos
            ):
                if not prod_id:
                    continue

                try:
                    cant = int(cant_str)
                    costo = Decimal(costo_str)

                    if cant > 0 and costo >= 0:
                        subtotal = cant * costo
                        total_calculado += subtotal

                        lineas_validas.append(
                            {
                                "producto_id": prod_id,
                                "cantidad": cant,
                                "costo_unitario": costo,
                                "subtotal": subtotal,
                            }
                        )

                except (ValueError, TypeError):
                    continue

            if not lineas_validas:
                messages.error(
                    request,
                    "Debes agregar al menos un producto con cantidad "
                    "mayor a 0 para registrar la compra.",
                )
            else:
                with transaction.atomic():
                    compra = form.save(commit=False)
                    compra.usuario = request.user
                    compra.total = total_calculado
                    compra.estado = Compra.Estado.BORRADOR
                    compra.save()

                    # Guardar detalles
                    for linea in lineas_validas:
                        DetalleCompra.objects.create(
                            compra=compra,
                            producto_id=linea["producto_id"],
                            cantidad=linea["cantidad"],
                            costo_unitario=linea["costo_unitario"],
                            subtotal=linea["subtotal"],
                        )

                # Si el usuario solicitó confirmar inmediatamente
                if accion == "confirmar":
                    ok, msg = confirmar_compra(compra, request.user)

                    if ok:
                        messages.success(request, msg)
                    else:
                        messages.warning(
                            request,
                            f"Compra guardada como borrador: {msg}",
                        )
                else:
                    messages.success(
                        request,
                        f"Compra #{compra.id} guardada como borrador con éxito.",
                    )

                return redirect("compras:detalle", pk=compra.pk)

    else:
        form = CompraForm()

    return render(
        request,
        "compras/form.html",
        {
            "form": form,
            "productos": productos,
            "proveedores": proveedores,
        },
    )


@login_required
@administrador_o_encargado
def detalle_compra(request, pk):
    compra = get_object_or_404(
        Compra.objects.select_related(
            "proveedor",
            "usuario",
        ).prefetch_related(
            "detalles__producto"
        ),
        pk=pk,
    )

    return render(
        request,
        "compras/detalle.html",
        {"compra": compra},
    )


@login_required
@administrador_o_encargado
@require_POST
def confirmar_compra_view(request, pk):
    compra = get_object_or_404(Compra, pk=pk)

    ok, msg = confirmar_compra(compra, request.user)

    if ok:
        messages.success(request, msg)
    else:
        messages.error(request, msg)

    return redirect("compras:detalle", pk=pk)


@login_required
@administrador_o_encargado
@require_POST
def anular_compra_view(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    motivo = request.POST.get("motivo", "").strip()

    ok, msg = anular_compra(compra, request.user, motivo)

    if ok:
        messages.warning(request, msg)
    else:
        messages.error(request, msg)

    return redirect("compras:detalle", pk=pk)
