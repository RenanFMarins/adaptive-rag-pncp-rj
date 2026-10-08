"""Contratos validados entre Query Analyzer, Planner e ferramentas.

Este módulo não executa SQL, retrieval nem chamadas à LLM. Ele representa
somente o plano que será produzido pelo Query Analyzer e consumido pelo
Planner/Router nas etapas seguintes.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QueryRoute(str, Enum):
    """Estratégias de execução previstas para uma pergunta."""

    STRUCTURED = "structured"
    RAG = "rag"
    HYBRID = "hybrid"


class ExecutionTool(str, Enum):
    """Ferramentas internas permitidas no plano de execução."""

    STRUCTURED_DATABASE = "structured_database"
    RAG_RETRIEVAL = "rag_retrieval"


class QueryIntent(str, Enum):
    """Intenções de alto nível reconhecidas pelo Analyzer."""

    AGGREGATE = "aggregate"
    LOOKUP = "lookup"
    DOCUMENTAL = "documental"
    COMPARISON = "comparison"


class QueryEntity(str, Enum):
    """Entidades públicas que podem ser consultadas."""

    CONTRATO = "contrato"
    CONTRATACAO = "contratacao"
    DOCUMENTO = "documento"


class KnowledgeBase(str, Enum):
    """Bases de evidência previstas na arquitetura Adaptive RAG."""

    ESTRUTURADA = "estruturada"
    NORMATIVA = "normativa"
    CONVERSACIONAL = "conversacional"
    AGREGADA = "agregada"


class StructuredOperation(str, Enum):
    """Operações permitidas para a futura Structured DB Tool."""

    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    GROUP_BY = "group_by"
    ORDER_BY = "order_by"
    LIST = "list"


class StructuredField(str, Enum):
    """Campos públicos que poderão ser mapeados pela SQL Tool."""

    VALOR_GLOBAL = "valor_global"
    VALOR_ESTIMADO = "valor_estimado"
    ANO = "ano"
    DATA_PUBLICACAO = "data_publicacao"
    MUNICIPIO = "municipio"
    ORGAO = "orgao"
    FORNECEDOR = "fornecedor"
    MODALIDADE = "modalidade"
    OBJETO = "objeto"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class OrderBy(BaseModel):
    """Uma ordenação declarativa, sem conter SQL livre."""

    model_config = ConfigDict(extra="forbid")

    field: StructuredField
    direction: SortDirection = SortDirection.DESC


class QueryFilters(BaseModel):
    """Filtros extraídos da pergunta e reutilizados por SQL e RAG."""

    model_config = ConfigDict(extra="forbid")

    numero_controle_pncp: str | None = None
    document_id: int | None = Field(default=None, ge=1)
    tipo_entidade: QueryEntity | None = None
    tipo_documento: str | None = None
    orgao: str | None = None
    municipio: str | None = None
    fornecedor: str | None = None
    modalidade: str | None = None
    ano: int | None = Field(default=None, ge=2000, le=2100)
    period_start: date | None = None
    period_end: date | None = None
    valor_minimo: float | None = Field(default=None, ge=0)
    valor_maximo: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validar_intervalos(self) -> "QueryFilters":
        if self.period_start and self.period_end and self.period_start > self.period_end:
            raise ValueError("period_start não pode ser posterior a period_end.")
        if (
            self.valor_minimo is not None
            and self.valor_maximo is not None
            and self.valor_minimo > self.valor_maximo
        ):
            raise ValueError("valor_minimo não pode ser maior que valor_maximo.")
        return self


class QueryAnalysis(BaseModel):
    """Plano validado que será entregue pelo Query Analyzer ao Planner."""

    model_config = ConfigDict(extra="forbid")

    route: QueryRoute
    intent: QueryIntent
    entity: QueryEntity
    bases: list[KnowledgeBase] = Field(min_length=1)
    filters: QueryFilters = Field(default_factory=QueryFilters)
    operations: list[StructuredOperation] = Field(default_factory=list)
    aggregation_field: StructuredField | None = None
    group_by: list[StructuredField] = Field(default_factory=list)
    order_by: list[OrderBy] = Field(default_factory=list)
    limit: int | None = Field(default=None, ge=1, le=100)
    semantic_query: str | None = None
    needs_document_retrieval: bool = False

    @model_validator(mode="after")
    def validar_plano(self) -> "QueryAnalysis":
        if len(set(self.operations)) != len(self.operations):
            raise ValueError("operations não pode conter operações duplicadas.")

        operacoes_agregadas = {
            StructuredOperation.SUM,
            StructuredOperation.AVG,
            StructuredOperation.MIN,
            StructuredOperation.MAX,
        }
        if operacoes_agregadas.intersection(self.operations) and not self.aggregation_field:
            raise ValueError(
                "aggregation_field é obrigatório para sum, avg, min ou max."
            )
        if self.group_by and StructuredOperation.GROUP_BY not in self.operations:
            raise ValueError("group_by exige a operação group_by.")
        if StructuredOperation.GROUP_BY in self.operations and not self.group_by:
            raise ValueError("A operação group_by exige ao menos um campo.")
        if self.order_by and StructuredOperation.ORDER_BY not in self.operations:
            raise ValueError("order_by exige a operação order_by.")

        if self.route is QueryRoute.STRUCTURED:
            if KnowledgeBase.ESTRUTURADA not in self.bases:
                raise ValueError("A rota structured exige a base estruturada.")
            if self.needs_document_retrieval:
                raise ValueError(
                    "A rota structured não deve solicitar recuperação documental."
                )
        elif self.route is QueryRoute.RAG:
            if self.operations:
                raise ValueError("A rota rag não aceita operações estruturadas.")
            if not self.needs_document_retrieval:
                raise ValueError(
                    "A rota rag exige needs_document_retrieval igual a true."
                )
        elif self.route is QueryRoute.HYBRID:
            if KnowledgeBase.ESTRUTURADA not in self.bases:
                raise ValueError("A rota hybrid exige a base estruturada.")
            if not self.needs_document_retrieval:
                raise ValueError(
                    "A rota hybrid exige needs_document_retrieval igual a true."
                )

        return self


class ExecutionPlan(BaseModel):
    """Plano determinístico que o Router executará em uma etapa posterior."""

    model_config = ConfigDict(extra="forbid")

    route: QueryRoute
    tools: list[ExecutionTool] = Field(min_length=1)
    analysis: QueryAnalysis

    @model_validator(mode="after")
    def validar_consistencia(self) -> "ExecutionPlan":
        if self.route is not self.analysis.route:
            raise ValueError("route deve corresponder à rota da análise.")

        ferramentas_por_rota = {
            QueryRoute.STRUCTURED: [ExecutionTool.STRUCTURED_DATABASE],
            QueryRoute.RAG: [ExecutionTool.RAG_RETRIEVAL],
            QueryRoute.HYBRID: [
                ExecutionTool.STRUCTURED_DATABASE,
                ExecutionTool.RAG_RETRIEVAL,
            ],
        }
        ferramentas_esperadas = ferramentas_por_rota[self.route]
        if self.tools != ferramentas_esperadas:
            raise ValueError(
                "tools deve conter, na ordem definida, as ferramentas da rota."
            )
        return self
