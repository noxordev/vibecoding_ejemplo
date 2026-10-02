"""Tests de los endpoints de tareas."""

from fastapi.testclient import TestClient


def crear(cliente: TestClient, titulo: str = "Comprar pan", descripcion: str | None = None) -> dict:
    """Función auxiliar: crea una tarea y devuelve el JSON de la respuesta."""
    respuesta = cliente.post("/tareas", json={"titulo": titulo, "descripcion": descripcion})
    assert respuesta.status_code == 201
    return respuesta.json()


# --- POST ---


def test_crear_tarea(cliente: TestClient) -> None:
    tarea = crear(cliente, "Estudiar FastAPI", "Leer la documentación")

    assert tarea["id"] == 1
    assert tarea["titulo"] == "Estudiar FastAPI"
    assert tarea["descripcion"] == "Leer la documentación"
    assert tarea["completada"] is False
    assert tarea["fecha_creacion"].endswith("Z")  # fecha en UTC


def test_crear_tarea_con_titulo_vacio_devuelve_422(cliente: TestClient) -> None:
    respuesta = cliente.post("/tareas", json={"titulo": "   "})

    assert respuesta.status_code == 422


# --- GET ---


def test_listar_tareas_vacio(cliente: TestClient) -> None:
    respuesta = cliente.get("/tareas")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listar_tareas_filtrando_por_completada(cliente: TestClient) -> None:
    crear(cliente, "Pendiente")
    hecha = crear(cliente, "Hecha")
    cliente.put(f"/tareas/{hecha['id']}", json={"titulo": "Hecha", "completada": True})

    todas = cliente.get("/tareas").json()
    completadas = cliente.get("/tareas", params={"completada": True}).json()
    pendientes = cliente.get("/tareas", params={"completada": False}).json()

    assert len(todas) == 2
    assert [t["titulo"] for t in completadas] == ["Hecha"]
    assert [t["titulo"] for t in pendientes] == ["Pendiente"]


def test_obtener_tarea(cliente: TestClient) -> None:
    creada = crear(cliente)

    respuesta = cliente.get(f"/tareas/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_obtener_tarea_inexistente_devuelve_404(cliente: TestClient) -> None:
    respuesta = cliente.get("/tareas/999")

    assert respuesta.status_code == 404


# --- PUT ---


def test_actualizar_tarea(cliente: TestClient) -> None:
    creada = crear(cliente)

    respuesta = cliente.put(
        f"/tareas/{creada['id']}",
        json={"titulo": "Comprar pan integral", "descripcion": "Dos barras", "completada": True},
    )

    assert respuesta.status_code == 200
    tarea = respuesta.json()
    assert tarea["titulo"] == "Comprar pan integral"
    assert tarea["descripcion"] == "Dos barras"
    assert tarea["completada"] is True
    assert tarea["fecha_creacion"] == creada["fecha_creacion"]


def test_actualizar_tarea_inexistente_devuelve_404(cliente: TestClient) -> None:
    respuesta = cliente.put("/tareas/999", json={"titulo": "X", "completada": False})

    assert respuesta.status_code == 404


def test_completar_tarea(cliente: TestClient) -> None:
    creada = crear(cliente, "Comprar pan", "Integral")

    respuesta = cliente.put(f"/tareas/{creada['id']}/completar")

    assert respuesta.status_code == 200
    # Solo cambia "completada"; el resto de campos se mantiene igual.
    assert respuesta.json() == {**creada, "completada": True}


def test_completar_tarea_dos_veces_no_da_error(cliente: TestClient) -> None:
    creada = crear(cliente)
    cliente.put(f"/tareas/{creada['id']}/completar")

    respuesta = cliente.put(f"/tareas/{creada['id']}/completar")

    assert respuesta.status_code == 200
    assert respuesta.json()["completada"] is True


def test_completar_tarea_inexistente_devuelve_404(cliente: TestClient) -> None:
    respuesta = cliente.put("/tareas/999/completar")

    assert respuesta.status_code == 404


# --- DELETE ---


def test_eliminar_tarea(cliente: TestClient) -> None:
    creada = crear(cliente)

    respuesta = cliente.delete(f"/tareas/{creada['id']}")

    assert respuesta.status_code == 204
    assert cliente.get(f"/tareas/{creada['id']}").status_code == 404


def test_eliminar_tarea_inexistente_devuelve_404(cliente: TestClient) -> None:
    respuesta = cliente.delete("/tareas/999")

    assert respuesta.status_code == 404
