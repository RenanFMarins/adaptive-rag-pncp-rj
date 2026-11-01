from __future__ import annotations

from types import SimpleNamespace

from src.query.schemas import KnowledgeBase, QueryFilters
from src.retrieve import (
    _consulta_juridica_geral,
    _reordenar_por_autoridade_normativa,
)


def _chunk(doc_type: str):
    return SimpleNamespace(document=SimpleNamespace(doc_type=doc_type))


def test_general_legal_question_requires_explicit_normative_base() -> None:
    question = "Quais regras a lei prevê para esta licitação?"

    assert _consulta_juridica_geral(
        question, None, [KnowledgeBase.NORMATIVA]
    ) is True
    assert _consulta_juridica_geral(question, None, None) is False
    assert _consulta_juridica_geral(
        question,
        None,
        [KnowledgeBase.NORMATIVA, KnowledgeBase.ESTRUTURADA],
    ) is False


def test_specific_edital_or_filter_does_not_enable_authority_rerank() -> None:
    assert _consulta_juridica_geral(
        "Resuma as cláusulas deste edital",
        None,
        [KnowledgeBase.NORMATIVA],
    ) is False
    assert _consulta_juridica_geral(
        "Quais regras se aplicam?",
        QueryFilters(tipo_documento="Edital"),
        [KnowledgeBase.NORMATIVA],
    ) is False


def test_authority_rerank_preserves_rrf_score_and_prioritizes_source_type() -> None:
    candidates = [("edital", 0.04), ("decreto", 0.02), ("lei", 0.01)]
    chunks = {
        "edital": _chunk("edital"),
        "decreto": _chunk("decreto"),
        "lei": _chunk("lei"),
    }

    ranked = _reordenar_por_autoridade_normativa(candidates, chunks)

    assert ranked == [("decreto", 0.02), ("lei", 0.01), ("edital", 0.04)]


def test_authority_rerank_brings_first_part_of_relevant_section() -> None:
    candidates = [
        ("norma:art75:p4", 0.03),
        ("norma:outro:p1", 0.025),
        ("norma:art75:p1", 0.01),
    ]
    chunks = {chunk_id: _chunk("lei") for chunk_id, _score in candidates}

    ranked = _reordenar_por_autoridade_normativa(candidates, chunks)

    assert ranked[:2] == [
        ("norma:art75:p1", 0.01),
        ("norma:art75:p4", 0.03),
    ]
