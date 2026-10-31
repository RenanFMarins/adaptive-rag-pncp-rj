"""Contrato HTTP público dos endpoints operacionais."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.system.routes import router


def _client(*, normalized: bool, faiss: bool) -> TestClient:
    app = FastAPI()
    app.state.normalized_database_ready = normalized
    app.state.faiss_index_ready = faiss
    app.include_router(router)
    return TestClient(app)


def test_health_e_leve_e_nao_expoe_detalhes_operacionais() -> None:
    app = FastAPI()
    app.state.normalized_database_error = "/caminho/privado/normalizada.db"
    app.state.faiss_index_error = "token-secreto"
    app.include_router(router)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["cache-control"] == "no-store"
    assert "/caminho/privado" not in response.text
    assert "token-secreto" not in response.text


def test_ready_quando_as_duas_capacidades_estao_disponiveis() -> None:
    with _client(normalized=True, faiss=True) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "components": {
            "api": "ready",
            "normalized_database": "ready",
            "vector_index": "ready",
        },
        "capabilities": {
            "structured": True,
            "rag": True,
            "hybrid": True,
        },
    }


def test_ready_degradado_preserva_consulta_estruturada_sem_faiss() -> None:
    with _client(normalized=True, faiss=False) as client:
        response = client.get("/ready")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "degraded"
    assert body["capabilities"] == {
        "structured": True,
        "rag": False,
        "hybrid": False,
    }


def test_ready_degradado_preserva_rag_sem_base_normalizada() -> None:
    with _client(normalized=False, faiss=True) as client:
        response = client.get("/ready")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "degraded"
    assert body["capabilities"] == {
        "structured": False,
        "rag": True,
        "hybrid": False,
    }


def test_ready_retorna_503_quando_nao_ha_capacidade_principal() -> None:
    app = FastAPI()
    app.state.normalized_database_ready = False
    app.state.normalized_database_error = "/nao/expor/normalizada.db"
    app.state.faiss_index_ready = False
    app.state.faiss_index_error = "credencial-ficticia"
    app.include_router(router)

    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["capabilities"] == {
        "structured": False,
        "rag": False,
        "hybrid": False,
    }
    assert "/nao/expor" not in response.text
    assert "credencial-ficticia" not in response.text
