
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

try:
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    ) as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT current_database(), version()")
            nombre_bd, version = cursor.fetchone()

            print("¡Conexión exitosa con PostgreSQL!")
            print(f"Base de datos: {nombre_bd}")
            print(f"Versión: {version.split(',')[0]}")

except Exception as error:
    print("No se pudo conectar con PostgreSQL.")
    print(f"Detalle: {error}")
