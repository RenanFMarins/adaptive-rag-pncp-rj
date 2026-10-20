from pathlib import Path
from typing import Any

from src.base_estruturada.pncp.service import (
    baixar_documento_ata,
    carregar_modalidades,
    coletar_contratacoes,
    coletar_contratacoes_abertas,
    coletar_contratos,
    consultar_atas_compra,
    consultar_documentos_ata,
    consultar_quantidade_documentos_ata,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Compra real já validada no PNCP.
CNPJ = "00394452000103"
ANO_COMPRA = 2024
SEQUENCIAL_COMPRA = 22765
SEQUENCIAL_ATA = 1

# Período usado nas consultas gerais.
DATA_INICIAL = "20260917"
DATA_FINAL = "20260918"

# Estado usado nos testes.
UF = "RJ"

# Pregão Eletrônico.
MODALIDADE_PREGAO_ELETRONICO = 1

# Diretório onde os documentos serão salvos.
PASTA_DOWNLOADS = Path("downloads_pncp")

""""""
# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================


def titulo(texto: str) -> None:
    """
    Exibe um título no terminal.
    """

    print()
    print("=" * 80)
    print(texto)
    print("=" * 80)


def linha() -> None:
    """
    Exibe uma linha separadora.
    """

    print("-" * 80)


def exibir_campo(
    nome: str,
    valor: Any,
) -> None:
    """
    Exibe um campo de forma padronizada.
    """

    print(f"{nome}: {valor}")


# ============================================================
# 1. MODALIDADES
# ============================================================

def testar_modalidades() -> None:
    """
    Consulta as modalidades ativas disponíveis no PNCP.
    """

    titulo("1. MODALIDADES DO PNCP")

    modalidades = carregar_modalidades()

    if not modalidades:
        print("Nenhuma modalidade encontrada.")
        return

    print(
        f"Total de modalidades ativas: "
        f"{len(modalidades)}"
    )

    print()

    for codigo, nome in modalidades.items():
        print(
            f"{codigo:>3} - {nome}"
        )


# ============================================================
# 2. CONTRATAÇÕES PUBLICADAS
# ============================================================

def testar_contratacoes() -> None:
    """
    Consulta contratações publicadas no RJ.

    Utilizamos somente Pregão Eletrônico para reduzir
    a quantidade de chamadas realizadas contra o PNCP.
    """

    titulo("2. CONTRATAÇÕES PUBLICADAS")

    print(
        f"Consultando Pregões Eletrônicos em {UF}..."
    )

    dados = coletar_contratacoes(
        uf=UF,
        data_inicial=DATA_INICIAL,
        data_final=DATA_FINAL,
        modalidades=[
            MODALIDADE_PREGAO_ELETRONICO
        ],

        # O PNCP exige valor mínimo de 10
        # para este endpoint.
        tamanho_pagina=10,
    )

    print()
    exibir_campo(
        "Total encontrado",
        len(dados),
    )

    for item in dados[:5]:
        linha()

        exibir_campo(
            "Controle PNCP",
            item.get("numeroControlePNCP"),
        )

        exibir_campo(
            "Objeto",
            item.get("objetoCompra"),
        )

        orgao = (
            item.get("orgaoEntidade")
            or {}
        )

        exibir_campo(
            "Órgão",
            orgao.get("razaoSocial"),
        )


# ============================================================
# 3. CONTRATOS
# ============================================================

def testar_contratos() -> None:
    """
    Consulta contratos publicados no período configurado.
    """

    titulo("3. CONTRATOS")

    print("Consultando contratos...")

    dados = coletar_contratos(
        data_inicial=DATA_INICIAL,
        data_final=DATA_FINAL,

        # O endpoint de contratos rejeitou tamanho 5.
        # Mantemos 50 para esta consulta.
        tamanho_pagina=50,
    )

    print()

    exibir_campo(
        "Total coletado",
        len(dados),
    )

    for item in dados[:5]:
        linha()

        exibir_campo(
            "Controle PNCP",
            item.get("numeroControlePNCP"),
        )

        objeto = (
            item.get("objetoContrato")
            or item.get("objeto")
        )

        exibir_campo(
            "Objeto",
            objeto,
        )


# ============================================================
# 4. CONTRATAÇÕES COM PROPOSTAS ABERTAS
# ============================================================

def testar_contratacoes_abertas() -> None:
    """
    Consulta contratações com período de proposta aberto.
    """

    titulo(
        "4. CONTRATAÇÕES COM PROPOSTAS ABERTAS"
    )

    dados = coletar_contratacoes_abertas(
        data_final=DATA_FINAL,
        uf=UF,
        pagina=1,
    )

    if not dados:
        print(
            "Nenhuma contratação aberta encontrada "
            "ou o PNCP não respondeu."
        )
        return

    itens = dados.get("data") or []

    exibir_campo(
        "Registros na página",
        len(itens),
    )

    for item in itens[:5]:
        linha()

        exibir_campo(
            "Controle PNCP",
            item.get("numeroControlePNCP"),
        )

        exibir_campo(
            "Objeto",
            item.get("objetoCompra"),
        )


# ============================================================
# 5. ATA REAL
# ============================================================

def testar_ata() -> list[dict]:
    """
    Consulta a Ata de Registro de Preços da compra
    que já validamos anteriormente no PNCP.
    """

    titulo("5. ATA DE REGISTRO DE PREÇOS")

    print("Compra utilizada:")
    print()

    exibir_campo(
        "CNPJ",
        CNPJ,
    )

    exibir_campo(
        "Ano",
        ANO_COMPRA,
    )

    exibir_campo(
        "Sequencial da compra",
        SEQUENCIAL_COMPRA,
    )

    print()

    atas = consultar_atas_compra(
        cnpj=CNPJ,
        ano_compra=ANO_COMPRA,
        sequencial_compra=SEQUENCIAL_COMPRA,
    )

    exibir_campo(
        "Total de atas encontradas",
        len(atas),
    )

    for ata in atas:
        linha()

        exibir_campo(
            "Número da ata",
            ata.get(
                "numeroAtaRegistroPreco"
            ),
        )

        exibir_campo(
            "Ano",
            ata.get("anoAta"),
        )

        exibir_campo(
            "Sequencial",
            ata.get("sequencialAta"),
        )

        exibir_campo(
            "Controle PNCP",
            ata.get("numeroControlePNCP"),
        )

        exibir_campo(
            "Possibilidade de adesão",
            ata.get("possibilidadeAdesao"),
        )

        objeto = (
            ata.get("objetoContratacao")
            or ata.get("objetoCompra")
            or ata.get("objeto")
        )

        exibir_campo(
            "Objeto",
            objeto,
        )

    return atas


# ============================================================
# 6. QUANTIDADE DE DOCUMENTOS
# ============================================================

def testar_quantidade_documentos() -> int:
    """
    Consulta quantos documentos existem na Ata.
    """

    titulo(
        "6. QUANTIDADE DE DOCUMENTOS DA ATA"
    )

    quantidade = (
        consultar_quantidade_documentos_ata(
            cnpj=CNPJ,
            ano_compra=ANO_COMPRA,
            sequencial_compra=SEQUENCIAL_COMPRA,
            sequencial_ata=SEQUENCIAL_ATA,
        )
    )

    exibir_campo(
        "Quantidade de documentos",
        quantidade,
    )

    return quantidade


# ============================================================
# 7. DOCUMENTOS DA ATA
# ============================================================

def testar_documentos() -> list[dict]:
    """
    Lista os documentos associados à Ata.
    """

    titulo("7. DOCUMENTOS DA ATA")

    documentos = consultar_documentos_ata(
        cnpj=CNPJ,
        ano_compra=ANO_COMPRA,
        sequencial_compra=SEQUENCIAL_COMPRA,
        sequencial_ata=SEQUENCIAL_ATA,
    )

    exibir_campo(
        "Total de documentos",
        len(documentos),
    )

    for documento in documentos:
        linha()

        exibir_campo(
            "Sequencial",
            documento.get(
                "sequencialDocumento"
            ),
        )

        exibir_campo(
            "Título",
            documento.get("titulo"),
        )

        exibir_campo(
            "Tipo",
            documento.get(
                "tipoDocumentoNome"
            ),
        )

        exibir_campo(
            "URL",
            documento.get("url"),
        )

    return documentos


# ============================================================
# 8. DOWNLOAD DO PRIMEIRO DOCUMENTO
# ============================================================

def testar_download(
    documentos: list[dict],
) -> Path | None:
    """
    Baixa o primeiro documento retornado pela Ata.

    O sequencial e a URL são obtidos diretamente
    da resposta do PNCP.
    """

    titulo(
        "8. DOWNLOAD DO PRIMEIRO DOCUMENTO"
    )

    if not documentos:
        print(
            "Não existem documentos para baixar."
        )
        return None

    documento = documentos[0]

    sequencial_documento = documento.get(
        "sequencialDocumento"
    )

    url_documento = documento.get("url")

    if not sequencial_documento:
        print(
            "O documento não possui "
            "sequencialDocumento."
        )
        return None

    if not url_documento:
        print(
            "O documento não possui URL."
        )
        return None

    PASTA_DOWNLOADS.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino = (
        PASTA_DOWNLOADS
        / (
            f"ata_{SEQUENCIAL_ATA}"
            f"_documento_"
            f"{sequencial_documento}.pdf"
        )
    )

    exibir_campo(
        "Documento",
        sequencial_documento,
    )

    exibir_campo(
        "URL",
        url_documento,
    )

    exibir_campo(
        "Destino",
        destino,
    )

    print()
    print("Iniciando download...")

    caminho = baixar_documento_ata(
        cnpj=CNPJ,
        ano_compra=ANO_COMPRA,
        sequencial_compra=SEQUENCIAL_COMPRA,
        sequencial_ata=SEQUENCIAL_ATA,
        sequencial_documento=(
            sequencial_documento
        ),
        destino=destino,
        url_documento=url_documento,
    )

    print()

    if caminho is None:
        print(
            "Não foi possível realizar "
            "o download."
        )
        return None

    print(
        "Download realizado com sucesso."
    )

    exibir_campo(
        "Arquivo salvo em",
        caminho,
    )

    if caminho.exists():
        tamanho_bytes = (
            caminho.stat().st_size
        )

        tamanho_mb = (
            tamanho_bytes
            / 1024
            / 1024
        )

        exibir_campo(
            "Tamanho",
            f"{tamanho_mb:.2f} MB",
        )

    return caminho


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main() -> None:
    """
    Executa os testes de integração real com o PNCP.
    """

    titulo(
        "TESTE DE INTEGRAÇÃO REAL COM O PNCP"
    )

    print(
        "Este programa faz chamadas reais "
        "para a API do PNCP."
    )

    # --------------------------------------------------------
    # CONSULTAS GERAIS
    # --------------------------------------------------------

    testar_modalidades()

    testar_contratacoes()

    testar_contratos()

    testar_contratacoes_abertas()

    # --------------------------------------------------------
    # ATA REAL JÁ VALIDADA
    # --------------------------------------------------------

    testar_ata()

    testar_quantidade_documentos()

    documentos = testar_documentos()

    # --------------------------------------------------------
    # DOWNLOAD REAL
    # --------------------------------------------------------

    testar_download(documentos)

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    titulo("TESTE FINALIZADO")


if __name__ == "__main__":
    main()
