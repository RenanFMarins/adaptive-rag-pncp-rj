from __future__ import annotations

import argparse
import json

from .ingest import RawRepository, ingest_records
from .ingestion.pncp_client import PNCPClient
from .ingestion.pncp_collector import PCACollector, PNCPCollector
from .schema import Manifest

Collector = PNCPCollector


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
        checkpoint = repository.get_checkpoint(
            source.id, source.resource_type
        )
        start_page = checkpoint + 1 if checkpoint else 1
        collector_class = (
            PCACollector if source.resource_type == "pca" else PNCPCollector
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
