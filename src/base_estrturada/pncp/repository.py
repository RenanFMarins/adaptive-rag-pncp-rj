import json
import zipfile
import shutil
import stat
import os
import re

from pathlib import Path
from typing import Any


from src.base_estrturada.pncp.service import (
    consultar_documentos_contrato, consultar_documentos_contratacao)


ARQUIVO_CONTRATOS = Path(
    "data/normalized/contratos_rj.json"
)

ARQUIVO_CONTRATACOES = Path(
    "data/normalized/contratacoes_rj.json"
)


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


def adicionar_registros_novos(
        novos_registros: list[dict[str, Any]],
        arquivo: Path | str
) -> int:
    """
    Mescla novos_registros no arquivo indicado, deduplicando por
    numeroControlePNCP. Serve tanto para contratos quanto para
    contratacoes -- o dado que muda e' so o arquivo de destino.
    """

    registros_existentes = carregar_json(
        arquivo,
        padrao=[],
    )

    if not isinstance(registros_existentes, list):
        raise RuntimeError(
            f"O arquivo {arquivo} deveria conter uma lista."
        )

    controles_existentes = {
        item.get("numeroControlePNCP")
        for item in registros_existentes
        if isinstance(item, dict)
        and item.get("numeroControlePNCP")
    }

    quantidade_nova = 0

    for registro in novos_registros:

        if not isinstance(registro, dict):
            continue

        numero_controle = registro.get("numeroControlePNCP")

        if not numero_controle:
            continue

        if numero_controle in controles_existentes:
            continue

        registros_existentes.append(registro)
        controles_existentes.add(numero_controle)
        quantidade_nova += 1

    salvar_json(arquivo, registros_existentes)

    return quantidade_nova


def adicionar_contratos_novos(novos_contratos: list[dict[str, Any]]) -> int:
    return adicionar_registros_novos(novos_contratos, ARQUIVO_CONTRATOS)


def adicionar_contratacoes_novas(novas_contratacoes: list[dict[str, Any]]) -> int:
    return adicionar_registros_novos(novas_contratacoes, ARQUIVO_CONTRATACOES)


def salvar_paginas_com_erro(
    data_inicial: str,
    data_final: str,
    paginas: list[int],
    caminho: Path | str
) -> None:
    """
    caminho = Path(
        "data/checkpoints/contratos_paginas_com_erro.json"
    )
    """

    dados = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "paginasComErro": paginas,
    }

    salvar_json(caminho, dados)


def salvar_lista_de_documentos_contratos(
        contratos: list[dict],
        caminho: Path | str,
        limite: int = 5,) -> None:

    manifesto = []

    for contrato in contratos[:limite]:
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

    salvar_json(caminho, manifesto)

    return manifesto


def salvar_lista_documentos_contratacao(
    contratacoes: list[dict],
    caminho: Path | str,
    limite: int = 5,
) -> list[dict]:
    manifesto = []

    for contratacao in contratacoes[:limite]:
        documentos = consultar_documentos_contratacao(
            contratacao
        )

        orgao = contratacao.get("orgaoEntidade") or {}

        contratacao_formatada = {
            "numeroControlePNCP": contratacao.get(
                "numeroControlePNCP"
            ),
            "cnpjOrgao": orgao.get("cnpj"),
            "anoCompra": contratacao.get("anoCompra"),
            "sequencialCompra": contratacao.get(
                "sequencialCompra"
            ),
            "documentos": documentos,
        }

        manifesto.append(contratacao_formatada)

        print(
            f"Contratação: "
            f"{contratacao.get('numeroControlePNCP')} | "
            f"Documentos: {len(documentos)}"
        )

    salvar_json(caminho, manifesto)

    return manifesto


def _detectar_formato_arquivo(
    caminho: Path,
) -> tuple[str, str]:
    """
    Retorna: (extensão, descrição do formato).
    """

    with caminho.open("rb") as arquivo:
        inicio = arquivo.read(16)

    if inicio.startswith(b"%PDF-"):
        return ".pdf", "PDF"

    if inicio.startswith(b"Rar!\x1a\x07\x00"):
        return ".rar", "RAR 4"

    if inicio.startswith(b"Rar!\x1a\x07\x01\x00"):
        return ".rar", "RAR 5"

    if inicio.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png", "PNG"

    if inicio.startswith(b"\xff\xd8\xff"):
        return ".jpg", "JPEG"

    if inicio.startswith(b"PK"):
        try:
            with zipfile.ZipFile(caminho) as arquivo_zip:
                nomes = arquivo_zip.namelist()

                if any(nome.startswith("word/") for nome in nomes):
                    return ".docx", "DOCX"

                if any(nome.startswith("xl/") for nome in nomes):
                    return ".xlsx", "XLSX"

                if any(nome.startswith("ppt/") for nome in nomes):
                    return ".pptx", "PPTX"

                if "mimetype" in nomes:
                    tipo_odf = (
                        arquivo_zip.read("mimetype")
                        .decode("utf-8", errors="ignore")
                    )

                    if "opendocument.text" in tipo_odf:
                        return ".odt", "ODT"

                return ".zip", "ZIP"

        except zipfile.BadZipFile:
            return ".bin", "Binário desconhecido"

    # DOC, XLS e PPT antigos usam o mesmo formato-base OLE.
    if inicio.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return ".ole", "Documento Office antigo (OLE)"

    return ".bin", "Binário desconhecido"


