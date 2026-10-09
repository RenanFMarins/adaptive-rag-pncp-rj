from __future__ import annotations

from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

from src.retrieve import RankedChunk, retrieve_hibrido
from src.query.schemas import QueryFilters


EmbeddingFn = Callable[[str], list[float]]


def recuperar_chunks_ranqueados(
    db: Session,
    pergunta: str,
    top_k: int = 10,
    cache_dir: Path = Path("data/index/faiss"),
    embedding_fn: EmbeddingFn | None = None,
    filters: QueryFilters | None = None,
) -> list[RankedChunk]:
    kwargs = {"cache_dir": cache_dir}
    if embedding_fn is not None:
        kwargs["embedding_fn"] = embedding_fn
    if filters is not None:
        kwargs["filters"] = filters
    return retrieve_hibrido(db=db, pergunta=pergunta, top_k=top_k, **kwargs)
