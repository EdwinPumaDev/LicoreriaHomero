
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.productos.models import Producto
from apps.ventas.models import Venta
from apps.ventas.forms import VentaForm, DetalleVentaForm
from apps.ventas.services import (
    calcular_totales,
    confirmar_venta,
    anular_venta,
)
from apps.usuarios.permisos import (
    todos_los_cargos,
    administrador_o_encargado,
)


# ==========================================================
# LISTADO DE VENTAS E INDICADORES
# ==========================================================

@login_required
@todos_los_cargos
def lista_ventas(request):

    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "").strip()

    todas_las_ventas = Venta.objects.all()

    indicadores = todas_las_ventas.aggregate(
        total_ventas=Count("id"),

        ventas_confirmadas=Count(
            "id",
            filter=Q(estado=Venta.Estado.CONFIRMADA),
        ),

        ventas_borrador=Count(
            "id",
            filter=Q(estado=Venta.Estado.BORRADOR),
        ),

        ventas_anuladas=Count(
            "id",
            filter=Q(estado=Venta.Estado.ANULADA),
        ),

        total_vendido=Sum(
            "total",
            filter=Q(estado=Venta.Estado.CONFIRMADA),
        ),
    )

    indicadores["total_vendido"] = (
        indicadores["total_vendido"] or Decimal("0.00")
    )

    ventas = Venta.objects.select_related("usuario").all()

    if q:
        ventas = ventas.filter(
            Q(numero__icontains=q)
            | Q(usuario__username__icontains=q)
            | Q(observaciones__icontains=q)
        )

    if estado:
        ventas = ventas.filter(estado=estado)

    ventas = ventas.order_by("-fecha", "-id")

    paginator = Paginator(ventas, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "ventas/lista.html",
        {
            "page_obj": page_obj,
            "ventas": page_obj.object_list,
            "q": q,
            "estado": estado,
            "estados": Venta.Estado.choices,
            "indicadores": indicadores,
        },
    )


# ==========================================================
# CREAR NUEVA VENTA
# ==========================================================

@login_required
@todos_los_cargos
def crear_venta(request):

    if request.method == "POST":

        form = VentaForm(request.POST)

        if form.is_valid():

            venta = form.save(commit=False)
            venta.usuario = request.user

            venta.numero = (
                f"V-{timezone.now():%Y%m%d}-"
                f"{uuid4().hex[:6].upper()}"
            )

            venta.estado = Venta.Estado.BORRADOR
            venta.subtotal = 0
            venta.total = 0

            venta.save()

            return redirect(
                "ventas:detalle",
                pk=venta.pk,
            )

    else:
        form = VentaForm()

    return render(
        request,
        "ventas/crear.html",
        {"form": form},
    )


# ==========================================================
# DETALLE Y REGISTRO DE PRODUCTOS
# ==========================================================

@login_required
@todos_los_cargos
def detalle_venta(request, pk):

    venta = get_object_or_404(
        Venta.objects.select_related("usuario"),
        pk=pk,
    )

    if request.method == "POST":

        form = DetalleVentaForm(request.POST)

        if venta.estado != Venta.Estado.BORRADOR:

            form.add_error(
                None,
                "Esta venta ya no se puede modificar.",
            )

        elif form.is_valid():

            try:
                with transaction.atomic():

                    venta = Venta.objects.select_for_update().get(
                        pk=pk
                    )

                    if venta.estado != Venta.Estado.BORRADOR:
                        raise ValidationError(
                            "La venta ya no se encuentra en estado borrador."
                        )

                    producto = Producto.objects.select_for_update().get(
                        pk=form.cleaned_data["producto"].pk
                    )

                    if not producto.activo:
                        raise ValidationError(
                            "El producto seleccionado ya no está activo."
                        )

                    cantidad = form.cleaned_data["cantidad"]
                    descuento = form.cleaned_data.get(
                        "descuento"
                    ) or Decimal("0.00")

                    precio = producto.precio_venta
                    importe = cantidad * precio

                    if descuento > importe:
                        raise ValidationError(
                            "El descuento no puede superar el importe del producto."
                        )

                    detalle = form.save(commit=False)

                    detalle.venta = venta
                    detalle.producto = producto
                    detalle.precio_unitario = precio
                    detalle.costo_unitario = producto.costo
                    detalle.descuento = descuento
                    detalle.subtotal = importe - descuento

                    detalle.save()

                    calcular_totales(venta)

                return redirect(
                    "ventas:detalle",
                    pk=venta.pk,
                )

            except ValidationError as error:

                for mensaje in error.messages:
                    form.add_error(None, mensaje)

            except Producto.DoesNotExist:

                form.add_error(
                    "producto",
                    "El producto seleccionado ya no existe.",
                )

    else:
        form = DetalleVentaForm()

    detalles = venta.detalles.select_related(
        "producto"
    ).all()

    return render(
        request,
        "ventas/detalle.html",
        {
            "venta": venta,
            "detalles": detalles,
            "form": form,
            "detalle_form": form,
        },
    )


# ==========================================================
# CONFIRMAR VENTA
# ==========================================================

@login_required
@todos_los_cargos
@require_POST
def confirmar_venta_view(request, pk):

    venta = get_object_or_404(
        Venta,
        pk=pk,
    )

    try:
        confirmar_venta(
            venta=venta,
            usuario=request.user,
        )

        return redirect(
            "ventas:detalle",
            pk=venta.pk,
        )

    except ValidationError as error:

        venta.refresh_from_db()

        detalles = venta.detalles.select_related(
            "producto"
        ).all()

        form = DetalleVentaForm()

        return render(
            request,
            "ventas/detalle.html",
            {
                "venta": venta,
                "detalles": detalles,
                "form": form,
                "detalle_form": form,
                "error": " ".join(error.messages),
            },
        )


# ==========================================================
# ANULAR VENTA
# ==========================================================

@login_required
@administrador_o_encargado
@require_POST
def anular_venta_view(request, pk):

    venta = get_object_or_404(
        Venta,
        pk=pk,
    )

    motivo = request.POST.get("motivo", "").strip()

    try:
        anular_venta(
            venta=venta,
            usuario=request.user,
            motivo=motivo,
        )

        return redirect(
            "ventas:detalle",
            pk=venta.pk,
        )

    except ValidationError as error:

        venta.refresh_from_db()

        detalles = venta.detalles.select_related(
            "producto"
        ).all()

        form = DetalleVentaForm()

        return render(
            request,
            "ventas/detalle.html",
            {
                "venta": venta,
                "detalles": detalles,
                "form": form,
                "detalle_form": form,
                "error": " ".join(error.messages),
            },
        )


# ==========================================================
# VISTA PREVIA DEL COMPROBANTE
# ==========================================================

@login_required
@todos_los_cargos
def ver_comprobante(request, pk):

    venta = get_object_or_404(
        Venta.objects.select_related("usuario"),
        pk=pk,
    )

    if venta.estado != Venta.Estado.CONFIRMADA:
        return redirect(
            "ventas:detalle",
            pk=venta.pk,
        )

    detalles = venta.detalles.select_related(
        "producto"
    ).all()

    return render(
        request,
        "ventas/comprobante.html",
        {
            "venta": venta,
            "detalles": detalles,
        },
    )
