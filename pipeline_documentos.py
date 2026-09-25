"""
Pipeline de Documentos — Contratos e Contratações
==================================================

Este script roda APENAS a segunda parte do fluxo (download e organização
dos documentos). A primeira parte (coleta de contratos/contratações via
API) já tem uma base pronta e por isso fica comentada/desativada abaixo,
para não disparar requisições desnecessárias de novo.

As funções (coletar_contratos, adicionar_contratos_novos,
salvar_paginas_com_erro, carregar_json, salvar_json,
salvar_lista_documentos_contratacao, baixar_documentos_manifesto,
identificar_arquivos_do_manifesto, extrair_zips_do_manifesto) são
assumidas como já existentes no seu projeto (importe-as do módulo onde
estão implementadas). Aqui só está a ORQUESTRAÇÃO do fluxo.
"""

from src.base_estrturada.pncp.repository import (
    adicionar_contratacoes_novas,
    adicionar_contratos_novos,
    salvar_paginas_com_erro,
    salvar_json,
    salvar_lista_de_documentos_contratos,
    carregar_json, salvar_lista_documentos_contratacao,
    salvar_lista_de_documentos_contratos,
    identificar_arquivos_do_manifesto,
    extrair_zips_do_manifesto,

)

from src.base_estrturada.pncp.service import (
    coletar_contratos, consultar_documentos_contrato,
    baixar_documentos_manifesto,
    coletar_contratacoes, consultar_detalhe_contratacao

)


# -----------------------------------------------------------------
# PARTE 1 — COLETA DE CONTRATAÇÕES (DESATIVADA)
# -----------------------------------------------------------------
# Já existe uma base de contratações coletada e estruturada.
# Não rodar de novo agora (evita requisições demoradas e desnecessárias).
# Quando precisar atualizar a base, é só descomentar este bloco
# (lembrando de definir data_inicial e data_final antes).
#
# resultado = coletar_contratacoes(
#     uf="RJ",
#     data_inicial=data_inicial,
#     data_final=data_final,
#     tamanho_pagina=50,
# )
# quantidade_nova = adicionar_contratacoes_novas(
#     resultado.contratacoes
# )
# salvar_paginas_com_erro(
#     data_inicial=data_inicial,
#     data_final=data_final,
#     paginas=resultado.paginas_com_erro,
#     caminho=CAMINHO_MANIFESTO_CONTRATACOES,
# )


# ---------------------------------------------------------------------------
# PARTE 2 — DOCUMENTOS (o que roda agora)
# ---------------------------------------------------------------------------

def processar_documentos(
    nome_etapa: str,
    arquivo_entrada: str,
    caminho_manifesto: str,
    pasta_base: str,
    pasta_extrair: str,
    funcao_gerar_manifesto,
    limite_contratos: int = 5,
    limite_documentos_por_contrato: int = 1,
):
    """
    Roda o fluxo completo de documentos para uma base já coletada
    (contratos OU contratações — o mesmo fluxo serve para os dois).

    Passos:
        1. Carrega os itens já salvos (arquivo_entrada).
        2. Gera o manifesto com a lista de documentos de cada item.
        3. Recarrega o manifesto salvo em disco.
        4. Baixa os documentos listados no manifesto.
        5. Identifica o tipo de cada arquivo baixado (PDF, ZIP, etc.).
        6. Extrai os arquivos que vierem em ZIP/RAR.
        7. Salva o manifesto atualizado (estado final).

    Parâmetros
    ----------
    nome_etapa : str
        Só para identificar nos prints/logs (ex: "Contratos" ou "Contratações").
    arquivo_entrada : str
        Caminho do JSON com os itens já coletados.
    caminho_manifesto : str
        Caminho onde o manifesto (lista de documentos) é salvo/lido.
    pasta_base : str
        Pasta onde os documentos baixados são salvos.
    pasta_extrair : str
        Pasta onde os arquivos ZIP/RAR extraídos são salvos.
    limite_contratos : int
        Quantos itens processar (útil para testes/execuções parciais).
    limite_documentos_por_contrato : int
        Quantos documentos baixar por item.

    Retorna
    -------
    dict com os totais de cada etapa (baixados, identificados, extraídos).
    """
    print(f"\n=== {nome_etapa}: iniciando processamento de documentos ===")

    # 1. Carrega os itens já coletados (contratos ou contratações)
    itens = carregar_json(arquivo_entrada, padrao=[])
    print(f"[{nome_etapa}] {len(itens)} itens carregados de '{arquivo_entrada}'.")

    # 2. Gera o manifesto com a lista de documentos de cada item
    manifesto = funcao_gerar_manifesto(
        itens, caminho_manifesto, limite_contratos,
    )

    # 3. Recarrega o manifesto do disco, garantindo que estamos trabalhando
    #    com exatamente o que foi salvo (e não só com o retorno em memória)
    manifesto = carregar_json(caminho_manifesto, padrao=[])

    # 4. Baixa os documentos listados no manifesto
    #    (essa função também marca, no próprio manifesto, se cada
    #    documento foi baixado com sucesso ou não)
    qtd_baixada = baixar_documentos_manifesto(
        manifesto=manifesto,
        pasta_base=pasta_base,
        limite_contratos=limite_contratos,
        limite_documentos_por_contrato=limite_documentos_por_contrato,
    )
    print(f"[{nome_etapa}] Downloads concluídos: {qtd_baixada}")

    # 5. Identifica o tipo de cada arquivo baixado (PDF, ZIP, RAR, etc.)
    qtd_identificada = identificar_arquivos_do_manifesto(manifesto)
    print(f"[{nome_etapa}] Arquivos identificados e checados: {qtd_identificada}")

    # 6. Extrai os arquivos que vierem compactados (ZIP/RAR)
    qtd_extraida = extrair_zips_do_manifesto(
        manifesto=manifesto,
        pasta_base=pasta_extrair,
    )
    print(f"[{nome_etapa}] Arquivos ZIP descompactados com sucesso: {qtd_extraida}")

    # 7. Salva o estado final do manifesto (com status de download,
    #    tipo identificado e extração já atualizados)
    salvar_json(caminho_manifesto, manifesto)
    print(f"[{nome_etapa}] Manifesto final salvo em '{caminho_manifesto}'.")

    return {
        "baixados": qtd_baixada,
        "identificados": qtd_identificada,
        "extraidos": qtd_extraida,
    }


