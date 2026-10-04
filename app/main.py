"""Punto de entrada de la aplicación.

Aquí se crea la aplicación FastAPI y se registran los routers. Para arrancar
el servidor de desarrollo:

    uvicorn app.main:app --reload
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ORIGENES_CORS
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

# CORS: autoriza a páginas web servidas desde otro dominio o puerto (por ejemplo,
# un frontend en http://localhost:5173) a llamar a esta API desde el navegador.
# No se activan credenciales (cookies): los navegadores no las permiten junto con
# el origen "*" y esta API no las necesita.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_CORS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra todas las rutas definidas en app/routers/tareas.py.
app.include_router(tareas.router)


@app.get("/", tags=["Estado"], summary="Comprobar que la API está activa")
def raiz() -> dict[str, str]:
    """Endpoint de bienvenida, útil para comprobar rápidamente que el servidor responde."""
    return {"mensaje": "API de Tareas funcionando. Documentación en /docs"}
