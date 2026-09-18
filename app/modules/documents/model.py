from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
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
    base_id: Mapped[str] = mapped_column(String)
    doc_type: Mapped[str] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(Text)
    sensitivity: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    corpus_version: Mapped[CorpusVersion] = relationship(back_populates="documents")
    chunks: Mapped[list[DocumentChunk]] = relationship(back_populates="document")


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
