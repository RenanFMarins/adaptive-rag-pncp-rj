from src.base_estruturada.pncp.repository import (
    adicionar_contratacoes_novas,
    salvar_paginas_com_erro,
    salvar_json,
    salvar_lista_de_documentos,
    carregar_json
)

from src.base_estruturada.pncp.service import (
    coletar_contratos, consultar_documentos_contrato,
    baixar_documentos_manifesto,
    identificar_arquivos_do_manifesto,
    extrair_zips_do_manifesto,
    coletar_contratacoes, consultar_detalhe_contratacao, salvar_lista_documentos_contratacao

)


import json
from pathlib import Path

ARQUIVO_CONTRATOS = Path(
    "data/normalized/contratos_rj.json"
)

ARQUIVO_CONTRATACOES = Path(
    "data/normalized/contratacoes_rj.json"
)
CAMINHO_MANIFESTO_CONTRATOS = Path("data/normalized/contratos_documentos.json")

CAMINHO_DOCUMENTOS = Path("data/documents/original")

CAMINHO_BASE_CONTRATACOES = Path("data/documents/original/contratacoes")

CAMINHO_MANIFESTO_CONTRATACOES = Path(
    "data/normalized/contratacoes_documentos.json"
)

CAMINHO_ERROR_CONTRATACOES = Path(
    "data/checkpoints/contratacoes_paginas_com_erro.json")

CAMINHO_EXTRAIR_CONTRATACOES = Path("data/documents/extracted/contratacoes")

"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from src.base_estrturada.pncp.service import (
    coletar_contratos,

)

# 1. Defina o período que você quer testar
# Ajuste para o formato exigido pela sua API (Ex: AAAA-MM-DD)
DATA_INICIO = (datetime.today() - timedelta(days=7)).strftime("%Y%m%d")
DATA_FIM = datetime.today().strftime("%Y%m%d")

print(f"Buscando contratos entre {DATA_INICIO} e {DATA_FIM}...")

# 2. Chama a função e armazena o retorno na variável 'contratos_retornados'
contratos_retornados = coletar_contratos(
    data_inicial=DATA_INICIO, data_final=DATA_FIM, tamanho_pagina=50
)

# =====================================================================
# BLCO DE TESTES E PRINTS DE VERIFICAÇÃO (FORA DA FUNÇÃO)
# =====================================================================
print("\n" + "=" * 60)
print("📊 RESULTADO DOS TESTES DE RETORNO")
print("=" * 60)

# Verificação 1: Quantidade total de documentos
total_documentos = len(contratos_retornados)
print(f"🔹 Quantidade de documentos retornados: {total_documentos}")

# Verificação 2: Base do que está retornando (Amostra do primeiro documento)
print("-" * 60)
if total_documentos > 0:
    print("📝 Estrutura da base (Primeiro documento retornado):")

    # Pegamos apenas o primeiro índice [0] da lista
    primeiro_documento = contratos_retornados[0]

    # json.dumps formata o dicionário para ficar legível no terminal
    print(json.dumps(primeiro_documento, indent=4, ensure_ascii=False))
else:
    print("⚠️  A busca não retornou nenhum documento para este período.")

print("=" * 60 + "\n")



def main() -> None:
    data_inicial = "20260920"
    data_final = "20260922"

    print(
        f"Buscando contratos entre "
        f"{data_inicial} e {data_final}..."
    )

    resultado = coletar_contratos(
        data_inicial=data_inicial,
        data_final=data_final,
        tamanho_pagina=50,
    )

    quantidade_nova = adicionar_contratos_novos(
        resultado.contratos
    )

    salvar_paginas_com_erro(
        data_inicial=data_inicial,
        data_final=data_final,
        paginas=resultado.paginas_com_erro,
    )

    print("\n" + "=" * 60)
    print("RESULTADO DA COLETA")
    print("=" * 60)
    print(
        f"Contratos RJ recebidos nesta execução: "
        f"{len(resultado.contratos)}"
    )
    print(
        f"Contratos novos adicionados ao JSON: "
        f"{quantidade_nova}"
    )

    if resultado.paginas_com_erro:
        print(
            "Páginas pendentes para retentativa: "
            f"{resultado.paginas_com_erro}"
        )
    else:
        print("Nenhuma página apresentou falha.")


