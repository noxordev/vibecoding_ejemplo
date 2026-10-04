"""Tests de la configuración CORS."""

from fastapi.testclient import TestClient

ORIGEN_FRONTEND = "http://localhost:5173"


def test_peticion_desde_otro_origen_incluye_cabecera_cors(cliente: TestClient) -> None:
    respuesta = cliente.get("/tareas", headers={"Origin": ORIGEN_FRONTEND})

    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == "*"


def test_preflight_permite_metodos_de_escritura(cliente: TestClient) -> None:
    # Antes de un PUT o DELETE, el navegador envía una petición OPTIONS ("preflight")
    # para preguntar si el método y las cabeceras están permitidos.
    respuesta = cliente.options(
        "/tareas/1",
        headers={
            "Origin": ORIGEN_FRONTEND,
            "Access-Control-Request-Method": "DELETE",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == "*"
    assert "DELETE" in respuesta.headers["access-control-allow-methods"]
