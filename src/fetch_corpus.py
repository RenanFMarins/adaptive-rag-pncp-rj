from __future__ import annotations

import argparse
import json
from dataclasses import replace

from .ingest import RawRepository, ingest_records
from .ingestion.pncp_client import PNCPClient
from .ingestion.pncp_collector import (
    ItemResultCollector,
    PCACollector,
    PNCPCollector,
)
from .schema import Manifest, SourceConfig, value_at_path

Collector = PNCPCollector


def resolve_source_targets(
    repository: RawRepository, source: SourceConfig
) -> SourceConfig:
    """Substitui alvos manuais por contratações RAW quando disponíveis."""
    if not source.target_source_id or not source.target_resource_type:
        return source

    payloads = repository.latest_payloads(
        source.target_source_id, source.target_resource_type
    )
    if not payloads:
        return source
    if not source.target_field_paths:
        raise ValueError("Fonte dependente sem target_field_paths")

    targets = []
    seen = set()
    for payload in payloads:
        target = {
            name: value_at_path(payload, path)
            for name, path in source.target_field_paths.items()
        }
        missing = [name for name, value in target.items() if value is None]
        if missing:
            raise ValueError(
                "Contratação RAW sem campos para resultado_item: "
                + ", ".join(missing)
            )
        identity = tuple(target.items())
        if identity not in seen:
            seen.add(identity)
            targets.append(target)
    return replace(source, targets=tuple(targets))


def run(
    manifest_path: str,
    source_id: str,
    mode: str,
    database_url: str | None = None,
) -> None:
    manifest = Manifest.load(manifest_path)
    source = manifest.source(source_id)
    repository = RawRepository(database_url)
    try:
        source = resolve_source_targets(repository, source)
        checkpoint = repository.get_checkpoint(
            source.id, source.resource_type
        )
        collector_classes = {
            "paged": PNCPCollector,
            "pca": PCACollector,
            "pncp_item_results": ItemResultCollector,
        }
        collector_name = source.collector
        if collector_name == "paged" and source.resource_type == "pca":
            collector_name = "pca"
        try:
            collector_class = collector_classes[collector_name]
        except KeyError as error:
            raise ValueError(
                f"Coletor não suportado: {collector_name}"
            ) from error
        start_page = (
            checkpoint + 1
            if mode == "update"
            and checkpoint
            and collector_name != "pncp_item_results"
            else 1
        )
        result = ingest_records(
            repository,
            source.id,
            source.key_fields,
            collector_class(PNCPClient()).collect(
                source, start_page=start_page
            ),
            mode=mode,
            resource_type=source.resource_type,
            base_id=source.base_id,
            natureza=source.natureza,
            query_params=dict(source.params),
            sensitivity=source.sensitivity,
        )
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    finally:
        repository.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Coleta PNCP e persiste a camada RAW"
    )
    parser.add_argument("command", choices=("fetch", "update"))
    parser.add_argument("--manifest", default="corpus_manifest.yaml")
    parser.add_argument("--source", default=None)
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args()
    manifest = Manifest.load(args.manifest)
    if not manifest.sources and not args.source:
        parser.error("O manifesto não possui fontes")
    source_id = args.source or manifest.sources[0].id
    run(args.manifest, source_id, args.command, args.database_url)


if __name__ == "__main__":
    main()
