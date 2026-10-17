
from getpass import getpass

from sqlalchemy import func, select

from app import create_app
from app.extensions import db
from app.models import Usuario


def solicitar_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("Este campo es obligatorio.")


def main():
    app = create_app()

    with app.app_context():
        administrador_existente = db.session.scalar(
            select(Usuario.id).where(
                Usuario.es_administrador_principal.is_(True)
            )
        )

        if administrador_existente is not None:
            print("Ya existe un administrador principal.")
            print("No se creó ninguna cuenta nueva.")
            return

        nombre = solicitar_texto("Nombre: ")
        apellido = input("Apellido (opcional): ").strip()
        username = solicitar_texto("Nombre de usuario: ")

        email = input("Correo electrónico (opcional): ").strip() or None

        usuario_existente = db.session.scalar(
            select(Usuario.id).where(
                func.lower(Usuario.username) == username.lower()
            )
        )

        if usuario_existente is not None:
            print("Ese nombre de usuario ya está registrado.")
            return

        if email:
            correo_existente = db.session.scalar(
                select(Usuario.id).where(
                    func.lower(Usuario.email) == email.lower()
                )
            )
            if correo_existente is not None:
                print("Ese correo electrónico ya está registrado.")
                return

        while True:
            password = getpass("Contraseña (mínimo 12 caracteres): ")

            if len(password) < 12:
                print("La contraseña debe tener al menos 12 caracteres.")
                continue

            confirmacion = getpass("Repite la contraseña: ")

            if password != confirmacion:
                print("Las contraseñas no coinciden.")
                continue

            break

        administrador = Usuario(
            nombre=nombre,
            apellido=apellido or None,
            username=username,
            email=email,
            rol="administrador",
            activo=True,
            es_administrador_principal=True,
        )

        administrador.establecer_password(password)

        try:
            db.session.add(administrador)
            db.session.commit()
            print("\nAdministrador principal creado correctamente.")
            print(f"Usuario: {username}")
            print("Guarda tus credenciales en un lugar seguro.")
        except Exception:
            db.session.rollback()
            print(
                "\nNo se pudo crear el administrador. "
                "Comprueba los datos y el estado de PostgreSQL."
            )
            raise


if __name__ == "__main__":
    main()
