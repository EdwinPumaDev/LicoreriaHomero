
from decimal import Decimal
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods

from apps.productos.models import Producto, Categoria
from apps.publico.models import Pedido, DetallePedido

from apps.ventas.models import Venta, DetalleVenta
from apps.ventas.services import confirmar_venta

from apps.usuarios.permisos import todos_los_cargos


# ==========================================================
# PÁGINA DE INICIO
# ==========================================================

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


# ==========================================================
# CATÁLOGO PÚBLICO
# ==========================================================

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
        productos = productos.filter(
            categoria_id=int(categoria_id)
        )

    contexto = {
        "productos": productos,
        "categorias": categorias,
        "busqueda": busqueda,
        "categoria_seleccionada": categoria_id,
    }

    return render(
        request,
        "publico/catalogo.html",
        contexto,
    )


# ==========================================================
# AGREGAR PRODUCTOS AL CARRITO
# ==========================================================

@require_POST
def agregar_carrito(request, producto_id):

    producto = get_object_or_404(
        Producto,
        id=producto_id,
        activo=True,
    )

    if producto.stock <= 0:
        messages.error(
            request,
            "Este producto no tiene stock disponible."
        )
        return redirect("publico:catalogo")

    carrito = request.session.get("carrito", {})
    producto_id_str = str(producto.id)

    cantidad_actual = int(
        carrito.get(producto_id_str, 0)
    )

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

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "publico:catalogo"
        )
    )


# ==========================================================
# VER CARRITO
# ==========================================================

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
        "cantidad_total": sum(
            item["cantidad"]
            for item in productos_carrito
        ),
    }

    return render(
        request,
        "publico/carrito.html",
        contexto,
    )


# ==========================================================
# ACTUALIZAR CANTIDAD DEL CARRITO
# ==========================================================

@require_POST
def actualizar_carrito(request, producto_id):

    carrito = request.session.get("carrito", {})
    producto_id_str = str(producto_id)

    if producto_id_str not in carrito:
        return redirect("publico:carrito")

    try:
        cantidad = int(
            request.POST.get("cantidad", 1)
        )

    except (TypeError, ValueError):

        messages.error(
            request,
            "La cantidad ingresada no es válida."
        )

        return redirect("publico:carrito")

    producto = Producto.objects.filter(
        id=producto_id,
        activo=True,
    ).first()

    if producto is None or producto.stock <= 0:

        carrito.pop(producto_id_str, None)

        request.session["carrito"] = carrito
        request.session.modified = True

        messages.warning(
            request,
            "El producto ya no está disponible."
        )

        return redirect("publico:carrito")

    if cantidad <= 0:

        carrito.pop(producto_id_str, None)

        messages.info(
            request,
            "Producto eliminado del carrito."
        )

    elif cantidad > producto.stock:

        messages.warning(
            request,
            f"Solo hay {producto.stock} unidades disponibles."
        )

    else:

        carrito[producto_id_str] = cantidad

        messages.success(
            request,
            "Cantidad actualizada."
        )

    request.session["carrito"] = carrito
    request.session.modified = True

    return redirect("publico:carrito")


# ==========================================================
# ELIMINAR PRODUCTO DEL CARRITO
# ==========================================================

@require_POST
def eliminar_del_carrito(request, producto_id):

    carrito = request.session.get("carrito", {})
    producto_id_str = str(producto_id)

    if producto_id_str in carrito:

        carrito.pop(producto_id_str)

        request.session["carrito"] = carrito
        request.session.modified = True

        messages.success(
            request,
            "Producto eliminado del carrito."
        )

    return redirect("publico:carrito")


# ==========================================================
# REGISTRAR PEDIDO DEL CLIENTE
# ==========================================================