if __name__ == "__main__":

    # --- Caminhos: CONTRATAÇÕES -------------------------------------------
    ARQUIVO_CONTRATACOES = "data/normalized/contratacoes_rj.json"
    CAMINHO_MANIFESTO_CONTRATACOES = "data/normalized/contratacoes_documentos.json"
    CAMINHO_BASE_CONTRATACOES = "data/documents/original/contratacoes"
    CAMINHO_EXTRAIR_CONTRATACOES = "data/documents/extracted/contratacoes"

    # --- Caminhos: CONTRATOS -------------------------------------------
    ARQUIVO_CONTRATOS = "data/normalized/contratos_rj.json"
    CAMINHO_MANIFESTO_CONTRATOS = "data/normalized/contratos_documentos.json"
    CAMINHO_BASE_CONTRATOS = "data/documents/original/contrato"
    CAMINHO_EXTRAIR_CONTRATOS = "data/documents/extracted/contratatos"

   # -----------------------------------------------------------------
    # PARTE 1 — COLETA DE CONTRATAÇÕES (DESATIVADA)
    # -----------------------------------------------------------------
    # Já existe uma base de contratações coletada e estruturada.
    # Não rodar de novo agora (evita requisições demoradas e desnecessárias).
    # Quando precisar atualizar a base, é só descomentar este bloco
    # (lembrando de definir data_inicial e data_final antes).
    #
    # resultado = coletar_contratacoes(
    #     uf="RJ",
    #     data_inicial=data_inicial,
    #     data_final=data_final,
    #     tamanho_pagina=50,
    # )
    # quantidade_nova = adicionar_contratacoes_novas(
    #     resultado.contratacoes
    # )
    # salvar_paginas_com_erro(
    #     data_inicial=data_inicial,
    #     data_final=data_final,
    #     paginas=resultado.paginas_com_erro,
    #     caminho=CAMINHO_MANIFESTO_CONTRATACOES,
    # )

    # Roda o fluxo para Contratações
    resultado_contratacoes = processar_documentos(
        nome_etapa="Contratações",
        arquivo_entrada=ARQUIVO_CONTRATACOES,
        caminho_manifesto=CAMINHO_MANIFESTO_CONTRATACOES,
        pasta_base=CAMINHO_BASE_CONTRATACOES,
        pasta_extrair=CAMINHO_EXTRAIR_CONTRATACOES,
        funcao_gerar_manifesto=salvar_lista_documentos_contratacao,
        limite_contratos=5,
        limite_documentos_por_contrato=1,
    )

    # -----------------------------------------------------------------
    # PARTE 1 — COLETA DE CONTRATOS (DESATIVADA)
    # -----------------------------------------------------------------
    # Mesma ideia da coleta de contratações, mas com as funções/parâmetros
    # equivalentes para contratos. Ajuste os nomes se forem diferentes
    # no seu projeto.
    #
    # resultado = coletar_contratos(
    #     data_inicial=data_inicial,
    #     data_final=data_final,
    #     tamanho_pagina=50,
    # )
    # quantidade_nova = adicionar_contratos_novos(resultado.contratos)
    # salvar_paginas_com_erro(
    #     data_inicial=data_inicial,
    #     data_final=data_final,
    #     paginas=resultado.paginas_com_erro,
    #     caminho=CAMINHO_MANIFESTO_CONTRATOS,
    # )

    # Roda o mesmo fluxo para Contratos (mesma lógica, pastas diferentes)
    resultado_contratos = processar_documentos(
        nome_etapa="Contratos",
        arquivo_entrada=ARQUIVO_CONTRATOS,
        caminho_manifesto=CAMINHO_MANIFESTO_CONTRATOS,
        pasta_base=CAMINHO_BASE_CONTRATOS,
        pasta_extrair=CAMINHO_EXTRAIR_CONTRATOS,
        funcao_gerar_manifesto=salvar_lista_de_documentos_contratos,
        limite_contratos=5,
        limite_documentos_por_contrato=1,
    )

    print("\n=== Resumo final ===")
    print("Contratações:", resultado_contratacoes)
    print("Contratos:", resultado_contratos)
