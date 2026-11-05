
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.productos.forms import CategoriaForm, MarcaForm, ProductoForm
from apps.productos.models import Categoria, Marca, Producto


@login_required
def lista_productos(request):
    q = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "")
    marca_id = request.GET.get("marca", "")
    solo_stock_bajo = request.GET.get("stock_bajo", "") == "1"
    estado = request.GET.get("estado", "activos")

    productos = Producto.objects.select_related(
        "categoria", "marca"
    ).all()

    if q:
        productos = productos.filter(
            Q(nombre__icontains=q)
            | Q(codigo__icontains=q)
            | Q(codigo_barras__icontains=q)
        )

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if marca_id:
        productos = productos.filter(marca_id=marca_id)

    if solo_stock_bajo:
        productos = productos.filter(
            stock__lte=F("stock_minimo")
        )

    if estado == "activos":
        productos = productos.filter(activo=True)
    elif estado == "inactivos":
        productos = productos.filter(activo=False)

    productos = productos.order_by("nombre")

    total_catalogo = Producto.objects.filter(
        activo=True
    ).count()

    total_bajo_stock = Producto.objects.filter(
        activo=True,
        stock__lte=F("stock_minimo")
    ).count()

    valor_inventario = (
        Producto.objects.filter(activo=True).aggregate(
            total=Sum(F("costo") * F("stock"))
        )["total"]
        or Decimal("0.00")
    )

    paginator = Paginator(productos, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    categorias = Categoria.objects.filter(activo=True)
    marcas = Marca.objects.filter(activo=True)

    contexto = {
        "page_obj": page_obj,
        "productos": page_obj.object_list,
        "categorias": categorias,
        "marcas": marcas,
        "q": q,
        "categoria_id": categoria_id,
        "marca_id": marca_id,
        "solo_stock_bajo": solo_stock_bajo,
        "estado": estado,
        "total_catalogo": total_catalogo,
        "total_bajo_stock": total_bajo_stock,
        "valor_inventario": valor_inventario,
    }

    return render(request, "productos/lista.html", contexto)


@login_required
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)

        if form.is_valid():
            producto = form.save()

            messages.success(
                request,
                f"El producto '{producto.nombre}' ha sido registrado exitosamente."
            )

            return redirect("productos:lista")

    else:
        form = ProductoForm()

    return render(
        request,
        "productos/form.html",
        {
            "form": form,
            "titulo": "Nuevo Producto",
            "accion": "Crear",
        }
    )


@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        form = ProductoForm(
            request.POST,
            request.FILES,
            instance=producto
        )

        if form.is_valid():
            producto = form.save()

            messages.success(
                request,
                f"El producto '{producto.nombre}' ha sido actualizado correctamente."
            )

            return redirect("productos:lista")

    else:
        form = ProductoForm(instance=producto)

    return render(
        request,
        "productos/form.html",
        {
            "form": form,
            "producto": producto,
            "titulo": f"Editar: {producto.nombre}",
            "accion": "Guardar cambios",
        }
    )


@login_required
@require_POST
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    tiene_ventas = producto.detalles_venta.exists()
    tiene_compras = producto.detalles_compra.exists()

    if tiene_ventas or tiene_compras:
        producto.activo = False
        producto.save()

        messages.warning(
            request,
            f"El producto '{producto.nombre}' tiene historial de ventas o compras. "
            "Se ha desactivado para conservar los registros históricos."
        )
    else:
        nombre = producto.nombre
        producto.delete()

        messages.success(
            request,
            f"El producto '{nombre}' fue eliminado definitivamente."
        )

    return redirect("productos:lista")


@login_required
def categorias_marcas(request):
    form_cat = CategoriaForm()
    form_marca = MarcaForm()

    if request.method == "POST":
        tipo = request.POST.get("tipo")

        if tipo == "categoria":
            form_cat = CategoriaForm(request.POST)

            if form_cat.is_valid():
                cat = form_cat.save()

                messages.success(
                    request,
                    f"Categoría '{cat.nombre}' creada con éxito."
                )

                return redirect("productos:categorias_marcas")

        elif tipo == "marca":
            form_marca = MarcaForm(request.POST)

            if form_marca.is_valid():
                marca = form_marca.save()

                messages.success(
                    request,
                    f"Marca '{marca.nombre}' creada con éxito."
                )

                return redirect("productos:categorias_marcas")

    categorias = Categoria.objects.all().order_by("nombre")
    marcas = Marca.objects.all().order_by("nombre")

    return render(
        request,
        "productos/categorias_marcas.html",
        {
            "categorias": categorias,
            "marcas": marcas,
            "form_cat": form_cat,
            "form_marca": form_marca,
        }
    )


# ==========================================
# EDICIÓN DE CATEGORÍAS Y MARCAS
# ==========================================

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f"La categoría '{categoria.nombre}' fue actualizada correctamente."
            )

            return redirect("productos:categorias_marcas")

    else:
        form = CategoriaForm(instance=categoria)

    return render(
        request,
        "productos/form_clasificacion.html",
        {
            "form": form,
            "titulo": "Editar categoría",
            "descripcion": "Modifica los datos de esta categoría.",
            "tipo": "categoría",
        }
    )


@login_required
def editar_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)

    if request.method == "POST":
        form = MarcaForm(request.POST, instance=marca)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f"La marca '{marca.nombre}' fue actualizada correctamente."
            )

            return redirect("productos:categorias_marcas")

    else:
        form = MarcaForm(instance=marca)

    return render(
        request,
        "productos/form_clasificacion.html",
        {
            "form": form,
            "titulo": "Editar marca",
            "descripcion": "Modifica los datos de esta marca.",
            "tipo": "marca",
        }
    )


# ==========================================
# ACTIVAR Y DESACTIVAR CATEGORÍAS Y MARCAS
# ==========================================

@login_required
@require_POST
def cambiar_estado_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    categoria.activo = not categoria.activo
    categoria.save(update_fields=["activo", "actualizado_en"])

    if categoria.activo:
        messages.success(
            request,
            f"La categoría '{categoria.nombre}' fue activada."
        )
    else:
        messages.warning(
            request,
            f"La categoría '{categoria.nombre}' fue desactivada."
        )

    return redirect("productos:categorias_marcas")


@login_required
@require_POST
def cambiar_estado_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)

    marca.activo = not marca.activo
    marca.save(update_fields=["activo", "actualizado_en"])

    if marca.activo:
        messages.success(
            request,
            f"La marca '{marca.nombre}' fue activada."
        )
    else:
        messages.warning(
            request,
            f"La marca '{marca.nombre}' fue desactivada."
        )

    return redirect("productos:categorias_marcas")
