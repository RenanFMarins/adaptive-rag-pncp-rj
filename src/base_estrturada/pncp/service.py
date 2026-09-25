from datetime import date
from dataclasses import dataclass
from pathlib import Path
import time
from typing import Any
import re
from urllib.parse import urlparse
import zipfile
import shutil
import stat
import requests

from src.base_estrturada.pncp.client import pncp_client


# ============================================================
# URLs BASE
# ============================================================

BASE_URL_CONSULTA = (
    "https://pncp.gov.br/api/consulta/v1"
)

BASE_URL_CONTRATACOES = (
    f"{BASE_URL_CONSULTA}/contratacoes/publicacao"
)

BASE_URL_CONTRATOS = (
    f"{BASE_URL_CONSULTA}/contratos"
)

BASE_URL_PROPOSTA = (
    f"{BASE_URL_CONSULTA}/contratacoes/proposta"
)

BASE_URL_PNCP = (
    "https://pncp.gov.br/api/pncp"
)


# ============================================================
# MODALIDADES
# ============================================================

def carregar_modalidades(
    somente_ativas: bool = True,
) -> dict[int, str]:
    """
    Consulta as modalidades de contratação disponíveis no PNCP.

    Retorna:
        dict[int, str]:
            Dicionário no formato:
            {
                codigo_modalidade: nome_modalidade
            }
    """

    url = (
        f"{BASE_URL_PNCP}/v1/modalidades"
    )

    try:
        response = pncp_client.get(url)

        response.raise_for_status()

        dados = response.json()

        modalidades: dict[int, str] = {}

        for item in dados:
            if (
                somente_ativas
                and not item.get(
                    "statusAtivo",
                    False,
                )
            ):
                continue

            codigo = item.get("id")
            nome = item.get("nome")

            if codigo is not None and nome:
                modalidades[codigo] = nome

        return modalidades

    except requests.RequestException as exc:
        print(
            f"Erro ao consultar modalidades: {exc}"
        )

        return {}

    except ValueError:
        print(
            "Resposta inválida do PNCP "
            "ao consultar modalidades."
        )

        return {}


# ============================================================
# CONTRATAÇÕES PUBLICADAS
# ============================================================

def coletar_contratacoes(
    uf: str,
    data_inicial: str,
    data_final: str,
    modalidades: list[int] | None = None,
    tamanho_pagina: int = 10,
) -> list[dict]:
    """
    Consulta contratações publicadas no PNCP.

    A consulta é realizada por modalidade e percorre
    automaticamente as páginas disponíveis.
    """

    if tamanho_pagina < 10:
        tamanho_pagina = 10

    if modalidades is None:
        modalidades_disponiveis = (
            carregar_modalidades()
        )

        modalidades = list(
            modalidades_disponiveis.keys()
        )

    resultados: list[dict] = []

    controles_encontrados: set[str] = set()

    for modalidade in modalidades:
        print(
            f"Coletando modalidade {modalidade}..."
        )

        pagina = 1

        while True:
            params = {
                "dataInicial": data_inicial,
                "dataFinal": data_final,
                "codigoModalidadeContratacao": modalidade,
                "uf": uf,
                "pagina": pagina,
                "tamanhoPagina": tamanho_pagina,
            }

            try:
                response = pncp_client.get(
                    BASE_URL_CONTRATACOES,
                    params=params,
                )

            except requests.exceptions.Timeout:
                print(
                    "Timeout | "
                    f"modalidade={modalidade} | "
                    f"página={pagina}"
                )

                break

            except requests.exceptions.ConnectionError as exc:
                print(
                    "Erro de conexão | "
                    f"modalidade={modalidade} | "
                    f"página={pagina} | "
                    f"{exc}"
                )

                break

            except requests.RequestException as exc:
                print(
                    "Erro HTTP | "
                    f"modalidade={modalidade} | "
                    f"página={pagina} | "
                    f"{exc}"
                )

                break

            # ------------------------------------------------
            # SEM CONTEÚDO
            # ------------------------------------------------

            if response.status_code == 204:
                break

            # ------------------------------------------------
            # RATE LIMIT
            # ------------------------------------------------

            if response.status_code == 429:
                print(
                    "PNCP retornou HTTP 429 "
                    "(muitas requisições)."
                )

                break

            # ------------------------------------------------
            # OUTROS ERROS
            # ------------------------------------------------

            if response.status_code != 200:
                print(
                    f"Erro {response.status_code} | "
                    f"modalidade={modalidade} | "
                    f"página={pagina}"
                )

                try:
                    print(response.text)
                except Exception:
                    pass

                break

            # ------------------------------------------------
            # JSON
            # ------------------------------------------------

            try:
                dados = response.json()

            except ValueError:
                print(
                    "Resposta inválida do PNCP "
                    "(não é JSON)."
                )

                break

            registros = (
                dados.get("data")
                or []
            )

            if not registros:
                break

            # ------------------------------------------------
            # REMOVE DUPLICADOS
            # ------------------------------------------------

            for item in registros:
                numero_controle = (
                    item.get(
                        "numeroControlePNCP"
                    )
                )

                if numero_controle:
                    if (
                        numero_controle
                        in controles_encontrados
                    ):
                        continue

                    controles_encontrados.add(
                        numero_controle
                    )

                resultados.append(item)

            # ------------------------------------------------
            # PAGINAÇÃO
            # ------------------------------------------------

            total_paginas = (
                dados.get("totalPaginas")
                or 1
            )

            if pagina >= total_paginas:
                break

            pagina += 1

    return resultados


