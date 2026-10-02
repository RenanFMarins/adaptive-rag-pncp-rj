from __future__ import annotations

import re
import json
import argparse
from dataclasses import asdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Callable

from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.documents.model import DocumentChunk
from llm_ecoa import gerar_embedding
from src.index import load_or_build_faiss_index


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


def _tokenizar(texto: str) -> list[str]:
    return re.findall(r"\w+", texto.lower())


def _score_decimal(valor: Decimal | None) -> float | None:
    return float(valor) if valor is not None else None


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
    }


def carregar_chunks(db: Session, limite: int | None = None) -> list[DocumentChunk]:
    query = select(DocumentChunk).order_by(DocumentChunk.id)
    if limite is not None:
        query = query.limit(limite)
    return list(db.scalars(query))


def buscar_bm25(
    pergunta: str,
    chunks: list[DocumentChunk],
    top_k: int,
) -> list[tuple[str, float]]:
    if not chunks:
        return []
    corpus = [_tokenizar(chunk.content) for chunk in chunks]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(_tokenizar(pergunta))
    ordenados = sorted(
        zip(chunks, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )
    return [
        (chunk.chunk_id, float(score))
        for chunk, score in ordenados[:top_k]
        if float(score) > 0
    ]


def buscar_dense(
    pergunta: str,
    chunks: list[DocumentChunk],
    top_k: int,
    cache_dir: Path,
    embedding_fn: EmbeddingFn = gerar_embedding,
) -> list[tuple[str, float]]:
    if not chunks:
        return []
    index = load_or_build_faiss_index(
        [(chunk.chunk_id, chunk.content) for chunk in chunks],
        embedding_fn,
        cache_dir,
    )
    return index.search(embedding_fn(pergunta), top_k)


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
) -> list[RankedChunk]:
    chunks = carregar_chunks(db)
    por_chunk_id = {chunk.chunk_id: chunk for chunk in chunks}

    bm25 = buscar_bm25(pergunta, chunks, bm25_k)
    dense = buscar_dense(pergunta, chunks, dense_k, cache_dir, embedding_fn)
    fused = reciprocal_rank_fusion([bm25, dense], k=rrf_k)

    bm25_rank = {chunk_id: rank for rank, (chunk_id, _) in enumerate(bm25, start=1)}
    bm25_score = dict(bm25)
    dense_rank = {chunk_id: rank for rank, (chunk_id, _) in enumerate(dense, start=1)}
    dense_score = dict(dense)

    ordenados = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:top_k]
    resultados: list[RankedChunk] = []
    for chunk_id, rrf_score in ordenados:
        chunk = por_chunk_id[chunk_id]
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

    parser = argparse.ArgumentParser(description="Executa retrieval hibrido sobre DocumentChunk.")
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
