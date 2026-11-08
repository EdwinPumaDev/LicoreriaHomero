from decimal import Decimal

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.productos.models import Producto, Categoria


def inicio(request):
    productos = (
        Producto.objects
        .filter(activo=True, stock__gt=0)
        .select_related("categoria", "marca")
        .order_by("nombre")[:8]
    )

    categorias = Categoria.objects.filter(
        activo=True,
        productos__activo=True,
        productos__stock__gt=0,
    ).distinct().order_by("nombre")

    contexto = {
        "productos": productos,
        "categorias": categorias,
    }

    return render(request, "publico/inicio.html", contexto)


def catalogo(request):
    productos = (
        Producto.objects
        .filter(activo=True, stock__gt=0)
        .select_related("categoria", "marca")
        .order_by("nombre")
    )

    categorias = Categoria.objects.filter(
        activo=True,
        productos__activo=True,
        productos__stock__gt=0,
    ).distinct().order_by("nombre")

    busqueda = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "").strip()

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    if categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))

    contexto = {
        "productos": productos,
        "categorias": categorias,
        "busqueda": busqueda,
        "categoria_seleccionada": categoria_id,
    }

    return render(request, "publico/catalogo.html", contexto)


@require_POST
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(
        Producto,
        id=producto_id,
        activo=True,
    )

    if producto.stock <= 0:
        messages.error(request, "Este producto no tiene stock disponible.")
        return redirect("publico:catalogo")

    carrito = request.session.get("carrito", {})
    producto_id_str = str(producto.id)

    cantidad_actual = int(carrito.get(producto_id_str, 0))

    if cantidad_actual + 1 > producto.stock:
        messages.warning(
            request,
            "No puedes agregar más unidades que el stock disponible."
        )
    else:
        carrito[producto_id_str] = cantidad_actual + 1
        request.session["carrito"] = carrito
        request.session.modified = True

        messages.success(
            request,
            f"{producto.nombre} se agregó al carrito."
        )

    return redirect(request.META.get("HTTP_REFERER", "publico:catalogo"))


def ver_carrito(request):
    carrito = request.session.get("carrito", {})
    productos_carrito = []
    total = Decimal("0.00")

    for producto_id, cantidad in carrito.items():
        producto = Producto.objects.filter(
            id=producto_id,
            activo=True,
        ).first()

        if producto is None or producto.stock <= 0:
            continue

        cantidad = int(cantidad)

        if cantidad > producto.stock:
            cantidad = producto.stock

        if cantidad <= 0:
            continue

        subtotal = producto.precio_venta * cantidad
        total += subtotal

        productos_carrito.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": subtotal,
        })

    contexto = {
        "productos_carrito": productos_carrito,
        "total": total,
        "cantidad_total": sum(item["cantidad"] for item in productos_carrito),
    }

    return render(request, "publico/carrito.html", contexto)


@require_POST
def actualizar_carrito(request, producto_id):
    carrito = request.session.get("carrito", {})
    producto_id_str = str(producto_id)

    if producto_id_str not in carrito:
        return redirect("publico:carrito")

    try:
        cantidad = int(request.POST.get("cantidad", 1))
    except (TypeError, ValueError):
        messages.error(request, "La cantidad ingresada no es válida.")
        return redirect("publico:carrito")

    producto = Producto.objects.filter(
        id=producto_id,
        activo=True,
    ).first()

    if producto is None or producto.stock <= 0:
        carrito.pop(producto_id_str, None)
        request.session["carrito"] = carrito
        request.session.modified = True

        messages.warning(request, "El producto ya no está disponible.")
        return redirect("publico:carrito")

    if cantidad <= 0:
        carrito.pop(producto_id_str, None)
        messages.info(request, "Producto eliminado del carrito.")

    elif cantidad > producto.stock:
        messages.warning(
            request,
            f"Solo hay {producto.stock} unidades disponibles."
        )
    else:
        carrito[producto_id_str] = cantidad
        messages.success(request, "Cantidad actualizada.")

    request.session["carrito"] = carrito
    request.session.modified = True

    return redirect("publico:carrito")


@require_POST
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get("carrito", {})
    producto_id_str = str(producto_id)

    if producto_id_str in carrito:
        carrito.pop(producto_id_str)
        request.session["carrito"] = carrito
        request.session.modified = True

        messages.success(request, "Producto eliminado del carrito.")

    return redirect("publico:carrito")