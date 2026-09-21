from datetime import date
from pathlib import Path

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

def coletar_contratos(
    data_inicial: str,
    data_final: str,
    tamanho_pagina: int = 50,
) -> list[dict]:
    """
    Consulta contratos publicados no PNCP.
    """

    if tamanho_pagina <= 0:
        tamanho_pagina = 50

    resultados: list[dict] = []

    controles_encontrados: set[str] = set()

    pagina = 1

    while True:
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

            break

        except requests.exceptions.ConnectionError as exc:
            print(
                "Erro de conexão | contratos | "
                f"página={pagina} | {exc}"
            )

            break

        except requests.RequestException as exc:
            print(
                "Erro HTTP | contratos | "
                f"página={pagina} | {exc}"
            )

            break

        if response.status_code == 204:
            break

        if response.status_code == 429:
            print(
                "PNCP retornou HTTP 429 "
                "ao consultar contratos."
            )

            break

        if response.status_code != 200:
            print(
                f"Erro {response.status_code} | "
                f"contratos | página={pagina}"
            )

            try:
                print(response.text)
            except Exception:
                pass

            break

        try:
            dados = response.json()

        except ValueError:
            print(
                "Resposta inválida do PNCP "
                "ao consultar contratos."
            )

            break

        registros = (
            dados.get("data")
            or []
        )

        if not registros:
            break

        # ----------------------------------------------------
        # REMOVE DUPLICADOS
        # ----------------------------------------------------

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

        total_paginas = (
            dados.get("totalPaginas")
            or 1
        )

        if pagina >= total_paginas:
            break

        pagina += 1

    return resultados


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
