
from decimal import Decimal, InvalidOperation

from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Producto
from app.routes.admin import admin


@admin.route("/productos")
@login_required
def lista_productos():
    busqueda = request.args.get("q", "").strip()

    consulta = select(Producto)

    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.where(
            or_(
                Producto.codigo.ilike(patron),
                Producto.nombre.ilike(patron),
                Producto.marca.ilike(patron),
                Producto.categoria.ilike(patron),
            )
        )

    productos = db.session.scalars(
        consulta.order_by(Producto.nombre.asc())
    ).all()

    return render_template(
        "admin/productos/lista.html",
        productos=productos,
        busqueda=busqueda,
    )


@admin.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_producto():
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        marca = request.form.get("marca", "").strip()
        categoria = request.form.get("categoria", "").strip()

        try:
            costo = Decimal(request.form.get("costo", ""))
            precio = Decimal(request.form.get("precio_venta", ""))
            stock = int(request.form.get("stock", ""))
            stock_minimo = int(request.form.get("stock_minimo", "5"))
        except (InvalidOperation, ValueError):
            flash("Revisa los precios y las cantidades ingresadas.", "danger")
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="nuevo",
            ), 400

        if not codigo or not nombre or not categoria:
            flash("Código, nombre y categoría son obligatorios.", "warning")
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="nuevo",
            ), 400

        if (
            len(codigo) > 50
            or len(nombre) > 150
            or len(marca) > 100
            or len(categoria) > 100
        ):
            flash("Uno de los campos supera la longitud permitida.", "warning")
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="nuevo",
            ), 400

        if (
            costo < 0
            or precio <= 0
            or costo.as_tuple().exponent < -2
            or precio.as_tuple().exponent < -2
            or costo >= Decimal("100000000")
            or precio >= Decimal("100000000")
            or stock < 0
            or stock_minimo < 0
            or stock > 2147483647
            or stock_minimo > 2147483647
        ):
            flash(
                "Los precios deben ser válidos y las cantidades no pueden ser negativas.",
                "warning",
            )
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="nuevo",
            ), 400

        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion or None,
            marca=marca or None,
            categoria=categoria,
            costo=costo,
            precio_venta=precio,
            stock=stock,
            stock_minimo=stock_minimo,
        )

        try:
            db.session.add(producto)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(
                "No se pudo registrar el producto. "
                "Comprueba que el código no esté repetido.",
                "danger",
            )
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="nuevo",
            ), 400

        flash("Producto registrado correctamente.", "success")
        return redirect(url_for("admin.lista_productos"))

    return render_template(
        "admin/productos/formulario.html",
        producto=None,
        modo="nuevo",
    )


@admin.route("/productos/<int:producto_id>/editar", methods=["GET", "POST"])
@login_required
def editar_producto(producto_id):
    producto = db.get_or_404(Producto, producto_id)

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        marca = request.form.get("marca", "").strip()
        categoria = request.form.get("categoria", "").strip()

        try:
            costo = Decimal(request.form.get("costo", ""))
            precio = Decimal(request.form.get("precio_venta", ""))
            stock = int(request.form.get("stock", ""))
            stock_minimo = int(request.form.get("stock_minimo", "5"))
        except (InvalidOperation, ValueError):
            flash("Revisa los precios y las cantidades ingresadas.", "danger")
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="editar",
            ), 400

        if not codigo or not nombre or not categoria:
            flash("Código, nombre y categoría son obligatorios.", "warning")
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="editar",
            ), 400

        if (
            len(codigo) > 50
            or len(nombre) > 150
            or len(marca) > 100
            or len(categoria) > 100
        ):
            flash("Uno de los campos supera la longitud permitida.", "warning")
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="editar",
            ), 400

        if (
            costo < 0
            or precio <= 0
            or costo.as_tuple().exponent < -2
            or precio.as_tuple().exponent < -2
            or costo >= Decimal("100000000")
            or precio >= Decimal("100000000")
            or stock < 0
            or stock_minimo < 0
            or stock > 2147483647
            or stock_minimo > 2147483647
        ):
            flash(
                "Los precios deben ser válidos y las cantidades no pueden ser negativas.",
                "warning",
            )
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="editar",
            ), 400

        producto.codigo = codigo
        producto.nombre = nombre
        producto.descripcion = descripcion or None
        producto.marca = marca or None
        producto.categoria = categoria
        producto.costo = costo
        producto.precio_venta = precio
        producto.stock = stock
        producto.stock_minimo = stock_minimo

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(
                "No se pudo actualizar el producto. "
                "Comprueba que el código no esté repetido.",
                "danger",
            )
            return render_template(
                "admin/productos/formulario.html",
                producto=request.form,
                modo="editar",
            ), 400

        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("admin.lista_productos"))

    return render_template(
        "admin/productos/formulario.html",
        producto=producto,
        modo="editar",
    )


@admin.post("/productos/<int:producto_id>/cambiar-estado")
@login_required
def cambiar_estado_producto(producto_id):
    producto = db.get_or_404(Producto, producto_id)
    producto.activo = not producto.activo
    db.session.commit()

    mensaje = "activado" if producto.activo else "desactivado"
    flash(f"Producto {mensaje} correctamente.", "success")

    return redirect(url_for("admin.lista_productos"))
