from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import faiss
import numpy as np


EmbeddingFn = Callable[[str], list[float]]


def _normalizar(vetores: np.ndarray) -> np.ndarray:
    normas = np.linalg.norm(vetores, axis=1, keepdims=True)
    normas[normas == 0] = 1.0
    return vetores / normas


class FaissChunkIndex:
    def __init__(self, index: faiss.Index, chunk_ids: list[str]):
        self.index = index
        self.chunk_ids = chunk_ids

    def search(self, query_embedding: list[float], top_k: int) -> list[tuple[str, float]]:
        consulta = np.array([query_embedding], dtype="float32")
        consulta = _normalizar(consulta)
        scores, indices = self.index.search(consulta, min(top_k, len(self.chunk_ids)))
        resultados: list[tuple[str, float]] = []
        for posicao, score in zip(indices[0], scores[0]):
            if posicao < 0:
                continue
            resultados.append((self.chunk_ids[int(posicao)], float(score)))
        return resultados


def build_faiss_index(
    chunks: list[tuple[str, str]],
    gerar_embedding: EmbeddingFn,
) -> FaissChunkIndex:
    if not chunks:
        raise ValueError("Nao ha chunks para indexar.")

    chunk_ids = [chunk_id for chunk_id, _ in chunks]
    embeddings = np.array(
        [gerar_embedding(content) for _, content in chunks],
        dtype="float32",
    )
    embeddings = _normalizar(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    return FaissChunkIndex(index=index, chunk_ids=chunk_ids)


def load_or_build_faiss_index(
    chunks: list[tuple[str, str]],
    gerar_embedding: EmbeddingFn,
    cache_dir: Path,
) -> FaissChunkIndex:
    cache_dir.mkdir(parents=True, exist_ok=True)
    index_path = cache_dir / "chunks.faiss"
    ids_path = cache_dir / "chunk_ids.json"
    chunk_ids = [chunk_id for chunk_id, _ in chunks]

    if index_path.exists() and ids_path.exists():
        cached_ids = json.loads(ids_path.read_text(encoding="utf-8"))
        if cached_ids == chunk_ids:
            return FaissChunkIndex(
                index=faiss.read_index(str(index_path)),
                chunk_ids=cached_ids,
            )

    dense_index = build_faiss_index(chunks, gerar_embedding)
    faiss.write_index(dense_index.index, str(index_path))
    ids_path.write_text(json.dumps(chunk_ids, ensure_ascii=False), encoding="utf-8")
    return dense_index
