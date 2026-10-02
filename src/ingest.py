from __future__ import annotations

import json
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
from .schema import CollectionCheckpoint, CollectedRecord, IngestionResult


class RawRepository:
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
        window_start: str | None = None,
        window_end: str | None = None,
    ) -> str:
        return self.runs.start(
            source_id,
            resource_type,
            window_start=window_start,
            window_end=window_end,
        )

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

    def save_progress(
        self,
        source_id: str,
        resource_type: str,
        run_id: str,
        last_page: int,
    ) -> None:
        self.checkpoints.update_progress(
            source_id, resource_type, run_id, last_page
        )

    def fail_progress(
        self,
        source_id: str,
        resource_type: str,
        run_id: str,
    ) -> None:
        self.checkpoints.mark_failed(source_id, resource_type, run_id)

    def latest_payloads(
        self, source_id: str, resource_type: str
    ) -> list[dict]:
        return [
            json.loads(row["payload"])
            for row in self.assets.list_latest(source_id, resource_type)
        ]

    def latest_assets(
        self, source_id: str, resource_type: str
    ) -> list[dict]:
        return self.assets.list_latest_with_payload(source_id, resource_type)

    def latest_targets(
        self,
        source_id: str,
        resource_type: str,
        field_paths: dict[str, str],
    ):
        return self.assets.iter_latest_target_values(
            source_id, resource_type, field_paths
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
        key = record.external_id or asset_key(record.payload, key_fields)
        digest = payload_hash(record.payload)
        latest_digest = self.assets.latest_hash(
            record.source_id, resource_type, key
        )
        if self.assets.contains_version(
            record.source_id, resource_type, key, digest
        ):
            status = "UNCHANGED"
        else:
            status = detect_change(latest_digest, digest)
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
    records: Iterable[CollectedRecord | CollectionCheckpoint],
    mode: str = "update",
    logger: JsonlLogger | None = None,
    resource_type: str = "records",
    base_id: str = "pncp",
    natureza: str = "estruturada",
    query_params: dict | None = None,
    corpus_version: str = "v1",
    sensitivity: str = "public",
    initial_checkpoint: int = 0,
    window_start: str | None = None,
    window_end: str | None = None,
) -> IngestionResult:
    run_id = repository.start_run(
        source_id,
        resource_type,
        window_start=window_start,
        window_end=window_end,
    )
    counts = {
        "records_seen": 0,
        "NEW": 0,
        "UPDATED": 0,
        "UNCHANGED": 0,
        "FAILED": 0,
    }
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
            if isinstance(record, CollectionCheckpoint):
                repository.save_progress(
                    source_id, resource_type, run_id, page
                )
                last_page = page
                continue
            status = repository.persist_record(
                run_id,
                record,
                key_fields,
                resource_type,
                base_id,
                natureza,
                (
                    dict(record.query_params)
                    if record.query_params is not None
                    else query_params
                ),
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
        last_page = max(processed_pages, default=initial_checkpoint)
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
    except BaseException as error:
        last_page = max(processed_pages, default=initial_checkpoint)
        error_message = str(error) or type(error).__name__
        counts["FAILED"] += 1
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
            failed=counts["FAILED"],
            error=error_message,
        )
        repository.runs.fail_run(
            run_id,
            counts,
            pages_processed=len(processed_pages),
            error=error_message,
        )
        repository.fail_progress(source_id, resource_type, run_id)
        raise


__all__ = [
    "RawRepository",
    "asset_key",
    "detect_change",
    "ingest_records",
    "payload_hash",
]
