
from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)

    codigo = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    nombre = db.Column(
        db.String(150),
        nullable=False,
        index=True,
    )

    descripcion = db.Column(db.Text, nullable=True)

    marca = db.Column(db.String(100), nullable=True)

    categoria = db.Column(db.String(100), nullable=False, index=True)

    costo = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    precio_venta = db.Column(
        db.Numeric(10, 2),
        nullable=False,
    )

    stock = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    stock_minimo = db.Column(
        db.Integer,
        nullable=False,
        default=5,
    )

    imagen = db.Column(db.String(255), nullable=True)

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    creado_en = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    actualizado_en = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def necesita_reposicion(self):
        return self.stock <= self.stock_minimo

    @property
    def margen_bruto_unitario(self):
        return self.precio_venta - self.costo

    def __repr__(self):
        return f"<Producto {self.codigo}: {self.nombre}>"
