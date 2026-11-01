from __future__ import annotations

import pytest

from eval.review_grounded_answers import extract_citations, review_citations


def test_extract_citations_preserves_order_and_removes_duplicates() -> None:
    assert extract_citations("Regra [2], fundamento [1] e reforço [2].") == (2, 1)


def test_review_accepts_cited_substantive_blocks() -> None:
    answer = (
        "A primeira regra substantiva está demonstrada pela fonte normativa [1].\n\n"
        "- A segunda condição também possui evidência documental suficiente [2]."
    )

    review = review_citations(answer, source_count=2)

    assert review.structurally_valid is True
    assert review.used_citations == (1, 2)
    assert review.invalid_citations == ()
    assert review.unused_sources == ()
    assert review.uncited_substantive_blocks == ()


def test_review_reports_invalid_unused_and_uncited_blocks_without_content() -> None:
    answer = (
        "Afirmação longa o bastante para exigir evidência, mas sem marcador algum.\n\n"
        "Outra afirmação substantiva usa uma fonte que não existe [4]."
    )

    payload = review_citations(answer, source_count=2).as_dict()

    assert payload == {
        "source_count": 2,
        "block_count": 2,
        "used_citations": (4,),
        "invalid_citations": (4,),
        "unused_sources": (1, 2),
        "uncited_substantive_blocks": (1,),
        "structurally_valid": False,
    }
    assert "Afirmação" not in repr(payload)


def test_short_heading_does_not_require_citation() -> None:
    review = review_citations(
        "## Resumo\n\nA conclusão suficientemente detalhada usa a fonte correta [1].",
        source_count=1,
    )

    assert review.structurally_valid is True
    assert review.uncited_substantive_blocks == ()


@pytest.mark.parametrize("source_count", [-1, -10])
def test_review_rejects_negative_source_count(source_count: int) -> None:
    with pytest.raises(ValueError, match="source_count"):
        review_citations("Resposta [1].", source_count=source_count)


def test_review_rejects_non_positive_minimum() -> None:
    with pytest.raises(ValueError, match="minimum_characters"):
        review_citations("Resposta [1].", source_count=1, minimum_characters=0)
