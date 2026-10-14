"""Persiste a base normativa já processada no SQLite, sem embeddings/FAISS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.core.database import SessionLocal, init_db
from app.modules.documents.services import persistir_chunks_jsonl_normativos


def _urls_por_arquivo(caminho_inventario: Path) -> dict[str, str]:
    if not caminho_inventario.is_file():
        return {}
    registros = json.loads(caminho_inventario.read_text(encoding="utf-8"))
    if not isinstance(registros, list):
        return {}
    return {
        Path(str(item.get("path", ""))).name: str(item["origem"])
        for item in registros
        if isinstance(item, dict) and item.get("path") and item.get("origem")
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Persiste JSONL normativo no SQLite, sem FAISS."
    )
    parser.add_argument("--versao", default="v1")
    parser.add_argument("--arquivo-chunks", type=Path)
    parser.add_argument("--inventario", type=Path)
    parser.add_argument("--corpus-version-id", type=int, default=1)
    args = parser.parse_args()

    arquivo_chunks = args.arquivo_chunks or Path(
        f"data/processed/{args.versao}_editais_normativo.jsonl"
    )
    inventario = args.inventario or Path(
        f"data/inventory/{args.versao}_editais_normativo.json"
    )
    init_db()
    with SessionLocal() as db:
        resumo = persistir_chunks_jsonl_normativos(
            db=db,
            corpus_version_id=args.corpus_version_id,
            arquivo_chunks=arquivo_chunks,
            urls_por_arquivo=_urls_por_arquivo(inventario),
        )
    print(f"Base normativa persistida no SQLite | {resumo}")
