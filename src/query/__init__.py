"""Contratos e componentes técnicos para análise de perguntas."""

from .analyzer import QueryAnalysisError, analisar_pergunta
from .planner import planejar_execucao
from .schemas import (
    ExecutionPlan,
    ExecutionTool,
    QueryAnalysis,
    QueryFilters,
    QueryRoute,
)

__all__ = [
    "ExecutionPlan",
    "ExecutionTool",
    "QueryAnalysis",
    "QueryAnalysisError",
    "QueryFilters",
    "QueryRoute",
    "analisar_pergunta",
    "planejar_execucao",
]
