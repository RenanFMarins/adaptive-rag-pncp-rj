from __future__ import annotations

import json
import sqlite3
import uuid
from typing import Any, Mapping

from src.ingestion.identity import (
    CanonicalIdentity,
    normalized_timestamp,
    source_timestamps,
)
from src.obs import utc_now
from src.schema import CollectedRecord, value_at_path


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

    def _canonical_rows(self, identity: CanonicalIdentity):
        return self.connection.execute(
            "SELECT rowid AS _rowid, * FROM raw_asset "
            "WHERE base_id = ? AND resource_type = ? AND external_id = ?",
            identity.values,
        ).fetchall()

    @staticmethod
    def _row_source_updated_at(row: sqlite3.Row) -> str | None:
        stored = row["source_updated_at"]
        if stored not in (None, ""):
            return str(stored)
        payload = json.loads(row["payload"])
        _, updated_at = source_timestamps(payload, row["resource_type"])
        return updated_at

    @classmethod
    def _current_order_key(cls, row: sqlite3.Row):
        source_updated_at = normalized_timestamp(
            cls._row_source_updated_at(row)
        )
        if source_updated_at is not None:
            return (1, source_updated_at, row["fetched_at"], row["_rowid"])
        return (0, row["fetched_at"], row["fetched_at"], row["_rowid"])

    def find_current(self, identity: CanonicalIdentity):
        """Retorna o estado atual pela identidade, não pelo job de coleta."""

        rows = self._canonical_rows(identity)
        return max(rows, key=self._current_order_key) if rows else None

    def contains_observation(
        self,
        identity: CanonicalIdentity,
        digest: str,
        source_updated_at: str | None,
    ) -> bool:
        """Detecta replay da mesma versão sem bloquear reversões posteriores."""

        expected_timestamp = normalized_timestamp(source_updated_at)
        if expected_timestamp is None:
            return self.connection.execute(
                "SELECT 1 FROM raw_asset "
                "WHERE base_id = ? AND resource_type = ? AND external_id = ? "
                "AND payload_hash = ? LIMIT 1",
                (*identity.values, digest),
            ).fetchone() is not None
        rows = self.connection.execute(
            "SELECT rowid AS _rowid, * FROM raw_asset "
            "WHERE base_id = ? AND resource_type = ? AND external_id = ? "
            "AND payload_hash = ?",
            (*identity.values, digest),
        ).fetchall()
        return any(
            normalized_timestamp(self._row_source_updated_at(row))
            == expected_timestamp
            for row in rows
        )

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
        return list(self._iter_current_source_rows(source, resource_type))

    def _iter_current_source_rows(self, source: str, resource_type: str):
        """Seleciona o estado atual sem confundir ordem de chegada com versão."""

        cursor = self.connection.execute(
            "SELECT rowid AS _rowid, * FROM raw_asset "
            "WHERE source = ? AND resource_type = ? "
            "ORDER BY external_id, rowid",
            (source, resource_type),
        )
        current_external_id = None
        current_row = None
        for row in cursor:
            if row["external_id"] != current_external_id:
                if current_row is not None:
                    yield current_row
                current_external_id = row["external_id"]
                current_row = row
            elif self._current_order_key(row) > self._current_order_key(
                current_row
            ):
                current_row = row
        if current_row is not None:
            yield current_row

    def list_latest_with_payload(self, source: str, resource_type: str):
        """Retorna metadados e JSON dos ativos mais recentes para novos alvos."""
        rows = self.list_latest(source, resource_type)
        return [
            {
                "external_id": row["external_id"],
                "payload": json.loads(row["payload"]),
            }
            for row in rows
        ]

    def iter_latest_target_values(
        self,
        source: str,
        resource_type: str,
        field_paths: Mapping[str, str],
    ):
        """Extrai alvos do estado atual, inclusive com chegada fora de ordem."""

        for row in self._iter_current_source_rows(source, resource_type):
            target = {}
            external_id = row["external_id"]
            payload = None
            for name, path in field_paths.items():
                if path == "@external_id":
                    target[name] = external_id
                elif path == "@parent_external_id":
                    parent, separator, _ = external_id.rpartition("|")
                    target[name] = parent if separator else None
                else:
                    if payload is None:
                        payload = json.loads(row["payload"])
                    target[name] = value_at_path(payload, path)
            yield target

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
        identity: CanonicalIdentity | None = None,
        previous_version_id: str | None = None,
    ) -> str:
        identity = identity or CanonicalIdentity(
            base_id, resource_type, external_id
        )
        if previous_version_id is None:
            previous = self.find_current(identity)
            previous_version_id = previous["id"] if previous else None
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
                previous_version_id,
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