@require_http_methods(["GET", "POST"])
def crear_pedido(request):

    carrito = request.session.get("carrito", {})

    if not carrito:

        messages.warning(
            request,
            "Tu carrito está vacío."
        )

        return redirect("publico:catalogo")

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

    if not productos_carrito:

        messages.warning(
            request,
            "Los productos de tu carrito ya no están disponibles."
        )

        request.session["carrito"] = {}
        request.session.modified = True

        return redirect("publico:catalogo")

    if request.method == "POST":

        nombre = request.POST.get(
            "nombre_cliente", ""
        ).strip()

        telefono = request.POST.get(
            "telefono", ""
        ).strip()

        direccion = request.POST.get(
            "direccion", ""
        ).strip()

        observaciones = request.POST.get(
            "observaciones", ""
        ).strip()

        if not nombre or not telefono or not direccion:

            messages.error(
                request,
                "Completa tu nombre, teléfono y dirección."
            )

        else:

            try:

                with transaction.atomic():

                    ids_productos = [
                        int(producto_id)
                        for producto_id in carrito.keys()
                    ]

                    productos_bloqueados = (
                        Producto.objects
                        .select_for_update()
                        .filter(
                            id__in=ids_productos,
                            activo=True,
                        )
                    )

                    productos_por_id = {
                        producto.id: producto
                        for producto in productos_bloqueados
                    }

                    if len(productos_por_id) != len(ids_productos):

                        raise ValueError(
                            "Uno de los productos ya no está disponible."
                        )

                    detalles_pedido = []
                    total_pedido = Decimal("0.00")

                    for producto_id, cantidad in carrito.items():

                        producto = productos_por_id.get(
                            int(producto_id)
                        )

                        cantidad = int(cantidad)

                        if producto is None or cantidad <= 0:

                            raise ValueError(
                                "Hay un producto inválido en el carrito."
                            )

                        if cantidad > producto.stock:

                            raise ValueError(
                                f"Stock insuficiente para {producto.nombre}. "
                                f"Disponibles: {producto.stock}."
                            )

                        precio = producto.precio_venta
                        subtotal = precio * cantidad

                        total_pedido += subtotal

                        detalles_pedido.append({
                            "producto": producto,
                            "cantidad": cantidad,
                            "precio": precio,
                            "subtotal": subtotal,
                        })

                    pedido = Pedido.objects.create(
                        nombre_cliente=nombre,
                        telefono=telefono,
                        direccion=direccion,
                        observaciones=observaciones,
                        total=total_pedido,
                    )

                    for detalle in detalles_pedido:

                        DetallePedido.objects.create(
                            pedido=pedido,
                            producto=detalle["producto"],
                            cantidad=detalle["cantidad"],
                            precio_unitario=detalle["precio"],
                            subtotal=detalle["subtotal"],
                        )

                request.session["carrito"] = {}
                request.session.modified = True

                return render(
                    request,
                    "publico/pedido_confirmado.html",
                    {"pedido": pedido},
                )

            except ValueError as error:

                messages.error(
                    request,
                    str(error)
                )

    contexto = {
        "productos_carrito": productos_carrito,
        "total": total,
        "cantidad_total": sum(
            item["cantidad"]
            for item in productos_carrito
        ),
        "nombre_cliente": request.POST.get(
            "nombre_cliente", ""
        ),
        "telefono": request.POST.get(
            "telefono", ""
        ),
        "direccion": request.POST.get(
            "direccion", ""
        ),
        "observaciones": request.POST.get(
            "observaciones", ""
        ),
    }

    return render(
        request,
        "publico/pedido.html",
        contexto,
    )


# ==========================================================
# LISTADO ADMINISTRATIVO DE PEDIDOS
# ==========================================================

@login_required
@todos_los_cargos
def lista_pedidos(request):

    pedidos = (
        Pedido.objects
        .prefetch_related("detalles__producto")
        .select_related("venta")
        .order_by("-creado_en")
    )

    contexto = {
        "pedidos": pedidos,
        "total_pedidos": pedidos.count(),

        "pedidos_pendientes": pedidos.filter(
            estado=Pedido.Estado.PENDIENTE
        ).count(),

        "pedidos_aceptados": pedidos.filter(
            estado=Pedido.Estado.ACEPTADO
        ).count(),

        "pedidos_rechazados": pedidos.filter(
            estado=Pedido.Estado.RECHAZADO
        ).count(),
    }

    return render(
        request,
        "publico/gestion_pedidos.html",
        contexto,
    )


