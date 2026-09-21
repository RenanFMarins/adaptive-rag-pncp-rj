from __future__ import annotations

import json
import sqlite3
import uuid
from typing import Any, Mapping

from src.obs import utc_now
from src.schema import CollectedRecord


class RawRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def find_latest(self, source: str, resource_type: str, external_id: str):
        return self.connection.execute(
            "SELECT * FROM raw_asset WHERE source = ? AND resource_type = ? "
            "AND external_id = ? ORDER BY rowid DESC LIMIT 1",
            (source, resource_type, external_id),
        ).fetchone()

    def latest(self, source: str, resource_type: str, external_id: str):
        """Alias de compatibilidade para find_latest."""
        return self.find_latest(source, resource_type, external_id)

    def latest_hash(
        self, source: str, resource_type: str, external_id: str
    ) -> str | None:
        row = self.find_latest(source, resource_type, external_id)
        return row["payload_hash"] if row else None

    def contains_version(
        self,
        source: str,
        resource_type: str,
        external_id: str,
        digest: str,
    ) -> bool:
    
        row = self.connection.execute(
            "SELECT 1 FROM raw_asset WHERE source = ? "
            "AND resource_type = ? AND external_id = ? "
            "AND payload_hash = ? LIMIT 1",
            (source, resource_type, external_id, digest),
        ).fetchone()
        return row is not None

    def list_latest(self, source: str, resource_type: str):
        return self.connection.execute(
            "SELECT asset.* FROM raw_asset AS asset "
            "JOIN ("
            "  SELECT external_id, MAX(rowid) AS latest_rowid "
            "  FROM raw_asset WHERE source = ? AND resource_type = ? "
            "  GROUP BY external_id"
            ") AS latest ON latest.latest_rowid = asset.rowid "
            "ORDER BY asset.rowid",
            (source, resource_type),
        ).fetchall()

    def insert_raw(
        self,
        run_id: str,
        record: CollectedRecord,
        external_id: str,
        digest: str,
        resource_type: str = "records",
        base_id: str = "pncp",
        natureza: str = "estruturada",
        query_params: Mapping[str, Any] | None = None,
        corpus_version: str = "v1",
        sensitivity: str = "public",
        source_published_at: str | None = None,
        source_updated_at: str | None = None,
    ) -> str:
        previous = self.find_latest(
            record.source_id, resource_type, external_id
        )
        asset_id = str(uuid.uuid4())
        payload_json = json.dumps(
            record.payload, ensure_ascii=False, separators=(",", ":")
        )
        self.connection.execute(
            "INSERT INTO raw_asset "
            "(id, source, base_id, natureza, resource_type, endpoint, "
            "external_id, query_params, payload, payload_hash, "
            "source_published_at, source_updated_at, fetched_at, "
            "corpus_version, sensitivity, ingestion_run_id, "
            "previous_version_id, processing_status, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                asset_id,
                record.source_id,
                base_id,
                natureza,
                resource_type,
                record.source_url,
                external_id,
                json.dumps(query_params or {}, ensure_ascii=False),
                payload_json,
                digest,
                source_published_at,
                source_updated_at,
                utc_now(),
                corpus_version,
                sensitivity,
                run_id,
                previous["id"] if previous else None,
                "RAW",
                utc_now(),
            ),
        )
        self.connection.commit()
        return asset_id

    def save_asset(
        self,
        run_id: str,
        record: CollectedRecord,
        external_id: str,
        digest: str,
        **metadata: Any,
    ) -> str:
        """Alias de compatibilidade para a inserção append-only."""
        return self.insert_raw(
            run_id, record, external_id, digest, **metadata
        )
