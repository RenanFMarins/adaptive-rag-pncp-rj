"""Roteamento técnico entre o plano validado e seus executores permitidos."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .executor import QueryExecutionError, executar_analise_estruturada
from .planner import planejar_execucao
from .schemas import AdaptiveQueryResult, ExecutionPlan, QueryAnalysis, QueryRoute


RagExecutorFn = Callable[[], Any]
HybridExecutorFn = Callable[[AdaptiveQueryResult], Any]


@dataclass(frozen=True)
class AdaptiveExecutionResult:
    """Resultado de uma rota estruturada ou RAG antes da adaptação HTTP."""

    analysis: QueryAnalysis
    plan: ExecutionPlan
    structured_result: AdaptiveQueryResult | None = None
    rag_result: Any | None = None


def executar_plano_adaptativo(
    analysis: QueryAnalysis,
    *,
    structured_connection: sqlite3.Connection | None = None,
    rag_executor: RagExecutorFn | None = None,
    hybrid_executor: HybridExecutorFn | None = None,
) -> AdaptiveExecutionResult:
    """Executa exclusivamente a ferramenta indicada pela rota planejada.

    A rota híbrida executa SQL primeiro e entrega seu resultado ao executor
    documental, que é responsável por manter os dois contextos separados.
    """

    plan = planejar_execucao(analysis)
    if plan.route is QueryRoute.STRUCTURED:
        if structured_connection is None:
            raise QueryExecutionError("A rota structured requer conexão SQLite.")
        structured = executar_analise_estruturada(structured_connection, analysis)
        return AdaptiveExecutionResult(
            analysis=analysis,
            plan=plan,
            structured_result=structured,
        )

    if plan.route is QueryRoute.RAG:
        if rag_executor is None:
            raise QueryExecutionError("A rota rag requer um executor documental.")
        return AdaptiveExecutionResult(
            analysis=analysis,
            plan=plan,
            rag_result=rag_executor(),
        )

    if structured_connection is None:
        raise QueryExecutionError("A rota hybrid requer conexão SQLite.")
    if hybrid_executor is None:
        raise QueryExecutionError("A rota hybrid requer um executor híbrido.")
    structured = executar_analise_estruturada(structured_connection, analysis)
    return AdaptiveExecutionResult(
        analysis=analysis,
        plan=plan,
        structured_result=structured,
        rag_result=hybrid_executor(structured),
    )