# ==========================================================
# ACEPTAR PEDIDO Y CONVERTIRLO EN VENTA
# ==========================================================

@login_required
@todos_los_cargos
@require_POST
def aceptar_pedido(request, pk):

    metodo_pago = request.POST.get(
        "metodo_pago", ""
    ).strip()

    metodos_validos = dict(
        Venta.MetodoPago.choices
    )

    if metodo_pago not in metodos_validos:

        messages.error(
            request,
            "Selecciona un método de pago válido."
        )

        return redirect("publico:lista_pedidos")

    try:

        with transaction.atomic():

            pedido = get_object_or_404(
                Pedido.objects.select_for_update(),
                pk=pk,
            )

            if pedido.estado != Pedido.Estado.PENDIENTE:

                raise ValidationError(
                    "Solo se pueden aceptar pedidos pendientes."
                )

            if pedido.venta_id is not None:

                raise ValidationError(
                    "Este pedido ya tiene una venta asociada."
                )

            detalles_pedido = list(
                pedido.detalles
                .select_related("producto")
                .all()
            )

            if not detalles_pedido:

                raise ValidationError(
                    "El pedido no contiene productos."
                )

            numero_venta = (
                f"V-{timezone.now():%Y%m%d}-"
                f"{uuid4().hex[:6].upper()}"
            )

            venta = Venta.objects.create(
                usuario=request.user,
                numero=numero_venta,
                metodo_pago=metodo_pago,
                estado=Venta.Estado.BORRADOR,
                subtotal=Decimal("0.00"),
                descuento=Decimal("0.00"),
                total=Decimal("0.00"),
                observaciones=(
                    f"Venta generada desde el pedido público #{pedido.pk}. "
                    f"Cliente: {pedido.nombre_cliente}. "
                    f"Teléfono: {pedido.telefono}. "
                    f"Dirección: {pedido.direccion}."
                ),
            )

            for detalle in detalles_pedido:

                producto = detalle.producto

                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=detalle.cantidad,
                    precio_unitario=detalle.precio_unitario,
                    costo_unitario=producto.costo,
                    descuento=Decimal("0.00"),
                    subtotal=(
                        detalle.precio_unitario
                        * detalle.cantidad
                    ),
                )

            # Reutilizar el servicio existente.
            # Este servicio calcula totales, descuenta stock
            # y registra el ingreso correspondiente en caja.

            confirmar_venta(
                venta=venta,
                usuario=request.user,
            )

            pedido.venta = venta
            pedido.estado = Pedido.Estado.ACEPTADO

            pedido.save(
                update_fields=[
                    "venta",
                    "estado",
                    "actualizado_en",
                ]
            )

        messages.success(
            request,
            f"El pedido #{pedido.pk} fue aceptado y convertido "
            f"en la venta {venta.numero}."
        )

    except ValidationError as error:

        messages.error(
            request,
            "No se pudo aceptar el pedido: "
            + " ".join(error.messages)
        )

    return redirect("publico:lista_pedidos")


# ==========================================================
# RECHAZAR PEDIDO
# ==========================================================

@login_required
@todos_los_cargos
@require_POST
def rechazar_pedido(request, pk):

    try:

        with transaction.atomic():

            pedido = get_object_or_404(
                Pedido.objects.select_for_update(),
                pk=pk,
            )

            if pedido.estado != Pedido.Estado.PENDIENTE:

                raise ValidationError(
                    "Solo se pueden rechazar pedidos pendientes."
                )

            if pedido.venta_id is not None:

                raise ValidationError(
                    "Este pedido ya tiene una venta asociada."
                )

            pedido.estado = Pedido.Estado.RECHAZADO

            pedido.save(
                update_fields=[
                    "estado",
                    "actualizado_en",
                ]
            )

        messages.success(
            request,
            f"El pedido #{pedido.pk} fue rechazado."
        )

    except ValidationError as error:

        messages.error(
            request,
            "No se pudo rechazar el pedido: "
            + " ".join(error.messages)
        )

    return redirect("publico:lista_pedidos")
