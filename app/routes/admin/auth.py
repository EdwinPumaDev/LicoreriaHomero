
from urllib.parse import urlsplit

from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, select

from app.extensions import db
from app.models import Usuario
from app.routes.admin import admin


@admin.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Ingresa tu usuario y contraseña.", "warning")
            return render_template("admin/login.html")

        usuario = db.session.scalar(
            select(Usuario).where(
                func.lower(Usuario.username) == username.lower()
            )
        )

        if (
            usuario is None
            or not usuario.activo
            or not usuario.verificar_password(password)
        ):
            flash("Usuario o contraseña incorrectos.", "danger")
            return render_template("admin/login.html"), 401

        login_user(usuario)

        destino = request.args.get("next", "")
        partes = urlsplit(destino)

        # Solo se aceptan destinos locales para evitar redirecciones externas.
        if (
            destino.startswith("/")
            and not destino.startswith("//")
            and not partes.netloc
            and not partes.scheme
        ):
            return redirect(destino)

        return redirect(url_for("admin.dashboard"))

    return render_template("admin/login.html")


@admin.get("/")
@login_required
def dashboard():
    return render_template("admin/dashboard.html")


@admin.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "success")
    return redirect(url_for("admin.login"))
