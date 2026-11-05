from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.proveedores.forms import ProveedorForm
from apps.proveedores.models import Proveedor


@login_required
def lista_proveedores(request):
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "activos")

    proveedores = Proveedor.objects.annotate(
        total_compras_registradas=Count("compras")
    ).all()

    if q:
        proveedores = proveedores.filter(
            Q(nombre__icontains=q)
            | Q(nit__icontains=q)
            | Q(persona_contacto__icontains=q)
            | Q(telefono__icontains=q)
        )

    if estado == "activos":
        proveedores = proveedores.filter(activo=True)
    elif estado == "inactivos":
        proveedores = proveedores.filter(activo=False)

    proveedores = proveedores.order_by("nombre")

    total_proveedores = Proveedor.objects.count()
    proveedores_activos = Proveedor.objects.filter(activo=True).count()

    paginator = Paginator(proveedores, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "proveedores/lista.html",
        {
            "page_obj": page_obj,
            "proveedores": page_obj.object_list,
            "q": q,
            "estado": estado,
            "total_proveedores": total_proveedores,
            "proveedores_activos": proveedores_activos,
        },
    )


@login_required
def crear_proveedor(request):
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(
                request,
                f"Proveedor '{proveedor.nombre}' registrado correctamente.",
            )
            return redirect("proveedores:lista")
    else:
        form = ProveedorForm()

    return render(
        request,
        "proveedores/form.html",
        {
            "form": form,
            "titulo": "Nuevo Proveedor",
            "accion": "Guardar Proveedor",
        },
    )


@login_required
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == "POST":
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save()
            messages.success(
                request,
                f"Datos del proveedor '{proveedor.nombre}' actualizados correctamente.",
            )
            return redirect("proveedores:lista")
    else:
        form = ProveedorForm(instance=proveedor)

    return render(
        request,
        "proveedores/form.html",
        {
            "form": form,
            "proveedor": proveedor,
            "titulo": f"Editar: {proveedor.nombre}",
            "accion": "Guardar cambios",
        },
    )


@login_required
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if proveedor.compras.exists():
        proveedor.activo = False
        proveedor.save()
        messages.warning(
            request,
            f"El proveedor '{proveedor.nombre}' tiene compras asociadas en el sistema. Ha sido marcado como inactivo.",
        )
    else:
        nombre = proveedor.nombre
        proveedor.delete()
        messages.success(
            request, f"El proveedor '{nombre}' ha sido eliminado exitosamente."
        )

    return redirect("proveedores:lista")
