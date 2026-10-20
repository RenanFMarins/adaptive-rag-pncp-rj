from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query as QueryParameter
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.llm_provider import LlmProviderError
from app.core.security import get_current_user
from app.modules.auth.model import User
from app.modules.query.schemas import (
    AdaptiveAskRequest,
    AdaptiveAskResponse,
    GenerateRequest,
    GenerateResponse,
    SourceResponse,
    StructuredQueryRequest,
    StructuredQueryResponse,
)
from app.modules.documents.services import consultar_catalogo_documentos_pncp
from app.modules.query.services import (
    executar_consulta_adaptativa_api,
    executar_consulta_estruturada,
)
from src.generate import gerar_resposta_rag
from src.query.analyzer import QueryAnalysisError
from src.query.executor import QueryExecutionError
from src.query.structured_tool import StructuredQueryError


router = APIRouter(prefix="/query", tags=["Query"])


def _detalhe_erro_consulta(exc: Exception) -> str | dict[str, object]:
    """Mantém o 422 explicável sem expor a resposta bruta da LLM."""

    if isinstance(exc, QueryAnalysisError):
        return exc.detalhe_publico()
    return str(exc)


@router.post(
    "/ask",
    response_model=AdaptiveAskResponse,
    summary="Executar consulta pelo roteamento adaptativo",
)
def ask(
    request: AdaptiveAskRequest,
    db: Annotated[Session, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
) -> AdaptiveAskResponse:
    """Executa SQL ou RAG conforme a rota validada pelo Planner."""

    try:
        result = executar_consulta_adaptativa_api(
            db,
            request.pergunta,
            request.top_k,
        )
    except LlmProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except (QueryAnalysisError, QueryExecutionError, StructuredQueryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_detalhe_erro_consulta(exc),
        ) from exc

    structured_result = (
        result.structured_result.structured_result
        if result.structured_result is not None
        else None
    )
    if result.rag_result is None and (
        structured_result is not None or result.plan.route.value == "catalog"
    ):
        return AdaptiveAskResponse(
            route=result.plan.route,
            analysis=result.analysis,
            plan=result.plan,
            structured_result=structured_result,
            external_documents=result.external_documents,
        )

    rag_result = result.rag_result
    if rag_result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A rota planejada não produziu resultado.",
        )
    return AdaptiveAskResponse(
        route=result.plan.route,
        analysis=result.analysis,
        plan=result.plan,
        structured_result=structured_result,
        answer=rag_result.answer,
        sources=[
            SourceResponse(
                rank=rank,
                chunk_id=source.chunk_id,
                relevance_score=source.rrf_score,
                metadata=source.metadata,
            )
            for rank, source in enumerate(rag_result.sources, start=1)
        ],
        external_documents=result.external_documents,
    )


@router.get(
    "/catalog/documents",
    summary="Consultar localmente os documentos listados no PNCP",
)
def consultar_catalogo(
    db: Annotated[Session, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
    numero_controle_pncp: str | None = None,
    tipo_entidade: str | None = None,
    tipo_documento: str | None = None,
    titulo: str | None = None,
    limite: int = QueryParameter(default=20, ge=1, le=100),
) -> dict[str, object]:
    """Consulta o catálogo local; não chama o endpoint do PNCP."""

    try:
        documentos = consultar_catalogo_documentos_pncp(
            db,
            numero_controle_pncp=numero_controle_pncp,
            tipo_entidade=tipo_entidade,
            tipo_documento=tipo_documento,
            titulo=titulo,
            limite=limite,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return {"total": len(documentos), "documents": documentos}


@router.post(
    "/structured",
    response_model=StructuredQueryResponse,
    summary="Consultar contratos e contratações estruturados",
)
def structured(
    request: StructuredQueryRequest,
    db: Annotated[Session, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
) -> StructuredQueryResponse:
    """Expõe somente a rota estruturada do Adaptive RAG nesta primeira fase."""

    try:
        result = executar_consulta_estruturada(db, request.pergunta)
    except LlmProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except (QueryAnalysisError, QueryExecutionError, StructuredQueryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_detalhe_erro_consulta(exc),
        ) from exc

    return StructuredQueryResponse(**result.model_dump())


@router.post("/generate", response_model=GenerateResponse)
def generate(
    request: GenerateRequest,
    db: Annotated[Session, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
):
    try:
        resultado = gerar_resposta_rag(
            db=db,
            pergunta=request.pergunta,
            top_k=request.top_k,
            persistir=True,
        )
    except LlmProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return GenerateResponse(
        answer=resultado.answer,
        sources=[
            SourceResponse(
                rank=rank,
                chunk_id=source.chunk_id,
                relevance_score=source.rrf_score,
                metadata=source.metadata,
            )
            for rank, source in enumerate(resultado.sources, start=1)
        ],
    )
