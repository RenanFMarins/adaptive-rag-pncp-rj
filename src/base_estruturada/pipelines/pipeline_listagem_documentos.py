"""Lista documentos do PNCP e salva manifestos mensais.

Este pipeline não baixa, identifica nem extrai arquivos. Ele somente lê os
JSONs mensais já coletados e consulta o endpoint ``/arquivos`` de cada item.
"""

from pathlib import Path
from typing import Any, Callable

from src.base_estruturada.pipelines.pipeline_documentos import (
    PeriodoColeta,
    caminhos_do_periodo,
)
from src.base_estruturada.pncp.repository import (
    carregar_checkpoint_documentos,
    carregar_json,
    salvar_lista_de_documentos_contratos,
    salvar_lista_documentos_contratacao,
)


def listar_documentos_do_periodo(
    nome_etapa: str,
    arquivo_entrada: Path,
    arquivo_manifesto: Path,
    arquivo_checkpoint: Path,
    funcao_listagem: Callable[..., list[dict[str, Any]]],
    limite_novos_itens: int,
) -> None:
    """Lista documentos para os próximos itens ainda ausentes do manifesto."""

    itens = carregar_json(arquivo_entrada, padrao=[])
    if not isinstance(itens, list):
        raise RuntimeError(
            f"O arquivo de entrada deve conter uma lista: {arquivo_entrada}"
        )

    antes = carregar_json(arquivo_manifesto, padrao=[])
    total_antes = len(antes) if isinstance(antes, list) else 0

    print(f"\n=== {nome_etapa}: listagem de documentos ===")
    print(f"Itens disponíveis: {len(itens)} | já no manifesto: {total_antes}")

    manifesto = funcao_listagem(
        itens,
        arquivo_manifesto,
        caminho_checkpoint=arquivo_checkpoint,
        limite=limite_novos_itens,
    )

    novos = len(manifesto) - total_antes
    checkpoint = carregar_checkpoint_documentos(arquivo_checkpoint)
    estados = checkpoint.get("entidades") or {}
    concluidos = sum(
        1
        for estado in estados.values()
        if isinstance(estado, dict)
        and estado.get("statusListagem") == "concluida"
    )
    erros = sum(
        1
        for estado in estados.values()
        if isinstance(estado, dict)
        and estado.get("statusListagem") == "erro"
    )

    print(
        f"Listagem original: {arquivo_manifesto}\n"
        f"Checkpoint: {arquivo_checkpoint} | novos={novos} | "
        f"concluídos={concluidos} | erros={erros}"
    )


if __name__ == "__main__":
    # Use o mesmo período usado no pipeline de coleta.
    PERIODO = PeriodoColeta(ano=2026, mes=8)
    CAMINHOS = caminhos_do_periodo(PERIODO)

    # Número de novas consultas por execução. Ao rodar novamente, o pipeline
    # pula itens que já estão no manifesto e avança para os próximos.
    LIMITE_NOVOS_CONTRATOS = 50
    LIMITE_NOVAS_CONTRATACOES = 50

    EXECUTAR_CONTRATOS = True
    EXECUTAR_CONTRATACOES = True

    if EXECUTAR_CONTRATOS:
        listar_documentos_do_periodo(
            nome_etapa="Contratos",
            arquivo_entrada=CAMINHOS["contratos"],
            arquivo_manifesto=CAMINHOS["manifesto_contratos"],
            arquivo_checkpoint=CAMINHOS["checkpoint_documentos_contratos"],
            funcao_listagem=salvar_lista_de_documentos_contratos,
            limite_novos_itens=LIMITE_NOVOS_CONTRATOS,
        )

    if EXECUTAR_CONTRATACOES:
        listar_documentos_do_periodo(
            nome_etapa="Contratações",
            arquivo_entrada=CAMINHOS["contratacoes"],
            arquivo_manifesto=CAMINHOS["manifesto_contratacoes"],
            arquivo_checkpoint=CAMINHOS[
                "checkpoint_documentos_contratacoes"
            ],
            funcao_listagem=salvar_lista_documentos_contratacao,
            limite_novos_itens=LIMITE_NOVAS_CONTRATACOES,
        )
