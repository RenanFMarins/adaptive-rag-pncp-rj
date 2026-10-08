from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Route = Literal["structured", "rag", "hybrid"]

Intent = Literal[
    "lookup",
    "aggregate",
    "comparison",
    "ranking",
    "document_question",
    "normative_question",
    "conversational_question",
    "unknown",
]

Entity = Literal[
    "contratos",
    "contratacoes",
    "itens_contratacao",
    "resultados_item",
    "pca",
    "documentos",
    "atas",
    "emails",
    "fornecedores",
    "orgaos",
    "municipios",
    "normas",
    "unknown",
]


class QueryFilters(BaseModel):
    model_config = ConfigDict(extra="allow")

    periodo_inicio: date | None = None
    periodo_fim: date | None = None

    ano: int | None = None
    mes: int | None = Field(default=None, ge=1, le=12)

    municipio: str | None = None
    uf: str | None = None

    orgao: str | None = None
    fornecedor: str | None = None

    modalidade: str | None = None

    numero_contrato: str | None = None
    numero_controle_pncp: str | None = None

    termos: list[str] = Field(default_factory=list)


class QueryAnalysis(BaseModel):
    """
    Resultado padronizado da análise de uma pergunta.

    O Analyzer interpreta a pergunta, mas não executa SQL,
    não realiza retrieval e não gera a resposta final.
    """

    model_config = ConfigDict(extra="forbid")

    route: Route
    intent: Intent
    entity: Entity

    operation: str | None = None
    field: str | None = None

    filters: QueryFilters = Field(default_factory=QueryFilters)

    bases: list[str] = Field(default_factory=list)

    requires_sql: bool = False
    requires_rag: bool = False

    reasoning: str = ""

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    original_question: str

    metadata: dict[str, Any] = Field(default_factory=dict)