"""Endpoints HTTP del recurso "tareas".

Esta capa solo se ocupa de HTTP: recibe la petición, delega el trabajo en el
repositorio y traduce el resultado a una respuesta (códigos 200, 201, 404...).

Los endpoints se definen con `def` (no `async def`) porque sqlite3 es una
librería bloqueante; así FastAPI los ejecuta en un hilo aparte y no bloquea
el servidor mientras se consulta la base de datos.
"""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app import repository
from app.database import get_db
from app.schemas import Tarea, TareaActualizar, TareaCrear

# Todas las rutas de este router empiezan por /tareas y aparecen agrupadas
# bajo la etiqueta "Tareas" en la documentación interactiva (/docs).
router = APIRouter(prefix="/tareas", tags=["Tareas"])

# Alias reutilizable: cualquier endpoint que declare un parámetro de este tipo
# recibirá una conexión a la base de datos (inyección de dependencias).
ConexionDB = Annotated[sqlite3.Connection, Depends(get_db)]


def _error_no_encontrada(tarea_id: int) -> HTTPException:
    """Construye el error 404 que se devuelve cuando una tarea no existe."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe ninguna tarea con id {tarea_id}",
    )


@router.get("", summary="Listar tareas")
def listar_tareas(
    conexion: ConexionDB,
    completada: Annotated[
        bool | None, Query(description="Filtrar por estado: true o false")
    ] = None,
) -> list[Tarea]:
    """**GET /tareas** — Devuelve todas las tareas.

    Opcionalmente se pueden filtrar con `?completada=true` o `?completada=false`.
    """
    return repository.listar_tareas(conexion, completada)


@router.get("/{tarea_id}", summary="Obtener una tarea")
def obtener_tarea(tarea_id: int, conexion: ConexionDB) -> Tarea:
    """**GET /tareas/{tarea_id}** — Devuelve una tarea concreta o 404 si no existe."""
    tarea = repository.obtener_tarea(conexion, tarea_id)
    if tarea is None:
        raise _error_no_encontrada(tarea_id)
    return tarea


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear una tarea")
def crear_tarea(datos: TareaCrear, conexion: ConexionDB) -> Tarea:
    """**POST /tareas** — Crea una tarea nueva y la devuelve con su id (201 Created)."""
    return repository.crear_tarea(conexion, datos)


@router.put("/{tarea_id}", summary="Actualizar una tarea")
def actualizar_tarea(tarea_id: int, datos: TareaActualizar, conexion: ConexionDB) -> Tarea:
    """**PUT /tareas/{tarea_id}** — Reemplaza todos los datos de una tarea existente."""
    tarea = repository.actualizar_tarea(conexion, tarea_id, datos)
    if tarea is None:
        raise _error_no_encontrada(tarea_id)
    return tarea


@router.put("/{tarea_id}/completar", summary="Completar una tarea")
def completar_tarea(tarea_id: int, conexion: ConexionDB) -> Tarea:
    """**PUT /tareas/{tarea_id}/completar** — Marca una tarea como completada.

    No necesita cuerpo. Si la tarea ya estaba completada, la devuelve sin
    cambios, por lo que se puede llamar varias veces con el mismo resultado.
    """
    tarea = repository.cambiar_estado_tarea(conexion, tarea_id, completada=True)
    if tarea is None:
        raise _error_no_encontrada(tarea_id)
    return tarea


@router.put("/{tarea_id}/desmarcar", summary="Desmarcar una tarea completada")
def desmarcar_tarea(tarea_id: int, conexion: ConexionDB) -> Tarea:
    """**PUT /tareas/{tarea_id}/desmarcar** — Vuelve a dejar una tarea como pendiente.

    Es la operación contraria a `/completar`: no necesita cuerpo y, si la tarea
    ya estaba pendiente, la devuelve sin cambios.
    """
    tarea = repository.cambiar_estado_tarea(conexion, tarea_id, completada=False)
    if tarea is None:
        raise _error_no_encontrada(tarea_id)
    return tarea


@router.delete(
    "/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una tarea"
)
def eliminar_tarea(tarea_id: int, conexion: ConexionDB) -> None:
    """**DELETE /tareas/{tarea_id}** — Borra una tarea (204 No Content, sin cuerpo)."""
    if not repository.eliminar_tarea(conexion, tarea_id):
        raise _error_no_encontrada(tarea_id)