def renomear_arquivo_detectado(
    caminho: Path,
) -> tuple[Path, str]:
    extensao, formato = _detectar_formato_arquivo(caminho)

    novo_caminho = caminho.with_suffix(extensao)

    if novo_caminho != caminho:
        caminho.replace(novo_caminho)

    return novo_caminho, formato


def identificar_arquivos_do_manifesto(
    manifesto: list[dict[str, Any]],
) -> int:
    quantidade_identificada = 0

    for contrato in manifesto:
        documentos = contrato.get("documentos") or []
        for documento in documentos:
            download = documento.get("download") or {}

            if download.get("status") != "baixado":
                continue

            caminho_texto = download.get("caminho")

            if not caminho_texto:
                continue

            caminho = Path(caminho_texto)

            if not caminho.exists():
                download["status"] = "arquivo_nao_encontrado"
                documento["download"] = download
                continue

            novo_caminho, formato = (
                renomear_arquivo_detectado(caminho)
            )

            documento["download"] = {
                "status": "identificado",
                "caminho": str(novo_caminho),
                "formato": formato,
            }

            quantidade_identificada += 1

            print(
                f"Identificado | {novo_caminho.name} | "
                f"formato={formato}"
            )

    return quantidade_identificada


def _nome_seguro(texto: str) -> str:
    caracteres_invalidos = '<>:"/\\|?*'

    for caractere in caracteres_invalidos:
        texto = texto.replace(caractere, "-")

    return texto


def extrair_zip_com_seguranca(
    caminho_zip: Path,
    pasta_destino: Path,
    max_arquivos: int = 100,
    max_tamanho_total: int = 200 * 1024 * 1024,
) -> list[Path]:
    """
    Descompacta um ZIP com limites de segurança.

    Retorna os caminhos dos arquivos extraídos.
    """

    with zipfile.ZipFile(caminho_zip) as arquivo_zip:
        itens = arquivo_zip.infolist()

        if len(itens) > max_arquivos:
            raise RuntimeError(
                f"ZIP possui {len(itens)} itens; "
                f"limite permitido: {max_arquivos}."
            )

        tamanho_total = sum(
            item.file_size
            for item in itens
        )

        if tamanho_total > max_tamanho_total:
            raise RuntimeError(
                "ZIP excede o limite de tamanho "
                "descompactado permitido."
            )

        pasta_destino.mkdir(
            parents=True,
            exist_ok=True,
        )

        destino_absoluto = pasta_destino.resolve()
        arquivos_extraidos: list[Path] = []

        for item in itens:
            if item.is_dir():
                continue

            modo = item.external_attr >> 16

            if stat.S_ISLNK(modo):
                print(
                    f"Link simbólico ignorado: {item.filename}"
                )
                continue

            caminho_saida = (
                pasta_destino / item.filename
            ).resolve()

            # Evita arquivos com caminhos como ../../arquivo.txt
            if not str(caminho_saida).startswith(
                str(destino_absoluto)
            ):
                print(
                    f"Caminho inválido ignorado: "
                    f"{item.filename}"
                )
                continue

            caminho_saida.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with arquivo_zip.open(item) as origem:
                with caminho_saida.open("wb") as destino:
                    shutil.copyfileobj(origem, destino)

            arquivos_extraidos.append(caminho_saida)

    return arquivos_extraidos


def extrair_zips_do_manifesto(
    manifesto: list[dict[str, Any]],
    pasta_base: Path | str,
) -> int:
    quantidade_extraida = 0
    pasta_base = Path(pasta_base)

    for contrato in manifesto:
        numero_controle = contrato.get(
            "numeroControlePNCP"
        )

        if not numero_controle:
            continue

        for documento in contrato.get("documentos") or []:
            download = documento.get("download") or {}

            if download.get("formato") != "ZIP":
                continue

            caminho_zip = Path(
                download.get("caminho", "")
            )

            if not caminho_zip.exists():
                print(
                    f"ZIP não encontrado: {caminho_zip}"
                )
                continue

            sequencial = documento.get(
                "sequencialDocumento",
                "sem_sequencial",
            )

            pasta_destino = (
                pasta_base
                / _nome_seguro(numero_controle)
                / f"documento_{sequencial}"
            )

            try:
                arquivos = extrair_zip_com_seguranca(
                    caminho_zip=caminho_zip,
                    pasta_destino=pasta_destino,
                )

            except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                documento["extracao"] = {
                    "status": "erro",
                    "mensagem": str(exc),
                }

                print(
                    f"Erro ao extrair ZIP | "
                    f"contrato={numero_controle} | {exc}"
                )
                continue

            documento["extracao"] = {
                "status": "extraido",
                "caminho": str(pasta_destino),
                "arquivos": [
                    str(arquivo)
                    for arquivo in arquivos
                ],
            }

            quantidade_extraida += 1

            print(
                f"ZIP extraído | contrato={numero_controle} | "
                f"arquivos={len(arquivos)}"
            )

    return quantidade_extraida
