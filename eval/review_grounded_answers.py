"""Valida a estrutura das citações de respostas documentais.

Este módulo não tenta substituir a revisão factual humana. Ele verifica
somente propriedades objetivas: marcadores ``[n]``, limites da lista de fontes,
blocos substantivos sem citação e fontes recuperadas que não foram usadas.

O texto analisado permanece em memória. O relatório retornado contém apenas
números de blocos e citações, sem copiar perguntas ou respostas completas.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

_CITATION_RE = re.compile(r"(?<!\w)\[(\d+)\](?!\w)")
_LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*]\s+|\d+[.)]\s+)")


@dataclass(frozen=True)
class CitationReview:
    """Resultado estrutural, sem reproduzir o conteúdo avaliado."""

    source_count: int
    block_count: int
    used_citations: tuple[int, ...]
    invalid_citations: tuple[int, ...]
    unused_sources: tuple[int, ...]
    uncited_substantive_blocks: tuple[int, ...]

    @property
    def structurally_valid(self) -> bool:
        return bool(self.used_citations) and not (
            self.invalid_citations or self.uncited_substantive_blocks
        )

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["structurally_valid"] = self.structurally_valid
        return payload


def extract_citations(text: str) -> tuple[int, ...]:
    """Extrai marcadores numéricos na ordem, removendo repetições."""

    return tuple(dict.fromkeys(int(value) for value in _CITATION_RE.findall(text)))


def _answer_blocks(text: str) -> list[str]:
    """Separa parágrafos e itens de lista sem guardar o resultado no relatório."""

    blocks: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(" ".join(paragraph).strip())
            paragraph.clear()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            continue
        if _LIST_PREFIX_RE.match(line):
            flush_paragraph()
            blocks.append(line)
        else:
            paragraph.append(line)
    flush_paragraph()
    return [block for block in blocks if block]


def _is_substantive(block: str, minimum_characters: int) -> bool:
    without_citations = _CITATION_RE.sub("", block)
    without_prefix = _LIST_PREFIX_RE.sub("", without_citations).strip()
    if len(without_prefix) < minimum_characters:
        return False
    # Títulos Markdown não são afirmações factuais isoladas.
    return not without_prefix.startswith("#")


def review_citations(
    answer: str,
    source_count: int,
    *,
    minimum_characters: int = 40,
) -> CitationReview:
    """Executa validação estrutural; correção factual continua sendo humana."""

    if source_count < 0:
        raise ValueError("source_count não pode ser negativo")
    if minimum_characters <= 0:
        raise ValueError("minimum_characters deve ser positivo")

    blocks = _answer_blocks(answer)
    used = extract_citations(answer)
    invalid = tuple(value for value in used if value < 1 or value > source_count)
    unused = tuple(value for value in range(1, source_count + 1) if value not in used)
    uncited = tuple(
        index
        for index, block in enumerate(blocks, start=1)
        if _is_substantive(block, minimum_characters) and not extract_citations(block)
    )
    return CitationReview(
        source_count=source_count,
        block_count=len(blocks),
        used_citations=used,
        invalid_citations=invalid,
        unused_sources=unused,
        uncited_substantive_blocks=uncited,
    )


__all__ = ["CitationReview", "extract_citations", "review_citations"]
