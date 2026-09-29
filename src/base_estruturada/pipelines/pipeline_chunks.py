"""Gera JSONL de chunks a partir de ``textoAtivo`` dos manifestos PNCP."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.base_estruturada.chunking import (
    caminho_relativo_portavel,
    gerar_chunk_id,
    gerar_chunks,
    montar_metadata_base,
    selecionar_configuracao,
)
from src.base_estruturada.pipelines.pipeline_documentos import (
    PeriodoColeta,
    caminhos_do_periodo,
)
from src.base_estruturada.pncp.repository import (
    carregar_checkpoint_documentos,
    carregar_json,
    materializar_manifesto_com_checkpoint,
    salvar_json,
)


def _indice_por_controle(registros: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(registro["numeroControlePNCP"]): registro
        for registro in registros
        if isinstance(registro, dict) and registro.get("numeroControlePNCP")
    }


def gerar_chunks_do_periodo(
    manifestos: dict[str, list[dict[str, Any]]],
    bases: dict[str, list[dict[str, Any]]],
    arquivo_saida: Path,
    arquivo_relatorio: Path,
    limite_textos: int | None,
    usar_langchain: bool,
) -> dict[str, int]:
    """Gera um JSONL reproduzivel sem alterar manifestos nem arquivos fonte."""

    raiz_projeto = Path.cwd()
    indices = {
        origem: _indice_por_controle(registros)
        for origem, registros in bases.items()
    }
    linhas: list[dict[str, Any]] = []
    resumo = {
        "textosLidos": 0,
        "chunksGerados": 0,
        "textosSemArquivo": 0,
        "textosSemRegistroEstruturado": 0,
    }

    for origem, manifesto in manifestos.items():
        tipo_entidade = "contrato" if origem == "contratos" else "contratacao"
        for entidade_manifesto in manifesto:
            if not isinstance(entidade_manifesto, dict):
                continue

            controle = str(entidade_manifesto.get("numeroControlePNCP") or "")
            entidade = indices[origem].get(controle)
            if entidade is None:
                resumo["textosSemRegistroEstruturado"] += 1
                continue

            for documento in entidade_manifesto.get("documentos") or []:
                if not isinstance(documento, dict):
                    continue
                for registro_texto in documento.get("processamentoTexto") or []:
                    ativo = registro_texto.get("textoAtivo") or {}
                    caminho_texto = Path(str(ativo.get("caminho") or ""))
                    if not caminho_texto.is_file():
                        if ativo:
                            resumo["textosSemArquivo"] += 1
                        continue
                    if limite_textos is not None and resumo["textosLidos"] >= limite_textos:
                        break

                    texto = caminho_texto.read_text(
                        encoding="utf-8", errors="replace")
                    configuracao = selecionar_configuracao(
                        documento.get("tipoDocumentoNome"),
                        caminho_texto,
                    )
                    metadata = montar_metadata_base(
                        entidade=entidade,
                        documento=documento,
                        registro_texto=registro_texto,
                        tipo_entidade=tipo_entidade,
                        caminho_relativo=caminho_relativo_portavel(
                            caminho_texto,
                            raiz_projeto,
                        ),
                    )

                    for indice, conteudo in enumerate(
                        gerar_chunks(
                            texto,
                            configuracao,
                            usar_langchain=usar_langchain,
                        )
                    ):
                        linhas.append(
                            {
                                "chunk_id": gerar_chunk_id(metadata, indice, conteudo),
                                "content": conteudo,
                                "metadata": {
                                    **metadata,
                                    "indiceChunk": indice,
                                    "configuracaoChunk": configuracao.nome,
                                },
                            }
                        )

                    resumo["textosLidos"] += 1

            if limite_textos is not None and resumo["textosLidos"] >= limite_textos:
                break

    arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    temporario = arquivo_saida.with_suffix(".tmp")
    with temporario.open("w", encoding="utf-8") as arquivo:
        for linha in linhas:
            arquivo.write(json.dumps(linha, ensure_ascii=False) + "\n")
    os.replace(temporario, arquivo_saida)

    resumo["chunksGerados"] = len(linhas)
    relatorio = {
        "geradoEm": datetime.now(timezone.utc).isoformat(),
        "arquivoChunks": str(arquivo_saida),
        "usarLangChain": usar_langchain,
        "resumo": resumo,
    }
    salvar_json(arquivo_relatorio, relatorio)
    return resumo


if __name__ == "__main__":
    PERIODO = PeriodoColeta(ano=2026, mes=8)
    CAMINHOS = caminhos_do_periodo(PERIODO)

    # Use "teste" enquanto estiver validando. Depois crie uma versao, por
    # exemplo "v1", para gerar a base definitiva sem misturar resultados.
    VERSAO_CHUNKS = "teste"
    LIMITE_TEXTOS: int | None = 5
    # True usa RecursiveCharacterTextSplitter e MarkdownHeaderTextSplitter.
    # False preserva o divisor manual como contingencia temporaria.
    USAR_LANGCHAIN = True

    manifestos = {
        "contratos": materializar_manifesto_com_checkpoint(
            carregar_json(CAMINHOS["manifesto_contratos"], padrao=[]),
            carregar_checkpoint_documentos(
                CAMINHOS["checkpoint_documentos_contratos"]
            ),
        ),
        "contratacoes": materializar_manifesto_com_checkpoint(
            carregar_json(CAMINHOS["manifesto_contratacoes"], padrao=[]),
            carregar_checkpoint_documentos(
                CAMINHOS["checkpoint_documentos_contratacoes"]
            ),
        ),
    }
    bases = {
        "contratos": carregar_json(CAMINHOS["contratos"], padrao=[]),
        "contratacoes": carregar_json(CAMINHOS["contratacoes"], padrao=[]),
    }
    if not all(isinstance(valor, list) for valor in [*manifestos.values(), *bases.values()]):
        raise RuntimeError(
            "Manifestos e bases estruturadas devem conter listas JSON.")

    arquivo_saida = Path(
        f"data/chunks/{VERSAO_CHUNKS}/chunks_{PERIODO.identificador}.jsonl"
    )
    arquivo_relatorio = Path(
        f"data/chunks/{VERSAO_CHUNKS}/relatorio_{PERIODO.identificador}.json"
    )
    resumo = gerar_chunks_do_periodo(
        manifestos=manifestos,
        bases=bases,
        arquivo_saida=arquivo_saida,
        arquivo_relatorio=arquivo_relatorio,
        limite_textos=LIMITE_TEXTOS,
        usar_langchain=USAR_LANGCHAIN,
    )
    print(f"Chunks gerados | {resumo}")
