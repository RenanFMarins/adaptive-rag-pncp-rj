"""Contratos públicos de saúde e prontidão da API."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, status


router = APIRouter(tags=["System"])


def _disable_cache(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


@router.get("/health", summary="Verificar se a API está ativa")
def health(response: Response) -> dict[str, str]:
    """Liveness leve: não abre bancos, índices ou serviços externos."""

    _disable_cache(response)
    return {"status": "ok"}


@router.get(
    "/ready",
    summary="Verificar as capacidades de consulta disponíveis",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Nenhuma rota principal de consulta está disponível"
        }
    },
)
def readiness(request: Request, response: Response) -> dict[str, object]:
    """Expõe prontidão sem revelar caminhos, exceções ou configurações.

    A API pode operar de forma degradada: consultas estruturadas dependem da
    base normalizada, RAG depende do índice vetorial e Hybrid depende dos dois.
    O serviço só retorna 503 quando nenhuma das duas capacidades principais
    está pronta.
    """

    _disable_cache(response)
    normalized_ready = bool(
        getattr(request.app.state, "normalized_database_ready", False)
    )
    faiss_ready = bool(getattr(request.app.state, "faiss_index_ready", False))

    if normalized_ready and faiss_ready:
        readiness_status = "ready"
    elif normalized_ready or faiss_ready:
        readiness_status = "degraded"
    else:
        readiness_status = "unavailable"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": readiness_status,
        "components": {
            "api": "ready",
            "normalized_database": (
                "ready" if normalized_ready else "unavailable"
            ),
            "vector_index": "ready" if faiss_ready else "unavailable",
        },
        "capabilities": {
            "structured": normalized_ready,
            "rag": faiss_ready,
            "hybrid": normalized_ready and faiss_ready,
        },
    }
