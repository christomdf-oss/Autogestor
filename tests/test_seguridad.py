
import os
import tempfile
from pathlib import Path

# Base de datos temporal para pruebas.
# Se configura ANTES de importar los módulos de AutoGestor.
directorio_temporal = tempfile.mkdtemp(
    prefix="autogestor_tests_"
)

ruta_db = Path(directorio_temporal) / "autogestor_test.db"

os.environ["DATABASE_URL"] = (
    f"sqlite:///{ruta_db.as_posix()}"
)
os.environ["SECRET_KEY"] = (
    "clave-exclusiva-de-pruebas-123456789"
)
os.environ["IMAGE_STORAGE"] = "local"

from fastapi.testclient import TestClient
from main import app
from database import engine


# PRUEBA 1: Consultar vehículos sin iniciar sesión.
def test_consultar_vehiculos_sin_token():
    with TestClient(app) as cliente:
        respuesta = cliente.get("/vehiculos")

    assert respuesta.status_code == 401


# PRUEBA 2: Crear vehículo sin iniciar sesión.
def test_crear_vehiculo_sin_token():
    with TestClient(app) as cliente:
        respuesta = cliente.post(
            "/vehiculos",
            json={}
        )

    assert respuesta.status_code == 401


# PRUEBA 3: Consultar usuarios sin iniciar sesión.
def test_consultar_usuarios_sin_token():
    with TestClient(app) as cliente:
        respuesta = cliente.get("/usuarios")

    assert respuesta.status_code == 401


# PRUEBA 4: Consultar perfil sin iniciar sesión.
def test_consultar_perfil_sin_token():
    with TestClient(app) as cliente:
        respuesta = cliente.get("/usuarios/me")

    assert respuesta.status_code == 401


# Cerrar las conexiones al finalizar las pruebas.
def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
