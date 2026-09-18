from __future__ import annotations

from typing import Iterable

from app.core.database import initialize_database
from app.core.database.repositories import (
    CheckpointRepository,
    RawRepository as RawAssetRepository,
    RunRepository,
)
from .ingestion.change_detector import asset_key, detect_change
from .ingestion.hashing import payload_hash
from .obs import JsonlLogger
from .schema import CollectedRecord, IngestionResult


class RawRepository:
    """Facade de compatibilidade para a persistencia RAW."""

    def __init__(self, database_url: str | None = None) -> None:
        self.connection = initialize_database(database_url)
        self.assets = RawAssetRepository(self.connection)
        self.runs = RunRepository(self.connection)
        self.checkpoints = CheckpointRepository(self.connection)

    def close(self) -> None:
        self.connection.close()

    def start_run(
        self,
        source_id: str,
        resource_type: str = "records",
    ) -> str:
        return self.runs.start(source_id, resource_type)

    def get_checkpoint(
        self,
        source_id: str,
        resource_type: str = "records",
    ) -> int:
        row = self.checkpoints.get_checkpoint(source_id, resource_type)
        return int(row["last_page"]) if row else 0

    def save_checkpoint(
        self,
        source_id: str,
        resource_type: str,
        run_id: str,
        last_page: int,
    ) -> None:
        self.checkpoints.update_checkpoint(
            source_id, resource_type, run_id, last_page
        )

    def persist_record(
        self,
        run_id: str,
        record: CollectedRecord,
        key_fields: tuple[str, ...],
        resource_type: str = "records",
        base_id: str = "pncp",
        natureza: str = "estruturada",
        query_params: dict | None = None,
        corpus_version: str = "v1",
        sensitivity: str = "public",
    ) -> str:
        key = asset_key(record.payload, key_fields)
        digest = payload_hash(record.payload)
        status = detect_change(
            self.assets.latest_hash(record.source_id, resource_type, key),
            digest,
        )
        if status != "UNCHANGED":
            self.assets.insert_raw(
                run_id,
                record,
                key,
                digest,
                resource_type=resource_type,
                base_id=base_id,
                natureza=natureza,
                query_params=query_params,
                corpus_version=corpus_version,
                sensitivity=sensitivity,
            )
        return status

    def finish_run(
        self,
        run_id: str,
        counts: dict[str, int],
        pages_processed: int = 0,
        status: str = "SUCCESS",
        error: str | None = None,
    ) -> None:
        self.runs.finish(run_id, counts, pages_processed, status, error)


def ingest_records(
    repository: RawRepository,
    source_id: str,
    key_fields: tuple[str, ...],
    records: Iterable[CollectedRecord],
    mode: str = "update",
    logger: JsonlLogger | None = None,
    resource_type: str = "records",
    base_id: str = "pncp",
    natureza: str = "estruturada",
    query_params: dict | None = None,
    corpus_version: str = "v1",
    sensitivity: str = "public",
) -> IngestionResult:
    run_id = repository.start_run(source_id, resource_type)
    counts = {"records_seen": 0, "NEW": 0, "UPDATED": 0, "UNCHANGED": 0}
    logger = logger or JsonlLogger()
    last_page = 0
    processed_pages: set[int] = set()
    try:
        for record in records:
            page = int(record.cursor)
            is_new_page = page not in processed_pages
            processed_pages.add(page)
            if is_new_page:
                logger.event(
                    "pncp_fetch",
                    stage="pncp_fetch",
                    run_id=run_id,
                    resource_type=resource_type,
                    page=page,
                    status="SUCCESS",
                )
            status = repository.persist_record(
                run_id,
                record,
                key_fields,
                resource_type,
                base_id,
                natureza,
                query_params,
                corpus_version,
                sensitivity,
            )
            counts["records_seen"] += 1
            counts[status] += 1
            logger.event(
                "change_detection",
                stage="change_detection",
                run_id=run_id,
                resource_type=resource_type,
                page=page,
                status=status,
                records_received=counts["records_seen"],
                new=counts["NEW"],
                updated=counts["UPDATED"],
                unchanged=counts["UNCHANGED"],
                failed=counts.get("FAILED", 0),
            )
            if status != "UNCHANGED":
                logger.event(
                    "raw_persistence",
                    stage="raw_persistence",
                    run_id=run_id,
                    resource_type=resource_type,
                    page=page,
                    status=status,
                )
        last_page = max(processed_pages, default=0)
        repository.finish_run(run_id, counts, len(processed_pages))
        repository.save_checkpoint(
            source_id, resource_type, run_id, last_page
        )
        logger.event(
            "checkpoint_update",
            stage="checkpoint_update",
            run_id=run_id,
            resource_type=resource_type,
            page=last_page,
            status="SUCCESS",
            records_received=counts["records_seen"],
            new=counts["NEW"],
            updated=counts["UPDATED"],
            unchanged=counts["UNCHANGED"],
            failed=counts.get("FAILED", 0),
        )
        return IngestionResult(
            run_id,
            source_id,
            "SUCCEEDED",
            counts["records_seen"],
            counts["NEW"],
            counts["UPDATED"],
            counts["UNCHANGED"],
        )
    except Exception as error:
        last_page = max(processed_pages, default=0)
        logger.event(
            "ingestion_failure",
            stage="pncp_fetch",
            run_id=run_id,
            resource_type=resource_type,
            page=last_page,
            status="FAILED",
            records_received=counts["records_seen"],
            new=counts["NEW"],
            updated=counts["UPDATED"],
            unchanged=counts["UNCHANGED"],
            failed=1,
            error=str(error),
        )
        repository.runs.fail_run(
            run_id, counts, pages_processed=last_page, error=str(error)
        )
        raise


__all__ = [
    "RawRepository",
    "asset_key",
    "detect_change",
    "ingest_records",
    "payload_hash",
]
