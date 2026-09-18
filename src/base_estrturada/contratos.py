import requests
import time
from datetime import date


BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
BASE_URL_CONTRATOS = "https://pncp.gov.br/api/consulta/v1/contratos"
BASE_URL_PROPOSTA = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"

sessao = requests.Session()
sessao.headers.update({"Accept": "application/json",
                      "User-Agent": "radio-licitacoes/1.0"})


def carregar_modalidades(somente_ativas=True):
    # Busca a tabela de dominio direto da API.
    url = "https://pncp.gov.br/api/pncp/v1/modalidades"
    r = sessao.get(url, timeout=30)
    r.raise_for_status()
    dados = r.json()
    if somente_ativas:
        dados = [d for d in dados if d.get("statusAtivo")]
    return {d["id"]: d["nome"].strip() for d in dados}


def coletar_contratacoes(uf, data_inicial, data_final, modalidades=None, tamanho_pagina=10):

    if modalidades is None:
        modalidades = list(carregar_modalidades().keys())

    registros = []
    vistos = set()

    for modalidade in modalidades:
        pagina = 1
        while True:
            params = {
                "dataInicial": data_inicial,
                "dataFinal": data_final,
                "uf": uf,
                "codigoModalidadeContratacao": modalidade,
                "tamanhoPagina": tamanho_pagina,
                "pagina": pagina
            }

            try:
                response = sessao.get(BASE_URL, params=params, timeout=45)

                if response.status_code == 204:
                    break
                if response.status_code == 429:
                    print(
                        "-> [Aviso] Erro 429 (Rate Limit). Aguardando 15 segundos para o IP liberar...")
                    time.sleep(15)
                    continue
                if response.status_code != 200:
                    print(
                        f"erro {response.status_code} | modalidade={modalidade} pagina={pagina} | {response.text[:200]}")
                    break

                corpo = response.json()

                for item in corpo.get("data") or []:

                    chave = item.get("numeroControlePNCP")
                    if chave not in vistos:
                        vistos.add(chave)
                        registros.append(item)

                total_paginas = corpo.get("totalPaginas") or 0
                if pagina >= total_paginas:
                    break
                pagina += 1
                time.sleep(1.5)

            except requests.exceptions.RequestException as e:
                print(
                    f"Erro de conexão na modalidade {modalidade}, página {pagina}: {e}")
                break
        print("Respeitando intervalo entre modalidades...")
        time.sleep(3)

    return registros

# contratos assinados por data de publicação


def coletar_contratos(data_inicial, data_final):
    registros = []
    vistos = set()
    pagina = 1

    while True:
        params = {
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "pagina": pagina}

        try:
            response = sessao.get(BASE_URL_CONTRATOS,
                                  params=params, timeout=120)

            response.raise_for_status()
            print(response.status_code)

            corpo = response.json()

            for item in corpo.get("data") or []:

                chave = item.get("numeroControlePNCP")

                if chave and chave not in vistos:
                    vistos.add(chave)
                    registros.append(item)

                total_paginas = corpo.get("totalPaginas") or 0

                if pagina >= total_paginas:
                    break

                pagina += 1
                time.sleep(1.5)

        except Exception as e:
            print(f"Erro na página {pagina}: {e}")
            break

    return registros


def coletar_contratacoes_abertas():

    hoje = date.today()
    params = {"dataFinal": hoje, "uf": "RJ", "pagina": 1}

    response = sessao.get(
        BASE_URL_PROPOSTA,
        params=params,
        timeout=45
    )

    response.raise_for_status()

    corpo = response.json()

    return corpo


modalidades = carregar_modalidades()
"""
dados = coletar_contratacoes(
    uf="RJ", data_inicial="20260901", data_final="20260916")
"""
dados = coletar_contratos(data_inicial="20260901", data_final="20260916")

print(f"total coletado: {len(dados)}")
print(f"total coletado: {dados[:1]}")
