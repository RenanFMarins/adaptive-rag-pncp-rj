from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.corpus.model import CorpusVersion
    from app.modules.query.model import ResponseSource


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    corpus_version_id: Mapped[int] = mapped_column(
        ForeignKey("corpus_versions.id"), index=True
    )
    source_file: Mapped[str] = mapped_column(String)
    title: Mapped[str | None] = mapped_column(String)
    base_id: Mapped[str] = mapped_column(String)
    doc_type: Mapped[str] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(Text)
    sensitivity: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    corpus_version: Mapped[CorpusVersion] = relationship(back_populates="documents")
    chunks: Mapped[list[DocumentChunk]] = relationship(back_populates="document")


class DocumentCatalogEntry(Base):
    """Referência a um arquivo anunciado pelo PNCP, ainda sem texto processado.

    O catálogo não é uma fonte para FTS5/FAISS. Ele permite saber quais
    arquivos existem para uma contratação/contrato e recuperar sua URL quando
    uma futura rota adaptativa decidir solicitar o documento sob demanda.
    """

    __tablename__ = "document_catalog_entries"
    __table_args__ = (
        UniqueConstraint(
            "tipo_entidade",
            "numero_controle_pncp",
            "sequencial_documento",
            name="uq_catalogo_documento_pncp",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_entidade: Mapped[str] = mapped_column(String, index=True)
    numero_controle_pncp: Mapped[str] = mapped_column(String, index=True)
    cnpj_orgao: Mapped[str | None] = mapped_column(String)
    ano: Mapped[int | None] = mapped_column(Integer, index=True)
    sequencial_entidade: Mapped[int | None] = mapped_column(Integer)
    sequencial_documento: Mapped[int] = mapped_column(Integer)
    tipo_documento: Mapped[str | None] = mapped_column(String, index=True)
    titulo: Mapped[str | None] = mapped_column(Text)
    url_download: Mapped[str | None] = mapped_column(Text)
    uri_original: Mapped[str | None] = mapped_column(Text)
    data_publicacao_pncp: Mapped[datetime | None] = mapped_column(DateTime)
    status_ativo: Mapped[bool | None] = mapped_column(Boolean)
    periodo_coleta: Mapped[str] = mapped_column(String, index=True)
    manifesto_origem: Mapped[str] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class DocumentProcessingTaskStatus(str, Enum):
    """Estados da tarefa assíncrona de processamento documental."""

    PENDENTE = "PENDENTE"
    EM_PROCESSAMENTO = "EM_PROCESSAMENTO"
    CONCLUIDO = "CONCLUIDO"
    ERRO = "ERRO"


class DocumentProcessingTask(Base):
    """Tarefa persistente para processar um item listado no catálogo PNCP."""

    # Mantém o nome físico legado para não exigir migração nem perder tarefas já gravadas.
    __tablename__ = "document_processing_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    catalog_entry_id: Mapped[int] = mapped_column(
        ForeignKey("document_catalog_entries.id"), index=True
    )
    status: Mapped[str] = mapped_column(String, index=True)
    tentativas: Mapped[int] = mapped_column(Integer, default=0)
    erro: Mapped[str | None] = mapped_column(Text)
    motivo: Mapped[str | None] = mapped_column(String)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    catalog_entry: Mapped[DocumentCatalogEntry] = relationship()


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    # Stable external identifier for future FAISS/BM25 indexes.
    chunk_id: Mapped[str] = mapped_column(String, unique=True)
    content: Mapped[str] = mapped_column(Text)
    doc_type: Mapped[str | None] = mapped_column(String)
    base_id: Mapped[str | None] = mapped_column(String)
    sensitivity: Mapped[str | None] = mapped_column(String)
    orgao: Mapped[str | None] = mapped_column(String)
    modalidade: Mapped[str | None] = mapped_column(String)
    municipio: Mapped[str | None] = mapped_column(String)
    fornecedor: Mapped[str | None] = mapped_column(String)
    objeto: Mapped[str | None] = mapped_column(Text)
    valor: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    ano: Mapped[int | None]
    data_publicacao: Mapped[date | None] = mapped_column(Date)
    vigencia: Mapped[date | None] = mapped_column(Date)

    document: Mapped[Document] = relationship(back_populates="chunks")
    response_sources: Mapped[list[ResponseSource]] = relationship(back_populates="chunk")