# ============================================================
# CONTRATOS
# ============================================================

@dataclass
class ResultadoColetaContratos:
    """Resultado da coleta, inclusive páginas que devem ser retentadas."""

    contratos: list[dict[str, Any]]
    paginas_com_erro: list[int]


def coletar_contratos(
    data_inicial: str,
    data_final: str,
    tamanho_pagina: int = 50,
) -> ResultadoColetaContratos:
    """
    Consulta contratos publicados no PNCP.
    """

    if tamanho_pagina <= 0:
        tamanho_pagina = 50

    resultados: list[dict[str, Any]] = []
    paginas_com_erro: list[int] = []

    controles_encontrados: set[str] = set()

    pagina = 1
    total_paginas: int | None = None

    while total_paginas is None or pagina <= total_paginas:
        params = {
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "pagina": pagina,
            "tamanhoPagina": tamanho_pagina,
        }

        try:
            response = pncp_client.get(
                BASE_URL_CONTRATOS,
                params=params,
            )

        except requests.exceptions.Timeout:
            print(
                "Timeout | contratos | "
                f"página={pagina}"
            )

            paginas_com_erro.append(pagina)

            if total_paginas is None:
                break

            pagina += 1
            continue

        except requests.exceptions.ConnectionError as exc:
            print(
                "Erro de conexão | contratos | "
                f"página={pagina} | {exc}"
            )

            paginas_com_erro.append(pagina)

            if total_paginas is None:
                break

            pagina += 1
            continue

        except requests.RequestException as exc:
            print(
                "Erro HTTP | contratos | "
                f"página={pagina} | {exc}"
            )

            paginas_com_erro.append(pagina)

            if total_paginas is None:
                break

            pagina += 1
            continue

        if response.status_code == 204:
            break

        if response.status_code == 429:
            print(
                f"PNCP continuou retornando HTTP 429 "
                f"na página {pagina} após as tentativas automáticas."
            )

            paginas_com_erro.append(pagina)

            if total_paginas is None:
                break

            pagina += 1
            continue

        if response.status_code != 200:
            print(
                f"Erro {response.status_code} | "
                f"contratos | página={pagina}"
            )
            print(response.text[:500])

            paginas_com_erro.append(pagina)

            if total_paginas is None:
                break

            pagina += 1
            continue

        try:
            dados = response.json()

        except ValueError:
            print(
                "Resposta inválida do PNCP "
                "ao consultar contratos."
            )

            paginas_com_erro.append(pagina)

            if total_paginas is None:
                break

            pagina += 1
            continue

        if not isinstance(dados, dict):
            print(
                f"Formato inválido | contratos | página={pagina}"
            )

            paginas_com_erro.append(pagina)

            if total_paginas is None:
                break

            pagina += 1
            continue

        registros = (
            dados.get("data")
            or []
        )

        if not isinstance(registros, list):
            print(
                f"Campo 'data' inválido | contratos | página={pagina}"
            )

            paginas_com_erro.append(pagina)

            if total_paginas is None:
                break

            pagina += 1
            continue

        total_paginas = dados.get("totalPaginas") or pagina

        if not registros:
            print(
                f"Página {pagina}/{total_paginas} | recebidos=0"
            )

            if pagina >= total_paginas:
                break

            pagina += 1
            time.sleep(5)
            continue

        # ----------------------------------------------------
        # FILTRAGEM LOCAL DA UF E REMOÇÃO DE DUPLICADOS
        # ----------------------------------------------------
        for item in registros:
            # Captura a UF do órgão emissor do contrato
            unidade_orgao = item.get("unidadeOrgao") or {}
            uf_orgao = str(
                unidade_orgao.get("ufSigla") or ""
            ).upper()
            # Se NÃO for do Rio de Janeiro, pula para o próximo item
            if uf_orgao != "RJ":
                continue

            numero_controle = item.get("numeroControlePNCP")

            if numero_controle:
                if numero_controle in controles_encontrados:
                    continue
                controles_encontrados.add(numero_controle)

            resultados.append(item)

        print(
            f"Página {pagina}/{total_paginas} | "
            f"recebidos={len(registros)} | "
            f"RJ acumulados={len(resultados)}"
        )

        if pagina >= total_paginas:
            break

        pagina += 1

        # Pausa entre páginas bem-sucedidas para reduzir HTTP 429.
        time.sleep(5)

    return ResultadoColetaContratos(
        contratos=resultados,
        paginas_com_erro=paginas_com_erro,
    )


