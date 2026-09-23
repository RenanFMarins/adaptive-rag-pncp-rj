from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.schema import Manifest, SourceConfig


ALLOWED_NATURES = {"normativa", "estruturada", "conversacional", "agregada"}
ALLOWED_COLLECTORS = {
    "paged",
    "pca",
    "pncp_purchase_items",
    "pncp_item_results",
}
ITEM_RESULT_FIELDS = {
    "numeroControlePNCPCompra",
    "numeroItem",
    "sequencialResultado",
}


def validate_source(source: SourceConfig) -> list[str]:
    errors: list[str] = []
    prefix = f"Fonte {source.id!r}"

    if not source.base.startswith(("http://", "https://")):
        errors.append(f"{prefix}: base deve ser uma URL HTTP(S)")
    if not source.endpoint.startswith("/"):
        errors.append(f"{prefix}: endpoint deve começar com '/'")
    if source.natureza not in ALLOWED_NATURES:
        errors.append(
            f"{prefix}: natureza {source.natureza!r} não é uma das "
            f"opções {sorted(ALLOWED_NATURES)}"
        )
    if source.collector not in ALLOWED_COLLECTORS:
        errors.append(f"{prefix}: collector {source.collector!r} não suportado")
    if not source.resource_type:
        errors.append(f"{prefix}: resource_type não pode ser vazio")
    if not source.key_fields:
        errors.append(f"{prefix}: key_fields não pode ser vazio")
    if source.page_size < 1:
        errors.append(f"{prefix}: page_size deve ser maior que zero")
    if source.max_pages is not None and source.max_pages < 1:
        errors.append(f"{prefix}: max_pages deve ser maior que zero")
    if source.max_retries < 0:
        errors.append(f"{prefix}: max_retries não pode ser negativo")
    if source.retry_backoff_seconds < 0:
        errors.append(
            f"{prefix}: retry_backoff_seconds não pode ser negativo"
        )

    if source.collector == "pncp_item_results":
        for placeholder in ("{cnpj}", "{ano}", "{sequencial}", "{numeroItem}"):
            if placeholder not in source.endpoint:
                errors.append(
                    f"{prefix}: endpoint de resultados não possui {placeholder}"
                )
        if not source.targets and not source.target_source_id:
            errors.append(
                f"{prefix}: configure target_source_id para os itens RAW"
            )
        missing_keys = ITEM_RESULT_FIELDS.difference(source.key_fields)
        if missing_keys:
            errors.append(
                f"{prefix}: key_fields sem {', '.join(sorted(missing_keys))}"
            )

    if source.collector == "pncp_purchase_items":
        for placeholder in ("{cnpj}", "{ano}", "{sequencial}"):
            if placeholder not in source.endpoint:
                errors.append(
                    f"{prefix}: endpoint de itens não possui {placeholder}"
                )
        if not source.targets and not source.target_source_id:
            errors.append(
                f"{prefix}: configure targets ou target_source_id para as compras"
            )

    return errors


def validate_manifest(manifest: Manifest) -> list[str]:
    errors: list[str] = []
    source_ids = [source.id for source in manifest.sources]
    duplicates = sorted(
        source_id
        for source_id in set(source_ids)
        if source_ids.count(source_id) > 1
    )
    if not source_ids:
        errors.append("O manifesto não possui fontes")
    if duplicates:
        errors.append("IDs de fonte duplicados: " + ", ".join(duplicates))
    for source in manifest.sources:
        errors.extend(validate_source(source))
    return errors


def source_summary(source: SourceConfig) -> dict[str, object]:
    return {
        "id": source.id,
        "base_id": source.base_id,
        "natureza": source.natureza,
        "resource_type": source.resource_type,
        "collector": source.collector,
        "url": source.url,
        "parameter_names": sorted(source.params),
        "key_fields": list(source.key_fields),
        "page_size": source.page_size,
        "max_pages": source.max_pages,
        "target_count": len(source.targets),
        "target_source_id": source.target_source_id,
    }


def inspect_manifest(path: str | Path) -> dict[str, object]:
    manifest_path = Path(path)
    manifest = Manifest.load(manifest_path)
    errors = validate_manifest(manifest)
    return {
        "manifest": str(manifest_path.resolve()),
        "status": "VALID" if not errors else "INVALID",
        "source_count": len(manifest.sources),
        "errors": errors,
        "sources": [source_summary(source) for source in manifest.sources],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida e resume as fontes do corpus sem chamar a API"
    )
    parser.add_argument("--manifest", default="corpus_manifest.yaml")
    args = parser.parse_args()

    report = inspect_manifest(args.manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "VALID":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
