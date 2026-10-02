"""Fixtures compartidas por todos los tests (pytest las carga automáticamente)."""

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database import conectar, get_db, inicializar_db
from app.main import app


@pytest.fixture
def cliente(tmp_path: Path) -> Iterator[TestClient]:
    """Cliente HTTP de pruebas con una base de datos temporal y vacía para cada test."""
    ruta_db = str(tmp_path / "test.db")
    inicializar_db(ruta_db)

    def get_db_de_prueba() -> Iterator[sqlite3.Connection]:
        conexion = conectar(ruta_db)
        try:
            yield conexion
        finally:
            conexion.close()

    # Sustituye la dependencia real por la de pruebas durante el test.
    app.dependency_overrides[get_db] = get_db_de_prueba
    # Sin "with": así no se ejecuta el lifespan, que crearía la base de datos real (tareas.db).
    yield TestClient(app)
    app.dependency_overrides.clear()
