"""Conversão validada de perguntas em planos de execução do RAG."""

from __future__ import annotations

import json
from collections.abc import Callable

from pydantic import ValidationError

from llm_ecoa import gerar_resposta
from src.query.prompts import montar_prompt_analise
from src.query.schemas import QueryAnalysis, QueryRoute


AnalyzerLlmFn = Callable[[str], str]


class QueryAnalysisError(ValueError):
    """Indica que a resposta da LLM não pode ser usada como plano válido."""


def _extrair_json(resposta: str) -> str:
    """Aceita JSON puro e a cerca Markdown que alguns modelos ainda produzem."""

    conteudo = resposta.strip()
    if not conteudo:
        raise QueryAnalysisError("A LLM retornou uma análise vazia.")
    if not conteudo.startswith("```"):
        return conteudo

    linhas = conteudo.splitlines()
    if len(linhas) < 3 or not linhas[-1].strip().startswith("```"):
        raise QueryAnalysisError(
            "A LLM retornou uma cerca Markdown incompleta.")
    return "\n".join(linhas[1:-1]).strip()


def analisar_pergunta(
    pergunta: str,
    llm_fn: AnalyzerLlmFn = gerar_resposta,
    *,
    rota_obrigatoria: QueryRoute | None = None,
) -> QueryAnalysis:
    """Gera e valida um plano estruturado sem executar qualquer ferramenta."""

    pergunta_limpa = pergunta.strip()
    if not pergunta_limpa:
        raise QueryAnalysisError("A pergunta não pode estar vazia.")

    resposta = llm_fn(
        montar_prompt_analise(
            pergunta_limpa,
            rota_obrigatoria=(
                rota_obrigatoria.value if rota_obrigatoria is not None else None
            ),
        )
    )
    try:
        plano_bruto = json.loads(_extrair_json(resposta))
    except json.JSONDecodeError as exc:
        raise QueryAnalysisError("A LLM não retornou um JSON válido.") from exc

    if not isinstance(plano_bruto, dict):
        raise QueryAnalysisError("A análise deve ser um objeto JSON.")

    try:
        analysis = QueryAnalysis.model_validate(plano_bruto)
    except ValidationError as exc:
        raise QueryAnalysisError("A LLM retornou um plano inválido.") from exc

    if rota_obrigatoria is not None and analysis.route is not rota_obrigatoria:
        raise QueryAnalysisError(
            "A LLM retornou a rota "
            f"'{analysis.route.value}', mas este endpoint exige "
            f"'{rota_obrigatoria.value}'."
        )
    return analysis


def analisar_pergunta_estruturada(
    pergunta: str,
    llm_fn: AnalyzerLlmFn = gerar_resposta,
) -> QueryAnalysis:
    """Analisa uma pergunta para o endpoint que aceita somente SQL seguro."""

    return analisar_pergunta(
        pergunta,
        llm_fn=llm_fn,
        rota_obrigatoria=QueryRoute.STRUCTURED,
    )
