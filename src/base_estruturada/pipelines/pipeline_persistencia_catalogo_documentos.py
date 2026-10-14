"""Persiste as listagens originais de documentos PNCP no catálogo SQLite.

Não chama o PNCP e não baixa arquivos. É seguro rodar durante uma indisponibilidade
externa, desde que os manifestos mensais já estejam em ``data/normalized``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.core.database import SessionLocal, init_db
from app.modules.documents.services import persistir_catalogo_documentos_pncp
from src.base_estruturada.pipelines.pipeline_documentos import (
    PeriodoColeta,
    caminhos_do_periodo,
)


def _periodo(valor: str) -> PeriodoColeta:
    ano, mes = valor.replace("-", "/").split("/", maxsplit=1)
    return PeriodoColeta(ano=int(ano), mes=int(mes))


def _manifestos(periodos: list[PeriodoColeta], tipo: str) -> list[tuple[str, str, Path]]:
    resultado: list[tuple[str, str, Path]] = []
    for periodo in periodos:
        caminhos = caminhos_do_periodo(periodo)
        if tipo in {"contratos", "todos"}:
            resultado.append(("contrato", periodo.identificador, caminhos["manifesto_contratos"]))
        if tipo in {"contratacoes", "todos"}:
            resultado.append(("contratacao", periodo.identificador, caminhos["manifesto_contratacoes"]))
    return resultado


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Persiste manifestos PNCP como catálogo local de URLs."
    )
    parser.add_argument(
        "--periodo",
        action="append",
        required=True,
        help="Repita para cada mês, por exemplo: --periodo 2026/06 --periodo 2026/07",
    )
    parser.add_argument(
        "--tipo", choices=["contratos", "contratacoes", "todos"], default="todos"
    )
    args = parser.parse_args()

    periodos = [_periodo(valor) for valor in args.periodo]
    manifestos = _manifestos(periodos, args.tipo)
    ausentes = [str(caminho) for _, _, caminho in manifestos if not caminho.is_file()]
    if ausentes:
        raise FileNotFoundError("Manifestos não encontrados:\n- " + "\n- ".join(ausentes))

    init_db()
    with SessionLocal() as db:
        resumo = persistir_catalogo_documentos_pncp(db, manifestos)
    print(f"Catálogo PNCP persistido no SQLite | {resumo}")
