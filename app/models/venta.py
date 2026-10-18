
from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db


class Venta(db.Model):
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True)

    numero = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )

    fecha = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    total = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="completada",
    )

    observaciones = db.Column(db.String(500), nullable=True)

    usuario = db.relationship(
        "Usuario",
        backref=db.backref("ventas", lazy="select"),
    )

    detalles = db.relationship(
        "DetalleVenta",
        back_populates="venta",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="DetalleVenta.id",
    )

    def __repr__(self):
        return f"<Venta {self.numero}>"


class DetalleVenta(db.Model):
    __tablename__ = "detalles_venta"

    id = db.Column(db.Integer, primary_key=True)

    venta_id = db.Column(
        db.Integer,
        db.ForeignKey("ventas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey("productos.id"),
        nullable=False,
        index=True,
    )

    cantidad = db.Column(
        db.Integer,
        nullable=False,
    )

    precio_unitario = db.Column(
        db.Numeric(10, 2),
        nullable=False,
    )

    subtotal = db.Column(
        db.Numeric(12, 2),
        nullable=False,
    )

    venta = db.relationship(
        "Venta",
        back_populates="detalles",
    )

    producto = db.relationship(
        "Producto",
        backref=db.backref("detalles_venta", lazy="select"),
    )

    def __repr__(self):
        return (
            f"<DetalleVenta venta={self.venta_id} "
            f"producto={self.producto_id}>"
        )
