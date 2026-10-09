"""Retrieval híbrido: SQLite FTS5 + FAISS incremental + RRF.

Esta etapa só consulta índices prontos. A criação de embeddings e a inclusão
de novos vetores pertencem à
``base_estruturada.pipelines.pipeline_indexacao_faiss``.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from typing import Callable

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.documents.model import Document, DocumentChunk
from llm_ecoa import gerar_embedding
from src.fts import buscar_fts5
from src.index import carregar_indice_faiss
from src.query.schemas import QueryEntity, QueryFilters


EmbeddingFn = Callable[[str], list[float]]


@dataclass(frozen=True)
class RankedChunk:
    chunk_id: str
    content: str
    rrf_score: float
    bm25_rank: int | None
    bm25_score: float | None
    dense_rank: int | None
    dense_score: float | None
    metadata: dict[str, object]


def _score_decimal(valor: Decimal | None) -> float | None:
    return float(valor) if valor is not None else None


def _numero_controle_pncp(chunk: DocumentChunk) -> str | None:
    """Recupera o identificador PNCP do formato estável de ``source_file``."""

    if chunk.document.base_id != "pncp_rj_estruturada":
        return None
    partes = chunk.document.source_file.split("|")
    if len(partes) < 4 or not partes[2]:
        return None
    return partes[2]


def _metadata(chunk: DocumentChunk) -> dict[str, object]:
    return {
        "id": chunk.id,
        "doc_type": chunk.doc_type or chunk.document.doc_type,
        "base_id": chunk.base_id or chunk.document.base_id,
        "sensitivity": chunk.sensitivity or chunk.document.sensitivity,
        "orgao": chunk.orgao,
        "modalidade": chunk.modalidade,
        "municipio": chunk.municipio,
        "fornecedor": chunk.fornecedor,
        "objeto": chunk.objeto,
        "valor": _score_decimal(chunk.valor),
        "ano": chunk.ano,
        "data_publicacao": chunk.data_publicacao.isoformat()
        if chunk.data_publicacao
        else None,
        "vigencia": chunk.vigencia.isoformat() if chunk.vigencia else None,
        "document_id": chunk.document_id,
        "numeroControlePNCP": _numero_controle_pncp(chunk),
        "tituloDocumento": chunk.document.title,
        "urlFontePncp": chunk.document.source_url,
    }


def carregar_chunks_por_ids(
    db: Session,
    chunk_ids: list[str],
) -> dict[str, DocumentChunk]:
    """Carrega apenas os chunks vencedores dos índices."""

    if not chunk_ids:
        return {}
    consulta = (
        select(DocumentChunk)
        .options(selectinload(DocumentChunk.document))
        .where(DocumentChunk.chunk_id.in_(chunk_ids))
    )
    return {chunk.chunk_id: chunk for chunk in db.scalars(consulta)}


def buscar_dense(
    pergunta: str,
    top_k: int,
    cache_dir: Path,
    embedding_fn: EmbeddingFn = gerar_embedding,
    allowed_chunk_ids: set[str] | None = None,
) -> list[tuple[str, float]]:
    """Consulta somente um FAISS já indexado; nunca o reconstrói."""

    if top_k <= 0:
        return []
    indice = carregar_indice_faiss(cache_dir)
    if allowed_chunk_ids is None:
        return indice.search(embedding_fn(pergunta), top_k)
    if not allowed_chunk_ids:
        return []

    # O IndexFlat do FAISS não oferece filtro por metadados. Para manter a
    # correção do recorte, ordenamos o índice e só então preservamos IDs
    # autorizados pelo SQLite. Não há reconstrução nem gravação do índice.
    ranking_completo = indice.search(embedding_fn(pergunta), len(indice.chunk_ids))
    return [
        (chunk_id, score)
        for chunk_id, score in ranking_completo
        if chunk_id in allowed_chunk_ids
    ][:top_k]


def resolver_chunk_ids_filtrados(
    db: Session,
    filters: QueryFilters | None,
) -> set[str] | None:
    """Resolve no SQLite os IDs de chunks permitidos pelos filtros da pergunta."""

    if filters is None or not filters.model_fields_set:
        return None

    query = select(DocumentChunk.chunk_id).join(DocumentChunk.document)
    if filters.numero_controle_pncp:
        query = query.where(
            Document.source_file.contains(f"|{filters.numero_controle_pncp}|")
        )
    if filters.document_id is not None:
        query = query.where(DocumentChunk.document_id == filters.document_id)
    if filters.tipo_entidade and filters.tipo_entidade is not QueryEntity.DOCUMENTO:
        query = query.where(Document.doc_type == filters.tipo_entidade.value)
    if filters.tipo_documento:
        query = query.where(
            func.lower(Document.title).like(f"%{filters.tipo_documento.lower()}%")
        )

    text_filters = (
        (DocumentChunk.orgao, filters.orgao),
        (DocumentChunk.municipio, filters.municipio),
        (DocumentChunk.fornecedor, filters.fornecedor),
        (DocumentChunk.modalidade, filters.modalidade),
    )
    for column, value in text_filters:
        if value:
            query = query.where(func.lower(column).like(f"%{value.lower()}%"))

    if filters.ano is not None:
        query = query.where(DocumentChunk.ano == filters.ano)
    if filters.period_start:
        query = query.where(DocumentChunk.data_publicacao >= filters.period_start)
    if filters.period_end:
        query = query.where(DocumentChunk.data_publicacao <= filters.period_end)
    if filters.valor_minimo is not None:
        query = query.where(DocumentChunk.valor >= filters.valor_minimo)
    if filters.valor_maximo is not None:
        query = query.where(DocumentChunk.valor <= filters.valor_maximo)

    return set(db.scalars(query))


def reciprocal_rank_fusion(
    rankings: list[list[tuple[str, float]]],
    k: int = 60,
) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for posicao, (chunk_id, _) in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + posicao)
    return scores


def retrieve_hibrido(
    db: Session,
    pergunta: str,
    top_k: int = 10,
    bm25_k: int = 20,
    dense_k: int = 20,
    rrf_k: int = 60,
    cache_dir: Path = Path("data/index/faiss"),
    embedding_fn: EmbeddingFn = gerar_embedding,
    filters: QueryFilters | None = None,
) -> list[RankedChunk]:
    """Combina ranking lexical persistente e ranking semântico vetorial."""

    allowed_chunk_ids = resolver_chunk_ids_filtrados(db, filters)
    if allowed_chunk_ids is not None and not allowed_chunk_ids:
        return []

    lexical = buscar_fts5(
        db,
        pergunta,
        bm25_k,
        allowed_chunk_ids=allowed_chunk_ids,
    )
    dense = buscar_dense(
        pergunta,
        dense_k,
        cache_dir,
        embedding_fn,
        allowed_chunk_ids=allowed_chunk_ids,
    )
    fused = reciprocal_rank_fusion([lexical, dense], k=rrf_k)

    bm25_rank = {chunk_id: rank for rank, (chunk_id, _) in enumerate(lexical, start=1)}
    bm25_score = dict(lexical)
    dense_rank = {chunk_id: rank for rank, (chunk_id, _) in enumerate(dense, start=1)}
    dense_score = dict(dense)
    ordenados = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:top_k]
    chunks = carregar_chunks_por_ids(db, [chunk_id for chunk_id, _ in ordenados])

    resultados: list[RankedChunk] = []
    for chunk_id, rrf_score in ordenados:
        chunk = chunks.get(chunk_id)
        # Um ID pode permanecer em um FAISS antigo se o banco foi limpo ou se
        # houve troca de corpus. Ignorar evita retornar evidência inexistente.
        if chunk is None:
            continue
        resultados.append(
            RankedChunk(
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                rrf_score=rrf_score,
                bm25_rank=bm25_rank.get(chunk_id),
                bm25_score=bm25_score.get(chunk_id),
                dense_rank=dense_rank.get(chunk_id),
                dense_score=dense_score.get(chunk_id),
                metadata=_metadata(chunk),
            )
        )
    return resultados


if __name__ == "__main__":
    from app.core.database import SessionLocal, init_db

    parser = argparse.ArgumentParser(description="Executa retrieval híbrido sobre DocumentChunk.")
    parser.add_argument("pergunta")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--cache-dir", default="data/index/faiss")
    args = parser.parse_args()

    init_db()
    with SessionLocal() as db:
        resultados = retrieve_hibrido(
            db=db,
            pergunta=args.pergunta,
            top_k=args.top_k,
            cache_dir=Path(args.cache_dir),
        )
    print(json.dumps([asdict(item) for item in resultados], ensure_ascii=False, indent=2))