if __name__ == "__main__":
    main()



manifesto = carregar_json(CAMINHO_MANIFESTO,
                          padrao=[],)

# salvar_lista_de_documentos(dados)

quantidade = extrair_zips_do_manifesto(manifesto)

salvar_json(CAMINHO_MANIFESTO, manifesto)

print(f"{quantidade} ZIPs extraídos.")


CAMINHO_MANIFESTO_CONTRATACOES = (
    "data/normalized/contratacoes_documentos.json"
)
 coletar_contratacoes,consultar_detalhe_contratacao, salvar_lista_documentos_contratacao

 

===============================================

contratacoes = coletar_contratacoes(
    uf="RJ",
    data_inicial="20260920",
    data_final="20260922",
    modalidades=[6],
    tamanho_pagina=10,
)

# Teste opcional de detalhe: apenas uma contratação.
if contratacoes:
    detalhe = consultar_detalhe_contratacao(
        contratacoes[0]
    )

    print("Detalhe retornado:", detalhe)

manifesto = salvar_lista_documentos_contratacao(
    contratacoes=contratacoes,
    caminho_manifesto=CAMINHO_MANIFESTO_CONTRATACOES,
    limite=5,
)

=========================================================
 



def main() -> None:
    data_inicial = "20260920"
    data_final = "20260922"

    print(
        f"Buscando contratos entre "
        f"{data_inicial} e {data_final}..."
    )

    resultado = coletar_contratacoes(
        uf="RJ",
        data_inicial=data_inicial,
        data_final=data_final,
        tamanho_pagina=50,
    )

    quantidade_nova = adicionar_contratacoes_novas(
        resultado.contratacoes
    )

    salvar_paginas_com_erro(
        data_inicial=data_inicial,
        data_final=data_final,
        paginas=resultado.paginas_com_erro,
        caminho=CAMINHO_MANIFESTO_CONTRATACOES
    )

    print("\n" + "=" * 60)
    print("RESULTADO DA COLETA")
    print("=" * 60)
    print(
        f"Contratações RJ recebidos nesta execução: "
        f"{len(resultado.contratacoes)}"
    )
    print(
        f"Contratações novos adicionados ao JSON: "
        f"{quantidade_nova}"
    )

    if resultado.paginas_com_erro:
        print(
            "Páginas pendentes para retentativa: "
            f"{resultado.paginas_com_erro}"
        )
    else:
        print("Nenhuma página apresentou falha.")


if __name__ == "__main__":
    main()


contratacoes = carregar_json(ARQUIVO_CONTRATACOES,
                             padrao=[],)

print(len(contratacoes))

manifesto = salvar_lista_documentos_contratacao(
    contratacoes=contratacoes,
    caminho_manifesto=CAMINHO_MANIFESTO_CONTRATACOES,
    limite=5,
)

"""

manifesto = carregar_json(CAMINHO_MANIFESTO_CONTRATACOES,
                          padrao=[],)


qtd_baixada = baixar_documentos_manifesto(
    manifesto=manifesto,
    pasta_base=CAMINHO_BASE_CONTRATACOES,
    limite_contratos=5,
    limite_documentos_por_contrato=1,
)
print(f"Downloads concluídos: {qtd_baixada}")

qtd_identificada = identificar_arquivos_do_manifesto(manifesto)
print(f"Arquivos identificados e checados: {qtd_identificada}")

qtd_extraida = extrair_zips_do_manifesto(
    manifesto=manifesto,
    pasta_base=CAMINHO_EXTRAIR_CONTRATACOES
)
print(f"Arquivos ZIP descompactados com sucesso: {qtd_extraida}")

# 💾 Salva o estado final do manifesto limpo
salvar_json(CAMINHO_MANIFESTO_CONTRATACOES, manifesto)

# quantidade = extrair_zips_do_manifesto(manifesto, CAMINHO_EXTRAIR_CONTRATACOES)

# salvar_json(CAMINHO_MANIFESTO_CONTRATACOES, manifesto)

# print(f"{quantidade} ZIPs extraídos.")
