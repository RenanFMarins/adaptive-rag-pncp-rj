"""Persiste Document/DocumentChunk a partir de textoAtivo dos manifestos PNCP."""

import argparse
from pathlib import Path

from app.core.database import SessionLocal, init_db
from app.modules.documents.services import persistir_textos_ativos_pncp
from src.base_estruturada.pipelines.pipeline_documentos import (
    PeriodoColeta,
    caminhos_do_periodo,
)
from src.base_estruturada.pipelines.pipeline_chunks import (
    aplicar_estado_docling,
    carregar_estados_docling_do_periodo,
)
from src.base_estruturada.pncp.repository import (
    carregar_checkpoint_documentos,
    carregar_json,
    materializar_manifesto_com_checkpoint,
)


def _periodo(valor: str) -> PeriodoColeta:
    ano, mes = valor.replace("-", "/").split("/", maxsplit=1)
    return PeriodoColeta(ano=int(ano), mes=int(mes))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Persiste Document/DocumentChunk a partir de textoAtivo."
    )
    parser.add_argument("--tipo", choices=["contratos", "contratacoes", "todos"])
    parser.add_argument("--periodo")
    parser.add_argument("--limite", type=int)
    parser.add_argument("--corpus-version-id", type=int)
    parser.add_argument("--sem-langchain", action="store_true")
    args = parser.parse_args()

    PERIODO = PeriodoColeta(ano=2026, mes=8)
    CORPUS_VERSION_ID = 1
    LIMITE_TEXTOS: int | None = 5
    USAR_LANGCHAIN = True
    if args.periodo:
        PERIODO = _periodo(args.periodo)
    if args.corpus_version_id is not None:
        CORPUS_VERSION_ID = args.corpus_version_id
    if args.limite is not None:
        LIMITE_TEXTOS = args.limite
    if args.sem_langchain:
        USAR_LANGCHAIN = False

    CAMINHOS = caminhos_do_periodo(PERIODO)
    manifestos = {
        "contratos": materializar_manifesto_com_checkpoint(
            carregar_json(CAMINHOS["manifesto_contratos"], padrao=[]),
            carregar_checkpoint_documentos(CAMINHOS["checkpoint_documentos_contratos"]),
        ),
        "contratacoes": materializar_manifesto_com_checkpoint(
            carregar_json(CAMINHOS["manifesto_contratacoes"], padrao=[]),
            carregar_checkpoint_documentos(
                CAMINHOS["checkpoint_documentos_contratacoes"]
            ),
        ),
    }
    # Os manifestos preservam a resposta original do PNCP. Os resultados do
    # Docling ficam em checkpoints separados, gerados por lote no Colab.
    # Aplicamos esse estado somente em memoria para que ``textoAtivo`` aponte
    # para os Markdown que devem ser persistidos no banco.
    estado_docling, arquivos_estado = carregar_estados_docling_do_periodo(
        PERIODO
    )
    aplicar_estado_docling(manifestos, estado_docling)
    print(f"Checkpoints Docling encontrados: {len(arquivos_estado)}")

    if args.tipo in {"contratos", "contratacoes"}:
        manifestos = {args.tipo: manifestos[args.tipo]}
    bases = {
        "contratos": carregar_json(CAMINHOS["contratos"], padrao=[]),
        "contratacoes": carregar_json(CAMINHOS["contratacoes"], padrao=[]),
    }
    if args.tipo in {"contratos", "contratacoes"}:
        bases = {args.tipo: bases[args.tipo]}
    if not all(isinstance(valor, list) for valor in [*manifestos.values(), *bases.values()]):
        raise RuntimeError("Manifestos e bases estruturadas devem conter listas JSON.")

    init_db()
    with SessionLocal() as db:
        resumo = persistir_textos_ativos_pncp(
            db=db,
            corpus_version_id=CORPUS_VERSION_ID,
            manifestos=manifestos,
            bases=bases,
            limite_textos=LIMITE_TEXTOS,
            usar_langchain=USAR_LANGCHAIN,
            raiz_projeto=Path.cwd(),
        )
    print(f"Persistencia Document/DocumentChunk | {resumo}")