# ============================================================
# CONTRATAÇÕES COM PROPOSTAS ABERTAS
# ============================================================

def coletar_contratacoes_abertas(
    data_final: str | None = None,
    uf: str = "RJ",
    pagina: int = 1,
) -> dict:
    """
    Consulta contratações com período de recebimento
    de propostas aberto.
    """

    if data_final is None:
        data_final = (
            date.today().strftime(
                "%Y%m%d"
            )
        )

    params = {
        "dataFinal": data_final,
        "uf": uf,
        "pagina": pagina,
    }

    try:
        response = pncp_client.get(
            BASE_URL_PROPOSTA,
            params=params,
        )

    except requests.exceptions.Timeout:
        print(
            "Timeout ao consultar "
            "contratações abertas."
        )

        return {}

    except requests.exceptions.ConnectionError as exc:
        print(
            "Erro de conexão ao consultar "
            f"contratações abertas: {exc}"
        )

        return {}

    except requests.RequestException as exc:
        print(
            "Erro ao consultar "
            f"contratações abertas: {exc}"
        )

        return {}

    if response.status_code == 204:
        return {}

    if response.status_code == 429:
        print(
            "PNCP retornou HTTP 429 "
            "ao consultar contratações abertas."
        )

        return {}

    if response.status_code != 200:
        print(
            f"Erro {response.status_code} "
            "ao consultar contratações abertas."
        )

        try:
            print(response.text)
        except Exception:
            pass

        return {}

    try:
        dados = response.json()

        if isinstance(dados, dict):
            return dados

        return {}

    except ValueError:
        print(
            "Resposta inválida do PNCP "
            "ao consultar contratações abertas."
        )

        return {}


