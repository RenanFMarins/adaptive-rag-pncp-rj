"""Contratos e componentes técnicos para análise de perguntas."""

from .analyzer import QueryAnalysisError, analisar_pergunta
from .planner import planejar_execucao
from .schemas import (
    ExecutionPlan,
    ExecutionTool,
    QueryAnalysis,
    QueryFilters,
    QueryRoute,
    StructuredQueryResult,
)
from .structured_tool import StructuredQueryError, executar_consulta_estruturada

__all__ = [
    "ExecutionPlan",
    "ExecutionTool",
    "QueryAnalysis",
    "QueryAnalysisError",
    "QueryFilters",
    "QueryRoute",
    "StructuredQueryError",
    "StructuredQueryResult",
    "analisar_pergunta",
    "executar_consulta_estruturada",
    "planejar_execucao",
]
