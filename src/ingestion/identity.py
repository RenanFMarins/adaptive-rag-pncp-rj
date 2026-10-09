from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class CanonicalIdentity:
    """Identidade PNCP independente do coletor que observou a entidade."""

    base_id: str
    resource_type: str
    external_id: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("base_id", self.base_id),
            ("resource_type", self.resource_type),
            ("external_id", self.external_id),
        ):
            if not str(value).strip():
                raise ValueError(
                    f"Identidade canônica requer {field_name} não vazio"
                )

    @property
    def values(self) -> tuple[str, str, str]:
        return self.base_id, self.resource_type, self.external_id


_UPDATED_FIELDS: dict[str, tuple[str, ...]] = {
    "pca": ("dataAtualizacaoGlobalPCA", "dataAtualizacao"),
    "contratacao": ("dataAtualizacaoGlobal", "dataAtualizacao"),
    "contratacao_item": ("dataAtualizacao",),
    "resultado_item": ("dataAtualizacao",),
    "contrato": ("dataAtualizacaoGlobal", "dataAtualizacao"),
    "empenho": ("dataAtualizacao",),
    "ata_registro_preco": ("dataAtualizacaoGlobal", "dataAtualizacao"),
}

_PUBLISHED_FIELDS: dict[str, tuple[str, ...]] = {
    "pca": ("dataPublicacaoPNCP", "dataPublicacaoPncp"),
    "contratacao": ("dataPublicacaoPncp", "dataInclusao"),
    "contratacao_item": ("dataInclusao",),
    "resultado_item": ("dataResultado", "dataInclusao"),
    "contrato": ("dataPublicacaoPncp", "dataInclusao"),
    "empenho": ("dataInclusao",),
    "ata_registro_preco": ("dataPublicacaoPncp", "dataInclusao"),
}


def _first_text(payload: Mapping[str, Any], fields: tuple[str, ...]) -> str | None:
    for field in fields:
        value = payload.get(field)
        if value not in (None, ""):
            return str(value)
    return None


def source_timestamps(
    payload: Mapping[str, Any], resource_type: str
) -> tuple[str | None, str | None]:
    """Extrai publicação e atualização sem alterar o payload RAW."""

    published_fields = _PUBLISHED_FIELDS.get(
        resource_type,
        ("dataPublicacaoPncp", "dataPublicacaoPNCP", "dataInclusao"),
    )
    updated_fields = _UPDATED_FIELDS.get(
        resource_type,
        ("dataAtualizacaoGlobal", "dataAtualizacao"),
    )
    return (
        _first_text(payload, published_fields),
        _first_text(payload, updated_fields),
    )


def normalized_timestamp(value: object) -> str | None:
    """Normaliza ISO-8601 para comparação e igualdade entre observações."""

    if value in (None, ""):
        return None
    text = str(value).strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed.isoformat(timespec="microseconds")