# ============================================================
# ATAS DA COMPRA
# ============================================================

def consultar_atas_compra(
    cnpj: str,
    ano_compra: int,
    sequencial_compra: int,
) -> list[dict]:
    """
    Consulta as Atas de Registro de Preços
    associadas a uma compra.
    """

    url = (
        f"{BASE_URL_PNCP}/v1/orgaos/"
        f"{cnpj}/compras/"
        f"{ano_compra}/"
        f"{sequencial_compra}/atas"
    )

    try:
        response = pncp_client.get(url)

        if response.status_code == 204:
            return []

        if response.status_code == 429:
            print(
                "PNCP retornou HTTP 429 "
                "ao consultar atas."
            )

            return []

        if response.status_code != 200:
            print(
                f"Erro {response.status_code} "
                "ao consultar atas."
            )

            try:
                print(response.text)
            except Exception:
                pass

            return []

        dados = response.json()

        # O endpoint real pode retornar
        # diretamente uma lista.
        if isinstance(dados, list):
            return dados

        # Compatibilidade caso o PNCP
        # retorne um objeto com "data".
        if isinstance(dados, dict):
            return (
                dados.get("data")
                or []
            )

        return []

    except requests.RequestException as exc:
        print(
            f"Erro ao consultar atas: {exc}"
        )

        return []

    except ValueError:
        print(
            "Resposta inválida do PNCP "
            "ao consultar atas."
        )

        return []


# ============================================================
# QUANTIDADE DE DOCUMENTOS DA ATA
# ============================================================

def consultar_quantidade_documentos_ata(
    cnpj: str,
    ano_compra: int,
    sequencial_compra: int,
    sequencial_ata: int,
) -> int:
    """
    Consulta a quantidade de documentos existentes
    em uma Ata de Registro de Preços.
    """

    url = (
        f"{BASE_URL_PNCP}/v1/orgaos/"
        f"{cnpj}/compras/"
        f"{ano_compra}/"
        f"{sequencial_compra}/atas/"
        f"{sequencial_ata}/"
        "arquivos/quantidade"
    )

    try:
        response = pncp_client.get(url)

        if response.status_code == 204:
            return 0

        if response.status_code == 429:
            print(
                "PNCP retornou HTTP 429 "
                "ao consultar quantidade "
                "de documentos."
            )

            return 0

        if response.status_code != 200:
            print(
                f"Erro {response.status_code} "
                "ao consultar quantidade "
                "de documentos."
            )

            try:
                print(response.text)
            except Exception:
                pass

            return 0

        dados = response.json()

        # Resposta observada no endpoint:
        #
        # 4

        if isinstance(dados, int):
            return dados

        # Compatibilidade caso a API retorne:
        #
        # {"quantidade": 4}

        if isinstance(dados, dict):
            quantidade = (
                dados.get("quantidade")
            )

            if quantidade is not None:
                return int(quantidade)

        return 0

    except requests.RequestException as exc:
        print(
            "Erro ao consultar quantidade "
            f"de documentos: {exc}"
        )

        return 0

    except (
        ValueError,
        TypeError,
    ):
        print(
            "Resposta inválida ao consultar "
            "quantidade de documentos."
        )

        return 0


# ============================================================
# DOCUMENTOS DA ATA
# ============================================================

