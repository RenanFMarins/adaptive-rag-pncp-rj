"""Pipeline genérica para acrescentar ``DocumentChunk`` ao FAISS.

Ela funciona com lotes PNCP (``--arquivo-chunks``) e também com documentos de
outras bases que já tenham sido persistidos no SQLite. Não altera JSONL nem
DocumentChunk: o único artefato produzido é o índice vetorial derivado.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.modules.documents.model import Document, DocumentChunk
from llm_ecoa import EMBEDDING_MODEL, gerar_embedding
from src.index import indexar_chunks_incrementalmente


def _ids_do_jsonl(caminho: Path) -> list[str]:
    if not caminho.is_file():
        raise FileNotFoundError(f"JSONL de chunks não encontrado: {caminho}")
    vistos: set[str] = set()
    ids: list[str] = []
    with caminho.open(encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            if not linha.strip():
                continue
            try:
                item = json.loads(linha)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSONL inválido na linha {numero_linha}: {caminho}") from exc
            chunk_id = item.get("chunk_id") if isinstance(item, dict) else None
            if isinstance(chunk_id, str) and chunk_id and chunk_id not in vistos:
                vistos.add(chunk_id)
                ids.append(chunk_id)
    return ids


def _chunks_por_ids(db: Session, ids: list[str]) -> list[DocumentChunk]:
    """SQLite possui limite de parâmetros; consulta IDs em grupos seguros."""

    encontrados: dict[str, DocumentChunk] = {}
    for inicio in range(0, len(ids), 500):
        grupo = ids[inicio : inicio + 500]
        consulta = select(DocumentChunk).where(DocumentChunk.chunk_id.in_(grupo))
        encontrados.update({chunk.chunk_id: chunk for chunk in db.scalars(consulta)})
    return [encontrados[chunk_id] for chunk_id in ids if chunk_id in encontrados]


def selecionar_chunks(
    db: Session,
    *,
    arquivo_chunks: Path | None,
    base_id: str | None,
    tipo: str | None,
    corpus_version_id: int | None,
    limite_chunks: int | None,
) -> list[DocumentChunk]:
    if arquivo_chunks is not None:
        chunks = _chunks_por_ids(db, _ids_do_jsonl(arquivo_chunks))
        if limite_chunks is not None:
            return chunks[:limite_chunks]
        return chunks

    consulta = select(DocumentChunk).join(Document).order_by(DocumentChunk.id)
    if base_id:
        consulta = consulta.where(DocumentChunk.base_id == base_id)
    if tipo:
        consulta = consulta.where(DocumentChunk.doc_type == tipo)
    if corpus_version_id is not None:
        consulta = consulta.where(Document.corpus_version_id == corpus_version_id)
    if limite_chunks is not None:
        consulta = consulta.limit(limite_chunks)
    return list(db.scalars(consulta))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Indexa incrementalmente DocumentChunk no FAISS."
    )
    parser.add_argument(
        "--arquivo-chunks",
        type=Path,
        help="JSONL de um lote. Indexa somente IDs presentes nele.",
    )
    parser.add_argument("--base-id", help="Seleciona chunks de uma base.")
    parser.add_argument(
        "--tipo",
        choices=["contrato", "contratacao"],
        help="Seleciona o tipo documental persistido.",
    )
    parser.add_argument("--corpus-version-id", type=int)
    parser.add_argument("--limite-chunks", type=int)
    parser.add_argument("--tamanho-lote", type=int, default=50)
    parser.add_argument(
        "--indice-dir",
        type=Path,
        default=Path("data/index/faiss/v1"),
    )
    parser.add_argument(
        "--origem",
        help="Rótulo auditável da execução, por exemplo 2026_08_lote_001.",
    )
    args = parser.parse_args()

    if args.limite_chunks is not None and args.limite_chunks <= 0:
        parser.error("--limite-chunks deve ser maior que zero.")

    init_db()
    with SessionLocal() as db:
        chunks = selecionar_chunks(
            db,
            arquivo_chunks=args.arquivo_chunks,
            base_id=args.base_id,
            tipo=args.tipo,
            corpus_version_id=args.corpus_version_id,
            limite_chunks=args.limite_chunks,
        )

    if not chunks:
        print("Nenhum DocumentChunk selecionado para indexação.")
        return

    origem = args.origem or (
        args.arquivo_chunks.name if args.arquivo_chunks else "selecao_por_filtros"
    )
    print(
        "FAISS incremental | "
        f"selecionados={len(chunks)} | índice={args.indice_dir} | origem={origem}"
    )
    colunas = [
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TextColumn("{task.percentage:>5.1f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ]
    with Progress(*colunas) as progresso_visual:
        tarefa = progresso_visual.add_task("Gerando embeddings", total=1)

        def atualizar(processados: int, total: int) -> None:
            progresso_visual.update(tarefa, total=total, completed=processados)

        _, resumo = indexar_chunks_incrementalmente(
            [(chunk.chunk_id, chunk.content) for chunk in chunks],
            gerar_embedding,
            args.indice_dir,
            tamanho_lote=args.tamanho_lote,
            modelo_embedding=EMBEDDING_MODEL,
            origem=origem,
            progresso=atualizar,
        )
        if resumo.novos == 0:
            progresso_visual.update(
                tarefa,
                description="Nenhum chunk novo",
                total=1,
                completed=1,
            )
        else:
            progresso_visual.update(
                tarefa,
                total=resumo.novos,
                completed=resumo.novos,
            )

    print(
        "Indexação concluída | "
        f"selecionados={resumo.selecionados} | já_indexados={resumo.ja_indexados} | "
        f"novos={resumo.novos} | total_indice={resumo.total_no_indice}"
    )


if __name__ == "__main__":
    main()
