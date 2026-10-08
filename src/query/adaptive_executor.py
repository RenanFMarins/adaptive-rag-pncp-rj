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
) -> AdaptiveExecutionResult:
    """Executa exclusivamente a ferramenta indicada pela rota planejada.

    A rota híbrida permanece bloqueada até existir uma política explícita para
    combinar resultados SQL e evidências documentais na geração.
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

    raise QueryExecutionError(
        "A rota 'hybrid' ainda não está integrada à combinação de evidências."
    )