def consultar_documentos_ata(
    cnpj: str,
    ano_compra: int,
    sequencial_compra: int,
    sequencial_ata: int,
) -> list[dict]:
    """
    Lista os documentos associados a uma Ata.
    """

    url = (
        f"{BASE_URL_PNCP}/v1/orgaos/"
        f"{cnpj}/compras/"
        f"{ano_compra}/"
        f"{sequencial_compra}/atas/"
        f"{sequencial_ata}/arquivos"
    )

    try:
        response = pncp_client.get(url)

        if response.status_code == 204:
            return []

        if response.status_code == 429:
            print(
                "PNCP retornou HTTP 429 "
                "ao consultar documentos da ata."
            )

            return []

        if response.status_code != 200:
            print(
                f"Erro {response.status_code} "
                "ao consultar documentos da ata."
            )

            try:
                print(response.text)
            except Exception:
                pass

            return []

        dados = response.json()

        # O endpoint real retorna diretamente uma lista.
        if isinstance(dados, list):
            return dados

        # Compatibilidade com eventual
        # resposta no formato {"data": [...]}.
        if isinstance(dados, dict):
            return (
                dados.get("data")
                or []
            )

        return []

    except requests.RequestException as exc:
        print(
            "Erro ao consultar documentos "
            f"da ata: {exc}"
        )

        return []

    except ValueError:
        print(
            "Resposta inválida do PNCP "
            "ao consultar documentos da ata."
        )

        return []


# ============================================================
# DOWNLOAD DE UM DOCUMENTO
# ============================================================

def baixar_documento_ata(
    cnpj: str,
    ano_compra: int,
    sequencial_compra: int,
    sequencial_ata: int,
    sequencial_documento: int,
    destino: str | Path,
    url_documento: str | None = None,
) -> Path | None:
    """
    Baixa um documento associado a uma Ata do PNCP.

    Para downloads utilizamos requests diretamente,
    pois este endpoint entrega conteúdo binário e não JSON.

    A URL retornada pelo próprio PNCP tem prioridade.
    """

    destino = Path(destino)

    # --------------------------------------------------------
    # DEFINE A URL
    # --------------------------------------------------------

    if url_documento:
        url = url_documento.strip()

    else:
        url = (
            "https://pncp.gov.br/"
            "pncp-api/v1/orgaos/"
            f"{cnpj}/compras/"
            f"{ano_compra}/"
            f"{sequencial_compra}/atas/"
            f"{sequencial_ata}/arquivos/"
            f"{sequencial_documento}"
        )

    try:
        # ----------------------------------------------------
        # DOWNLOAD BINÁRIO
        # ----------------------------------------------------

        response = requests.get(
            url,
            stream=True,
            timeout=120,
            headers={
                "Accept": "application/pdf,*/*",
                "User-Agent": "Mozilla/5.0",
            },
        )

        # ----------------------------------------------------
        # ERRO HTTP
        # ----------------------------------------------------

        if response.status_code != 200:
            print(
                f"Erro {response.status_code} "
                "ao baixar documento."
            )

            try:
                print(
                    "Resposta do PNCP:",
                    response.text[:1000],
                )
            except Exception:
                pass

            return None

        # ----------------------------------------------------
        # INFORMAÇÕES DA RESPOSTA
        # ----------------------------------------------------

        content_type = (
            response.headers.get(
                "Content-Type",
                "",
            )
        )

        print(
            f"Content-Type recebido: "
            f"{content_type}"
        )

        # ----------------------------------------------------
        # CRIA DIRETÓRIO
        # ----------------------------------------------------

        destino.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ----------------------------------------------------
        # SALVA O ARQUIVO
        # ----------------------------------------------------

        with destino.open("wb") as arquivo:
            for bloco in response.iter_content(
                chunk_size=8192
            ):
                if bloco:
                    arquivo.write(bloco)

        # ----------------------------------------------------
        # VALIDA ARQUIVO
        # ----------------------------------------------------

        if not destino.exists():
            print(
                "O arquivo não foi criado."
            )

            return None

        tamanho = destino.stat().st_size

        if tamanho == 0:
            print(
                "O arquivo recebido está vazio."
            )

            destino.unlink(
                missing_ok=True
            )

            return None

        print(
            f"Arquivo recebido: "
            f"{tamanho} bytes"
        )

        return destino

    except requests.exceptions.Timeout:
        print(
            "Timeout durante o download "
            "do documento."
        )

        return None

    except requests.exceptions.ConnectionError as exc:
        print(
            "Erro de conexão durante "
            f"o download: {exc}"
        )

        return None

    except requests.RequestException as exc:
        print(
            f"Erro ao baixar documento: {exc}"
        )

        return None

    except OSError as exc:
        print(
            f"Erro ao salvar documento: {exc}"
        )

        return None


