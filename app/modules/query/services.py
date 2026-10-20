from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import replace
from uuid import uuid4

from sqlalchemy.orm import Session
from app.core.logging import perf_stage
from app.core.config import resolver_caminho_indice_faiss

from app.modules.query.model import Query, Response, ResponseSource
from app.modules.documents.services import consultar_catalogo_documentos_pncp
from src.query.adaptive_executor import (
    AdaptiveExecutionResult,
    executar_plano_adaptativo,
)
from src.query.analyzer import analisar_pergunta, analisar_pergunta_estruturada
from src.query.executor import executar_consulta_adaptativa
from src.query.schemas import AdaptiveQueryResult, QueryAnalysis, QueryRoute
from src.retrieve import RankedChunk


AnalyzerFn = Callable[[str], QueryAnalysis]


def _sqlite_connection_from_session(db: Session) -> sqlite3.Connection:
    """Obtém a conexão SQLite atual sem abrir outro banco para a consulta."""

    sqlalchemy_connection = db.connection()
    connection_proxy = sqlalchemy_connection.connection
    raw_connection = getattr(connection_proxy, "driver_connection", connection_proxy)
    if not isinstance(raw_connection, sqlite3.Connection):
        raise RuntimeError("A consulta estruturada requer uma conexão SQLite.")
    return raw_connection


def executar_consulta_estruturada(
    db: Session,
    pergunta: str,
    analyzer_fn: AnalyzerFn | None = None,
) -> AdaptiveQueryResult:
    """Executa Analyzer, Planner e Structured Tool na conexão da API."""

    return executar_consulta_adaptativa(
        _sqlite_connection_from_session(db),
        pergunta,
        analyzer_fn=analyzer_fn or analisar_pergunta_estruturada,
    )


def executar_consulta_adaptativa_api(
    db: Session,
    pergunta: str,
    top_k: int,
    analyzer_fn: AnalyzerFn | None = None,
    rag_executor: Callable[[], object] | None = None,
    hybrid_executor: Callable[[AdaptiveQueryResult], object] | None = None,
    catalog_executor: Callable[[], list[dict[str, object]]] | None = None,
) -> AdaptiveExecutionResult:
    """Analisa uma vez a pergunta e executa exclusivamente sua rota planejada."""

    with perf_stage("analyzer"):
        analysis = (analyzer_fn or analisar_pergunta)(pergunta)

    if rag_executor is None:
        def rag_executor() -> object:
            # Importação tardia evita ciclo: generate.py já usa este service
            # para persistir Query, Response e ResponseSource.
            from src.generate import gerar_resposta_rag

            return gerar_resposta_rag(
                db=db,
                pergunta=pergunta,
                top_k=top_k,
                cache_dir=resolver_caminho_indice_faiss(),
                persistir=True,
                filters=analysis.filters,
                bases=analysis.bases,
            )

    if hybrid_executor is None:
        def hybrid_executor(structured: AdaptiveQueryResult) -> object:
            # A fonte estruturada é entregue em seção própria; as citações da
            # resposta continuam apontando somente para chunks documentais.
            from src.generate import gerar_resposta_rag

            return gerar_resposta_rag(
                db=db,
                pergunta=pergunta,
                top_k=top_k,
                cache_dir=resolver_caminho_indice_faiss(),
                persistir=True,
                filters=analysis.filters,
                bases=analysis.bases,
                structured_result=structured.structured_result,
            )

    if catalog_executor is None:
        def catalog_executor() -> list[dict[str, object]]:
            tipo_entidade = analysis.filters.tipo_entidade
            return consultar_catalogo_documentos_pncp(
                db,
                numero_controle_pncp=analysis.filters.numero_controle_pncp,
                tipo_entidade=(
                    tipo_entidade.value if tipo_entidade is not None else None
                ),
                tipo_documento=analysis.filters.tipo_documento,
                limite=20,
            )

    structured_connection = None
    if analysis.route is not QueryRoute.CATALOG:
        with perf_stage("database_connection"):
            structured_connection = _sqlite_connection_from_session(db)
    resultado = executar_plano_adaptativo(
        analysis,
        structured_connection=structured_connection,
        rag_executor=rag_executor,
        hybrid_executor=hybrid_executor,
        catalog_executor=catalog_executor,
    )

    # Fallback informativo: se uma pergunta documental por número de controle
    # não encontrou chunks, mostramos os arquivos previamente listados no
    # PNCP. Esta etapa NÃO baixa o documento e não chama a API externa.
    fontes = getattr(resultado.rag_result, "sources", None)
    controle = analysis.filters.numero_controle_pncp
    if resultado.rag_result is not None and not fontes and controle:
        tipo_entidade = (
            analysis.entity.value
            if analysis.entity.value in {"contrato", "contratacao"}
            else None
        )
        with perf_stage("catalog_fallback"):
            referencias = consultar_catalogo_documentos_pncp(
                db,
                numero_controle_pncp=controle,
                tipo_entidade=tipo_entidade,
                tipo_documento=analysis.filters.tipo_documento,
                limite=20,
            )
        return replace(resultado, external_documents=referencias)
    return resultado


def persistir_resultado_rag(
    db: Session,
    pergunta: str,
    resposta: str,
    sources: list[RankedChunk],
    is_refusal: bool = False,
) -> tuple[Query, Response]:
    query = Query(
        run_id=str(uuid4()),
        text=pergunta,
    )
    db.add(query)
    db.flush()

    response = Response(
        query_id=query.id,
        answer=resposta,
        is_refusal=is_refusal,
    )
    db.add(response)
    db.flush()

    for rank, source in enumerate(sources, start=1):
        document_chunk_id = source.metadata.get("id")

        if not isinstance(document_chunk_id, int):
            raise ValueError(
                f"RankedChunk {source.chunk_id} não possui "
                "DocumentChunk.id válido nos metadados."
            )

        db.add(
            ResponseSource(
                response_id=response.id,
                chunk_id=document_chunk_id,
                rank=rank,
                relevance_score=source.rrf_score,
            )
        )

    db.commit()
    db.refresh(query)
    db.refresh(response)

    return query, response
