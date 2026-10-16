"""Contratos HTTP para tarefas de processamento de documentos."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.documents.model import DocumentProcessingTaskStatus


class ProcessingTaskRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    motivo: str = Field(default="solicitacao_usuario", max_length=200)


class ProcessingTaskResponse(BaseModel):
    """Estado de uma tarefa de processamento documental."""

    id: int
    catalog_entry_id: int
    status: DocumentProcessingTaskStatus
    tentativas: int
    erro: str | None = None
    motivo: str | None = None
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None
    created: bool = False
    retried: bool = False