# ============================================================
# DOWNLOAD DE TODOS OS DOCUMENTOS DA ATA
# ============================================================

def baixar_todos_documentos_ata(
    cnpj: str,
    ano_compra: int,
    sequencial_compra: int,
    sequencial_ata: int,
    pasta_destino: str | Path = "downloads_pncp",
) -> list[Path]:
    """
    Lista e baixa todos os documentos de uma Ata.

    Retorna uma lista contendo os caminhos dos arquivos
    que foram baixados com sucesso.
    """

    documentos = consultar_documentos_ata(
        cnpj=cnpj,
        ano_compra=ano_compra,
        sequencial_compra=sequencial_compra,
        sequencial_ata=sequencial_ata,
    )

    pasta_destino = Path(
        pasta_destino
    )

    pasta_destino.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivos_baixados: list[Path] = []

    for documento in documentos:
        sequencial_documento = (
            documento.get(
                "sequencialDocumento"
            )
        )

        url_documento = (
            documento.get("url")
        )

        if sequencial_documento is None:
            print(
                "Documento sem "
                "sequencialDocumento. Ignorando."
            )

            continue

        destino = (
            pasta_destino
            / (
                f"ata_{sequencial_ata}"
                f"_documento_"
                f"{sequencial_documento}.pdf"
            )
        )

        caminho = baixar_documento_ata(
            cnpj=cnpj,
            ano_compra=ano_compra,
            sequencial_compra=sequencial_compra,
            sequencial_ata=sequencial_ata,
            sequencial_documento=(
                sequencial_documento
            ),
            destino=destino,
            url_documento=url_documento,
        )

        if caminho:
            arquivos_baixados.append(
                caminho
            )

    return arquivos_baixados


# ============================================================
# CONSULTAR DOCUMENTOS DO CONTRATO
# ============================================================

def consultar_documentos_contrato(
        contrato: dict
) -> list[dict]:
    """
    Lista os documentos vinculados a um contrato.
    Não faz download.
    """

    orgao_entidade = contrato.get("orgaoEntidade") or {}

    cnpj = orgao_entidade.get("cnpj")
    ano = contrato.get("anoContrato")
    sequencial = contrato.get("sequencialContrato")

    if not cnpj or ano is None or sequencial is None:
        print(
            "Contrato sem cnpj, anoContrato ou "
            "sequencialContrato. Ignorando."
        )
        return []
    url = (
        f"{BASE_URL_PNCP}/v1/orgaos/"
        f"{cnpj}/contratos/"
        f"{ano}/{sequencial}/arquivos"
    )

    try:
        response = pncp_client.get(url)

    except requests.RequestException as exc:
        print(
            f"Erro ao listar documentos do contrato "
            f"{contrato.get('numeroControlePNCP')}: {exc}"
        )
        return []

    if response.status_code == 204:
        return []

    if response.status_code != 200:
        print(
            f"Erro HTTP {response.status_code} ao listar "
            f"documentos do contrato "
            f"{contrato.get('numeroControlePNCP')}"
        )
        return []
    try:
        dados = response.json()
    except ValueError:
        print("Resposta de documentos não é um JSON válido.")
        return []

    if isinstance(dados, list):
        return dados

    if isinstance(dados, dict):
        return (
            dados.get("documentos")
            or dados.get("data")
            or []
        )

    return []


# ============================================================
# BAIXAR DOCUMENTOS DO CONTRATO
# ============================================================


def _nome_seguro(texto: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "-", texto)


def _url_pura(url: str) -> str:
    if url.startswith("[") and "](" in url and url.endswith(")"):
        return url.rsplit("](", 1)[1][:-1]
    return url


