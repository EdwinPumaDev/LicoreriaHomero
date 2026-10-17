
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=True)

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=True,
        index=True,
    )

    password_hash = db.Column(db.String(255), nullable=False)

    rol = db.Column(
        db.String(20),
        nullable=False,
        default="empleado",
    )

    activo = db.Column(db.Boolean, nullable=False, default=True)

    es_administrador_principal = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
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

    def establecer_password(self, password):
        """Guarda una contraseña mediante un hash seguro."""
        self.password_hash = generate_password_hash(password)

    def verificar_password(self, password):
        """Comprueba una contraseña sin almacenar texto plano."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.username}>"
