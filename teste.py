from src.base_estrturada.pncp.repository import (
    adicionar_contratos_novos,
    salvar_paginas_com_erro,
    salvar_json,
    salvar_lista_de_documentos,
    carregar_json
)

from src.base_estrturada.pncp.service import (
    coletar_contratos, consultar_documentos_contrato,
    baixar_documentos_manifesto,
    identificar_arquivos_do_manifesto,
    extrair_zips_do_manifesto)


import json
from pathlib import Path

ARQUIVO_CONTRATOS = Path(
    "data/normalized/contratos_rj.json"
)
CAMINHO_MANIFESTO = Path("data/normalized/contratos_documentos.json")

CAMINHO_DOCUMENTOS = Path("data/documents/original")

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

"""

manifesto = carregar_json(CAMINHO_MANIFESTO,
                          padrao=[],)

# salvar_lista_de_documentos(dados)

quantidade = extrair_zips_do_manifesto(manifesto)

salvar_json(CAMINHO_MANIFESTO, manifesto)

print(f"{quantidade} ZIPs extraídos.")
