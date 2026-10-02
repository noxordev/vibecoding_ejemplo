"""Punto de entrada de la aplicación.

Aquí se crea la aplicación FastAPI y se registran los routers. Para arrancar
el servidor de desarrollo:

    uvicorn app.main:app --reload
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import inicializar_db
from app.routers import tareas


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Ciclo de vida de la app: lo anterior al `yield` se ejecuta al arrancar
    y lo posterior, al apagar el servidor."""
    inicializar_db()
    yield


app = FastAPI(
    title="API de Tareas",
    description="API REST sencilla para gestionar tareas (CRUD) con FastAPI, Pydantic y SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)

# Registra todas las rutas definidas en app/routers/tareas.py.
app.include_router(tareas.router)


@app.get("/", tags=["Estado"], summary="Comprobar que la API está activa")
def raiz() -> dict[str, str]:
    """Endpoint de bienvenida, útil para comprobar rápidamente que el servidor responde."""
    return {"mensaje": "API de Tareas funcionando. Documentación en /docs"}
