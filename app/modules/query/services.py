from __future__ import annotations

import sqlite3
from collections.abc import Callable
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.query.model import Query, Response, ResponseSource
from src.query.adaptive_executor import (
    AdaptiveExecutionResult,
    executar_plano_adaptativo,
)
from src.query.analyzer import analisar_pergunta
from src.query.executor import executar_consulta_adaptativa
from src.query.schemas import AdaptiveQueryResult, QueryAnalysis
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

    kwargs: dict[str, object] = {}
    if analyzer_fn is not None:
        kwargs["analyzer_fn"] = analyzer_fn
    return executar_consulta_adaptativa(
        _sqlite_connection_from_session(db),
        pergunta,
        **kwargs,
    )


def executar_consulta_adaptativa_api(
    db: Session,
    pergunta: str,
    top_k: int,
    analyzer_fn: AnalyzerFn | None = None,
    rag_executor: Callable[[], object] | None = None,
) -> AdaptiveExecutionResult:
    """Analisa uma vez a pergunta e executa exclusivamente sua rota planejada."""

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
                persistir=True,
            )

    return executar_plano_adaptativo(
        analysis,
        structured_connection=_sqlite_connection_from_session(db),
        rag_executor=rag_executor,
    )


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