def _extensao_por_content_type(
        content_type: str,
        url: str
) -> str:
    content_type = content_type.lower().split(";")[0].strip()

    extensoes = {
        "application/pdf": ".pdf",
        "application/zip": ".zip",
        "application/x-rar-compressed": ".rar",
        "application/vnd.rar": ".rar",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.oasis.opendocument.text": ".odt",
        "image/jpeg": ".jpg",
        "image/png": ".png",
    }

    if content_type in extensoes:
        return extensoes[content_type]

    extensao_url = Path(urlparse(url).path).suffix

    if extensao_url:
        return extensao_url.lower()

    return ".bin"


def baixar_documento_contrato(
    numero_controle: str,
    documento: dict[str, Any],
    pasta_base: Path | str = "data/documents/original",

) -> Path | None:
    """
    Baixa um documento do manifesto e preserva seu formato original.
    """

    url = documento.get("url") or documento.get("uri")

    if not url:
        print("Documento sem URL. Ignorando.")
        return None

    url = _url_pura(str(url))

    sequencial = documento.get("sequencialDocumento", "sem_sequencial")

    pasta_contrato = (
        Path(pasta_base) / _nome_seguro(numero_controle)
    )

    try:
        response = pncp_client.get(
            url,
            stream=True,
            timeout=120
        )

        if response.status_code != 200:
            print(
                f"Erro HTTP {response.status_code} | "
                f"download | contrato={numero_controle}"
            )
            return None

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        extensao = _extensao_por_content_type(
            content_type,
            url,
        )
        destino = (
            pasta_contrato
            / f"documento_{sequencial}{extensao}"
        )

        temporario = destino.with_name(
            f"{destino.name}.part"
        )

        pasta_contrato.mkdir(
            parents=True,
            exist_ok=True,
        )

        with temporario.open("wb") as arquivo:
            for bloco in response.iter_content(
                chunk_size=82192
            ):
                if bloco:
                    arquivo.write(bloco)

        response.close()

        if temporario.stat().st_size == 0:
            temporario.unlink(missing_ok=True)

            print(
                f"Arquivo vazio | contrato={numero_controle}"
            )
            return None

        temporario.replace(destino)

        print(
            f"Baixado | contrato={numero_controle} | "
            f"arquivo={destino.name} | "
            f"tipo={content_type}"
        )

        return destino
    except requests.RequestException as exc:

        print(
            f"Erro no download | contrato={numero_controle} | "
            f"{exc}"
        )
        return None

    except OSError as exc:
        print(
            f"Erro ao salvar arquivo | contrato={numero_controle} | "
            f"{exc}"
        )
        return None


def baixar_documentos_manifesto(
        manifesto: list[dict[str, Any]],
        limite_contratos: int = 5,
        limite_documentos_por_contrato:  int = 1,
) -> int:
    quantidade_baixada = 0

    for contrato in manifesto[:limite_contratos]:
        numero_controle = contrato.get("numeroControlePNCP")

        if not numero_controle:
            continue

        documentos = contrato.get("documentos") or []

        for documento in documentos[:limite_documentos_por_contrato]:

            download_anterior = documento.get("download") or {}

            caminho_anterior = download_anterior.get("caminho")

            if (
                download_anterior.get("status") == "baixado"
                and caminho_anterior
                and Path(caminho_anterior).exists()
            ):
                print(
                    f"Já baixado | contrato={numero_controle}"
                )
                continue

            caminho = baixar_documento_contrato(
                numero_controle=numero_controle,
                documento=documento,
            )

            if caminho:
                documento["download"] = {
                    "status": "baixado",
                    "caminho": str(caminho),
                }

                quantidade_baixada += 1

            else:
                documento["download"] = {
                    "status": "erro",
                }

        time.sleep(5)

    return quantidade_baixada


def detectar_formato_arquivo(
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
    extensao, formato = detectar_formato_arquivo(caminho)

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
    pasta_base: Path | str = "data/documents/extracted",
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
