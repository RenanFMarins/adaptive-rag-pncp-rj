"""Orquestra a rota estruturada entre Analyzer, Planner e SQLite."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable

from .analyzer import analisar_pergunta
from .planner import planejar_execucao
from .schemas import AdaptiveQueryResult, QueryAnalysis, QueryRoute
from .structured_tool import executar_consulta_estruturada


AnalyzerFn = Callable[[str], QueryAnalysis]


class QueryExecutionError(RuntimeError):
    """Indica que a rota planejada ainda não possui executor integrado."""


def executar_consulta_adaptativa(
    connection: sqlite3.Connection,
    pergunta: str,
    analyzer_fn: AnalyzerFn = analisar_pergunta,
) -> AdaptiveQueryResult:
    """Executa a rota estruturada de ponta a ponta.

    As rotas ``rag`` e ``hybrid`` permanecem explicitamente bloqueadas aqui até
    a próxima etapa, quando o Retriever e a combinação de evidências forem
    integrados. Isso evita que uma pergunta seja respondida por uma ferramenta
    diferente daquela definida pelo Planner.
    """

    analysis = analyzer_fn(pergunta)
    return executar_analise_estruturada(connection, analysis)


def executar_analise_estruturada(
    connection: sqlite3.Connection,
    analysis: QueryAnalysis,
) -> AdaptiveQueryResult:
    """Executa uma análise estruturada já pronta, sem chamar a LLM novamente."""

    plan = planejar_execucao(analysis)
    if plan.route is not QueryRoute.STRUCTURED:
        raise QueryExecutionError(
            f"A rota '{plan.route.value}' ainda não está integrada ao executor."
        )

    structured_result = executar_consulta_estruturada(connection, analysis)
    return AdaptiveQueryResult(
        analysis=analysis,
        plan=plan,
        structured_result=structured_result,
    )
