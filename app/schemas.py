"""Modelos Pydantic (esquemas).

Definen la forma de los datos que entran y salen de la API. FastAPI los usa
para validar automáticamente el JSON recibido (si algo no cumple las reglas,
responde con un error 422) y para generar la documentación en /docs.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TareaBase(BaseModel):
    """Campos comunes a todos los modelos de tarea."""

    # Elimina los espacios al principio y al final de los textos,
    # así un título como "   " se considera vacío y se rechaza.
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: str = Field(min_length=1, max_length=100, examples=["Comprar pan"])
    descripcion: str | None = Field(
        default=None, max_length=500, examples=["Integral, en la panadería de la esquina"]
    )


class TareaCrear(TareaBase):
    """Datos para crear una tarea (POST).

    No incluye `id` ni `fecha_creacion` porque los genera la base de datos,
    ni `completada` porque toda tarea nueva empieza sin completar.
    """


class TareaActualizar(TareaBase):
    """Datos para reemplazar una tarea completa (PUT).

    PUT sustituye el recurso entero, por eso hay que enviar todos los campos.
    """

    completada: bool


class Tarea(TareaBase):
    """Tarea tal y como la devuelve la API."""

    id: int
    completada: bool
    fecha_creacion: datetime
