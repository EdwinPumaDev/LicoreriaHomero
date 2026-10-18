
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Producto, Venta, DetalleVenta
from app.routes.admin import admin


CENTAVOS = Decimal("0.01")


def dinero(valor):
    return Decimal(valor).quantize(
        CENTAVOS,
        rounding=ROUND_HALF_UP,
    )


@admin.get("/ventas")
@login_required
def lista_ventas():
    consulta = (
        select(Venta)
        .order_by(Venta.fecha.desc(), Venta.id.desc())
    )

    ventas = db.session.scalars(consulta).all()

    return render_template(
        "admin/ventas/lista.html",
        ventas=ventas,
    )


@admin.route("/ventas/nueva", methods=["GET", "POST"])
@login_required
def nueva_venta():
    if request.method == "POST":
        cantidades = {}
        errores = []

        # Recibir y validar las cantidades enviadas.
        for clave, valor in request.form.items():
            if not clave.startswith("cantidad_"):
                continue

            identificador = clave.removeprefix("cantidad_")

            if not identificador.isdigit():
                errores.append("Se recibió un producto inválido.")
                continue

            try:
                cantidad = int(valor)
            except (ValueError, TypeError):
                errores.append("Todas las cantidades deben ser enteras.")
                continue

            if cantidad < 0:
                errores.append("Las cantidades no pueden ser negativas.")
                continue

            if cantidad > 0:
                producto_id = int(identificador)
                cantidades[producto_id] = (
                    cantidades.get(producto_id, 0) + cantidad
                )

        observaciones = request.form.get(
            "observaciones", ""
        ).strip()

        if len(observaciones) > 500:
            errores.append(
                "Las observaciones no pueden superar 500 caracteres."
            )

        if not cantidades:
            errores.append(
                "Selecciona al menos un producto con cantidad mayor que cero."
            )

        if errores:
            for error in errores:
                flash(error, "danger")

            return redirect(url_for("admin.nueva_venta"))

        try:
            # Bloquear las filas de los productos durante la venta.
            consulta = (
                select(Producto)
                .where(Producto.id.in_(list(cantidades.keys())))
                .order_by(Producto.id)
                .with_for_update()
            )

            productos = db.session.scalars(consulta).all()
            productos_por_id = {
                producto.id: producto for producto in productos
            }

            if set(productos_por_id) != set(cantidades):
                db.session.rollback()
                flash(
                    "Uno de los productos seleccionados ya no existe.",
                    "danger",
                )
                return redirect(url_for("admin.nueva_venta"))

            lineas = []
            total = Decimal("0.00")

            # Verificar existencias y calcular en el servidor.
            for producto_id, cantidad in cantidades.items():
                producto = productos_por_id[producto_id]

                if not producto.activo:
                    raise ValueError(
                        f"El producto {producto.nombre} está inactivo."
                    )

                if cantidad > producto.stock:
                    raise ValueError(
                        f"Stock insuficiente para {producto.nombre}. "
                        f"Disponible: {producto.stock}."
                    )

                precio = dinero(producto.precio_venta)

                if precio < 0:
                    raise ValueError(
                        f"El precio de {producto.nombre} no es válido."
                    )

                subtotal = dinero(precio * cantidad)
                total += subtotal

                lineas.append({
                    "producto": producto,
                    "cantidad": cantidad,
                    "precio": precio,
                    "subtotal": subtotal,
                })

            total = dinero(total)

            venta = Venta(
                numero=(
                    datetime.now(timezone.utc).strftime("V-%Y%m%d-%H%M%S")
                    + "-"
                    + uuid4().hex[:8].upper()
                ),
                usuario_id=current_user.id,
                fecha=datetime.now(timezone.utc),
                total=total,
                estado="completada",
                observaciones=observaciones or None,
            )

            db.session.add(venta)
            db.session.flush()

            # Crear el detalle y descontar las existencias.
            for linea in lineas:
                producto = linea["producto"]

                detalle = DetalleVenta(
                    venta_id=venta.id,
                    producto_id=producto.id,
                    cantidad=linea["cantidad"],
                    precio_unitario=linea["precio"],
                    subtotal=linea["subtotal"],
                )

                db.session.add(detalle)
                producto.stock -= linea["cantidad"]

            # Guardar toda la operación de una sola vez.
            db.session.commit()

            flash(
                f"Venta {venta.numero} registrada correctamente. "
                f"Total: Bs {total:.2f}.",
                "success",
            )

            return redirect(url_for("admin.lista_ventas"))

        except ValueError as error:
            db.session.rollback()
            flash(str(error), "danger")
            return redirect(url_for("admin.nueva_venta"))

        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception(
                "Error al registrar una venta."
            )
            flash(
                "No se pudo registrar la venta. "
                "No se guardaron cambios; revisa el registro del servidor.",
                "danger",
            )
            return redirect(url_for("admin.nueva_venta"))

    productos = db.session.scalars(
        select(Producto)
        .where(
            Producto.activo.is_(True),
            Producto.stock > 0,
        )
        .order_by(Producto.nombre)
    ).all()

    return render_template(
        "admin/ventas/nueva.html",
        productos=productos,
    )
