"""Capa de acceso a datos (patrón Repositorio).

Todo el SQL de las tareas vive aquí. Los endpoints no escriben SQL: llaman a
estas funciones. Así, si mañana se cambia SQLite por otra base de datos, solo
hay que modificar este fichero.

Importante: los valores siempre se pasan como parámetros (`?`) y nunca
formateando el texto del SQL (f-strings), para evitar inyección SQL.
"""

import sqlite3

from app.schemas import Tarea, TareaActualizar, TareaCrear


def _fila_a_tarea(fila: sqlite3.Row) -> Tarea:
    """Convierte una fila de SQLite en un modelo Pydantic `Tarea`."""
    # Pydantic convierte automáticamente 0/1 en False/True y el texto de la fecha en datetime.
    return Tarea.model_validate(dict(fila))


def listar_tareas(conexion: sqlite3.Connection, completada: bool | None = None) -> list[Tarea]:
    """Devuelve todas las tareas, opcionalmente filtradas por su estado."""
    if completada is None:
        filas = conexion.execute("SELECT * FROM tareas ORDER BY id").fetchall()
    else:
        filas = conexion.execute(
            "SELECT * FROM tareas WHERE completada = ? ORDER BY id",
            (int(completada),),
        ).fetchall()
    return [_fila_a_tarea(fila) for fila in filas]


def obtener_tarea(conexion: sqlite3.Connection, tarea_id: int) -> Tarea | None:
    """Devuelve la tarea con ese id, o None si no existe."""
    fila = conexion.execute("SELECT * FROM tareas WHERE id = ?", (tarea_id,)).fetchone()
    return _fila_a_tarea(fila) if fila else None


def crear_tarea(conexion: sqlite3.Connection, datos: TareaCrear) -> Tarea:
    """Inserta una tarea nueva y la devuelve con su id y fecha de creación."""
    # RETURNING * devuelve la fila recién insertada, incluidos los valores
    # que ha generado SQLite (id, completada y fecha_creacion).
    fila = conexion.execute(
        "INSERT INTO tareas (titulo, descripcion) VALUES (?, ?) RETURNING *",
        (datos.titulo, datos.descripcion),
    ).fetchone()
    conexion.commit()
    return _fila_a_tarea(fila)


def actualizar_tarea(
    conexion: sqlite3.Connection, tarea_id: int, datos: TareaActualizar
) -> Tarea | None:
    """Reemplaza los datos de una tarea. Devuelve la tarea actualizada o None si no existe."""
    fila = conexion.execute(
        """
        UPDATE tareas
        SET titulo = ?, descripcion = ?, completada = ?
        WHERE id = ?
        RETURNING *
        """,
        (datos.titulo, datos.descripcion, int(datos.completada), tarea_id),
    ).fetchone()
    conexion.commit()
    return _fila_a_tarea(fila) if fila else None


def cambiar_estado_tarea(
    conexion: sqlite3.Connection, tarea_id: int, completada: bool
) -> Tarea | None:
    """Marca una tarea como completada o pendiente sin tocar el resto de campos.

    Devuelve la tarea actualizada o None si no existe.
    """
    fila = conexion.execute(
        "UPDATE tareas SET completada = ? WHERE id = ? RETURNING *",
        (int(completada), tarea_id),
    ).fetchone()
    conexion.commit()
    return _fila_a_tarea(fila) if fila else None


def eliminar_tarea(conexion: sqlite3.Connection, tarea_id: int) -> bool:
    """Borra una tarea. Devuelve True si se borró y False si no existía."""
    cursor = conexion.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    conexion.commit()
    # rowcount indica cuántas filas se han borrado (0 si el id no existía).
    return cursor.rowcount > 0
