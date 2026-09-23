import json
from pathlib import Path
from typing import Any
import os

from src.base_estrturada.pncp.service import (
    consultar_documentos_contrato)


ARQUIVO_CONTRATOS = Path(
    "data/normalized/contratos_rj.json"
)

CAMINHO_MANIFESTO = Path("data/normalized/contratos_documentos.json")


def carregar_json(caminho: Path | str, padrao: Any) -> Any:
    caminho = Path(caminho)

    if not caminho.exists():
        return padrao

    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"O arquivo JSON está inválido: {caminho}"
        ) from exc


def salvar_json(caminho: Path | str, dados: Any) -> None:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    temporario = caminho.with_suffix(".tmp")

    with temporario.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    os.replace(temporario, caminho)


def salvar_pagina_raw(
        dados: dict[str, Any],
        pagina: int,
        data_inicial: str,
        data_final: str
) -> None:
    caminho = Path(
        "data/raw/contratos/"
        f"{data_inicial}_{data_final}/"
        f"pagina_{pagina:04d}.json"
    )

    salvar_json(caminho, dados)


def adicionar_contratos_novos(
        novos_contratos: list[dict[str, Any]],
) -> int:

    contratos_existentes = carregar_json(
        ARQUIVO_CONTRATOS,
        padrao=[],
    )

    if not isinstance(contratos_existentes, list):
        raise RuntimeError(
            "O arquivo contratos_rj.json deveria conter uma lista."
        )

    controles_existentes = {
        item.get("numeroControlePNCP")
        for item in contratos_existentes
        if isinstance(item, dict)
        and item.get("numeroControlePNCP")
    }

    quantidade_nova = 0

    for contrato in novos_contratos:

        if not isinstance(contrato, dict):
            continue

        numero_controle = contrato.get("numeroControlePNCP")

        if not numero_controle:
            continue

        if numero_controle in controles_existentes:
            continue

        contratos_existentes.append(contrato)
        controles_existentes.add(numero_controle)
        quantidade_nova += 1

    salvar_json(ARQUIVO_CONTRATOS, contratos_existentes)

    return quantidade_nova


def salvar_paginas_com_erro(
    data_inicial: str,
    data_final: str,
    paginas: list[int],
) -> None:
    caminho = Path(
        "data/checkpoints/contratos_paginas_com_erro.json"
    )

    dados = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "paginasComErro": paginas,
    }

    salvar_json(caminho, dados)


def salvar_lista_de_documentos(dados: list[dict]) -> None:

    contratos = dados[:5]
    manifesto = []

    for contrato in contratos:
        lista_arquivos = consultar_documentos_contrato(contrato)

        contrato_formatado = {
            "numeroControlePNCP": contrato.get("numeroControlePNCP"),
            "cnpjOrgao": contrato.get("cnpjOrgao") or contrato.get("orgaoEntidade", {}).get("cnpj"),
            "anoContrato": contrato.get("anoContrato"),
            "sequencialContrato": contrato.get("sequencialContrato"),
            "documentos": lista_arquivos
        }

        manifesto.append(contrato_formatado)

        print(
            f"Contrato: {contrato['numeroControlePNCP']} | "
            f"Documentos: {len(lista_arquivos)}"
        )

        for documento in lista_arquivos:
            print(
                f"  - {documento.get('tipoDocumentoNome')} | "
                f"{documento.get('titulo')} | "
                f"{documento.get('url')}"
            )

    salvar_json(CAMINHO_MANIFESTO, manifesto)
