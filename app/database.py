"""Conexión con la base de datos SQLite.

Este módulo solo sabe abrir conexiones y crear las tablas. Las consultas
concretas sobre tareas están en `repository.py`.
"""

import sqlite3
from collections.abc import Iterator

from app.config import RUTA_DB

# Sentencia que crea la tabla de tareas si todavía no existe.
# - SQLite no tiene tipo BOOLEAN: guardamos "completada" como 0 (False) o 1 (True).
# - La fecha se guarda en UTC en formato ISO 8601 con "Z" al final
#   (ej. 2026-10-02T11:56:21Z) para que quien la reciba sepa que es UTC.
SQL_CREAR_TABLA_TAREAS = """
CREATE TABLE IF NOT EXISTS tareas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT    NOT NULL,
    descripcion    TEXT,
    completada     INTEGER NOT NULL DEFAULT 0,
    fecha_creacion TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
)
"""


def conectar(ruta: str = RUTA_DB) -> sqlite3.Connection:
    """Abre una conexión a SQLite que devuelve las filas como diccionarios."""
    # FastAPI puede abrir la conexión en un hilo y cerrarla en otro distinto.
    # Desactivar esta comprobación es seguro porque cada petición usa su propia conexión.
    conexion = sqlite3.connect(ruta, check_same_thread=False)
    # sqlite3.Row permite acceder a las columnas por nombre: fila["titulo"].
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db(ruta: str = RUTA_DB) -> None:
    """Crea las tablas necesarias. Se ejecuta una vez al arrancar la aplicación."""
    conexion = conectar(ruta)
    try:
        conexion.execute(SQL_CREAR_TABLA_TAREAS)
        conexion.commit()
    finally:
        conexion.close()


def get_db() -> Iterator[sqlite3.Connection]:
    """Dependencia de FastAPI: entrega una conexión por petición y la cierra al terminar.

    El código anterior al `yield` se ejecuta antes del endpoint; el bloque
    `finally` se ejecuta después, incluso si el endpoint lanza un error.
    """
    conexion = conectar()
    try:
        yield conexion
    finally:
        conexion.close()
