"""Índice FAISS incremental para os ``DocumentChunk`` persistidos.

O SQLite é a fonte de verdade do texto e dos metadados. Este módulo persiste
somente vetores e o mapeamento posição -> ``chunk_id``. Assim, o índice pode
ser reconstruído sem alterar o corpus e uma nova execução indexa apenas os
chunks ainda ausentes.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import faiss
import numpy as np


EmbeddingFn = Callable[[str], list[float]]
ProgressFn = Callable[[int, int], None]

ARQUIVO_INDICE = "chunks.faiss"
ARQUIVO_IDS = "chunk_ids.json"
ARQUIVO_ESTADO = "estado_indexacao.json"
ESQUEMA_INDICE = "faiss_document_chunks_v1"


def _normalizar(vetores: np.ndarray) -> np.ndarray:
    normas = np.linalg.norm(vetores, axis=1, keepdims=True)
    normas[normas == 0] = 1.0
    return vetores / normas


def _agora_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _salvar_json_atomico(caminho: Path, valor: object) -> None:
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    temporario.write_text(
        json.dumps(valor, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temporario, caminho)


@dataclass(frozen=True)
class FaissChunkIndex:
    index: faiss.Index
    chunk_ids: list[str]

    def search(self, query_embedding: list[float], top_k: int) -> list[tuple[str, float]]:
        if not self.chunk_ids or top_k <= 0:
            return []
        consulta = np.array([query_embedding], dtype="float32")
        consulta = _normalizar(consulta)
        scores, indices = self.index.search(consulta, min(top_k, len(self.chunk_ids)))
        resultados: list[tuple[str, float]] = []
        for posicao, score in zip(indices[0], scores[0]):
            if posicao < 0:
                continue
            resultados.append((self.chunk_ids[int(posicao)], float(score)))
        return resultados


@dataclass(frozen=True)
class ResumoIndexacaoFaiss:
    selecionados: int
    ja_indexados: int
    novos: int
    total_no_indice: int
    diretorio_indice: str


def _caminhos(cache_dir: Path) -> tuple[Path, Path, Path]:
    return (
        cache_dir / ARQUIVO_INDICE,
        cache_dir / ARQUIVO_IDS,
        cache_dir / ARQUIVO_ESTADO,
    )


def carregar_indice_faiss(cache_dir: Path) -> FaissChunkIndex:
    """Carrega um índice pronto, sem gerar embeddings ou reconstruir dados."""

    index_path, ids_path, _ = _caminhos(cache_dir)
    if not index_path.is_file() or not ids_path.is_file():
        raise FileNotFoundError(
            "Índice FAISS ausente. Execute primeiro a pipeline de indexação "
            f"para criar: {cache_dir}"
        )

    chunk_ids = json.loads(ids_path.read_text(encoding="utf-8"))
    if not isinstance(chunk_ids, list) or not all(isinstance(item, str) for item in chunk_ids):
        raise RuntimeError(f"Mapa de chunk_ids inválido: {ids_path}")
    index = faiss.read_index(str(index_path))
    if index.ntotal != len(chunk_ids):
        raise RuntimeError(
            "Índice FAISS e mapa de chunk_ids estão inconsistentes. "
            "Reconstrua o índice em um novo diretório de versão."
        )
    return FaissChunkIndex(index=index, chunk_ids=chunk_ids)


def _carregar_estado(cache_dir: Path) -> dict[str, object]:
    _, _, estado_path = _caminhos(cache_dir)
    if not estado_path.is_file():
        return {}
    estado = json.loads(estado_path.read_text(encoding="utf-8"))
    return estado if isinstance(estado, dict) else {}


def _salvar_indice(
    cache_dir: Path,
    indice: FaissChunkIndex,
    *,
    modelo_embedding: str | None,
    origem: str | None,
) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    index_path, ids_path, estado_path = _caminhos(cache_dir)
    index_temporario = index_path.with_suffix(index_path.suffix + ".tmp")
    faiss.write_index(indice.index, str(index_temporario))
    os.replace(index_temporario, index_path)
    _salvar_json_atomico(ids_path, indice.chunk_ids)

    estado_anterior = _carregar_estado(cache_dir)
    origens = estado_anterior.get("origens", [])
    if not isinstance(origens, list):
        origens = []
    if origem and origem not in origens:
        origens.append(origem)
    estado = {
        "esquema": ESQUEMA_INDICE,
        "modeloEmbedding": modelo_embedding or estado_anterior.get("modeloEmbedding"),
        "dimensao": int(indice.index.d),
        "totalVetores": int(indice.index.ntotal),
        "atualizadoEm": _agora_utc(),
        "origens": origens,
    }
    _salvar_json_atomico(estado_path, estado)


def _validar_modelo(cache_dir: Path, modelo_embedding: str | None) -> None:
    if not modelo_embedding:
        return
    modelo_anterior = _carregar_estado(cache_dir).get("modeloEmbedding")
    if modelo_anterior and modelo_anterior != modelo_embedding:
        raise RuntimeError(
            "O índice foi criado com outro modelo de embedding "
            f"({modelo_anterior!r}). Use um novo diretório de índice ou "
            "reconstrua conscientemente o corpus."
        )


def _deduplicar_chunks(chunks: list[tuple[str, str]]) -> list[tuple[str, str]]:
    vistos: set[str] = set()
    resultado: list[tuple[str, str]] = []
    for chunk_id, conteudo in chunks:
        if not chunk_id or chunk_id in vistos:
            continue
        vistos.add(chunk_id)
        resultado.append((chunk_id, conteudo))
    return resultado


def indexar_chunks_incrementalmente(
    chunks: list[tuple[str, str]],
    gerar_embedding: EmbeddingFn,
    cache_dir: Path,
    *,
    tamanho_lote: int = 50,
    modelo_embedding: str | None = None,
    origem: str | None = None,
    progresso: ProgressFn | None = None,
) -> tuple[FaissChunkIndex, ResumoIndexacaoFaiss]:
    """Acrescenta ao FAISS somente chunks ainda não presentes no índice.

    Cada lote concluído é salvo em disco. Portanto uma interrupção perde, no
    máximo, o lote em andamento; uma nova execução retoma pelos ``chunk_id``
    ainda ausentes.
    """

    if tamanho_lote <= 0:
        raise ValueError("tamanho_lote deve ser maior que zero.")

    selecionados = _deduplicar_chunks(chunks)
    cache_dir.mkdir(parents=True, exist_ok=True)
    index_path, ids_path, _ = _caminhos(cache_dir)
    if index_path.exists() or ids_path.exists():
        indice = carregar_indice_faiss(cache_dir)
        _validar_modelo(cache_dir, modelo_embedding)
    else:
        indice = None

    ids_existentes = set(indice.chunk_ids) if indice else set()
    pendentes = [item for item in selecionados if item[0] not in ids_existentes]
    ja_indexados = len(selecionados) - len(pendentes)

    if not pendentes:
        if indice is None:
            raise ValueError("Não há chunks válidos para indexar.")
        return indice, ResumoIndexacaoFaiss(
            selecionados=len(selecionados),
            ja_indexados=ja_indexados,
            novos=0,
            total_no_indice=len(indice.chunk_ids),
            diretorio_indice=str(cache_dir),
        )

    processados = 0
    for inicio in range(0, len(pendentes), tamanho_lote):
        lote = pendentes[inicio : inicio + tamanho_lote]
        vetores = np.array(
            [gerar_embedding(conteudo) for _, conteudo in lote],
            dtype="float32",
        )
        if vetores.ndim != 2 or vetores.shape[0] != len(lote):
            raise RuntimeError("O gerador de embeddings retornou vetores inválidos.")
        vetores = _normalizar(vetores)

        if indice is None:
            indice = FaissChunkIndex(
                index=faiss.IndexFlatIP(vetores.shape[1]),
                chunk_ids=[],
            )
        elif indice.index.d != vetores.shape[1]:
            raise RuntimeError(
                "A dimensão dos embeddings novos difere da dimensão do índice. "
                "Use um novo diretório de índice."
            )

        indice.index.add(vetores)
        indice.chunk_ids.extend(chunk_id for chunk_id, _ in lote)
        processados += len(lote)
        _salvar_indice(
            cache_dir,
            indice,
            modelo_embedding=modelo_embedding,
            origem=origem,
        )
        if progresso is not None:
            progresso(processados, len(pendentes))

    assert indice is not None
    return indice, ResumoIndexacaoFaiss(
        selecionados=len(selecionados),
        ja_indexados=ja_indexados,
        novos=len(pendentes),
        total_no_indice=len(indice.chunk_ids),
        diretorio_indice=str(cache_dir),
    )


# Mantida por compatibilidade temporária com o MVP anterior. Novos fluxos devem
# chamar ``indexar_chunks_incrementalmente`` durante a ingestão, nunca durante
# uma consulta de usuário.
def load_or_build_faiss_index(
    chunks: list[tuple[str, str]],
    gerar_embedding: EmbeddingFn,
    cache_dir: Path,
) -> FaissChunkIndex:
    indice, _ = indexar_chunks_incrementalmente(
        chunks,
        gerar_embedding,
        cache_dir,
    )
    return indice
