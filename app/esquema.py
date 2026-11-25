import click
from sqlalchemy import inspect

from . import app, db
from .models import PacienteVeterinario, TokenRevocado


@app.cli.command("actualizar-esquema")
def actualizar_esquema():
    """Agrega las columnas y tablas requeridas a una base existente."""
    with db.engine.begin() as conexion:
        inspector = inspect(conexion)
        tablas_base = ("usuario", "mascota", "catalogo_producto", "registro_aplicacion")
        faltantes = [tabla for tabla in tablas_base if not inspector.has_table(tabla)]
        if faltantes:
            raise click.ClickException("Importa primero el esquema base. Faltan: " + ", ".join(faltantes))

        columnas = {
            "usuario": {"actualizado_en": "DATETIME"},
            "mascota": {"sexo": "VARCHAR(10)", "actualizado_en": "DATETIME"},
        }
        for tabla, definiciones in columnas.items():
            existentes = {columna["name"] for columna in inspector.get_columns(tabla)}
            for nombre, tipo in definiciones.items():
                if nombre not in existentes:
                    conexion.exec_driver_sql(f"ALTER TABLE {tabla} ADD COLUMN {nombre} {tipo}")

        TokenRevocado.__table__.create(conexion, checkfirst=True)
        PacienteVeterinario.__table__.create(conexion, checkfirst=True)

    click.echo("Esquema actualizado.")
