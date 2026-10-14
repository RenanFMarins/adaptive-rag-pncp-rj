from __future__ import annotations

import json
import sqlite3
import uuid
from typing import Mapping

from src.obs import utc_now


class TargetFailureRepository:
    """Fila persistente para alvos cuja consulta ao PNCP falhou."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def record(
        self,
        source: str,
        resource_type: str,
        run_id: str,
        cursor: int,
        target_key: str,
        target: Mapping,
        source_url: str | None,
        error_message: str,
    ) -> None:
        now = utc_now()
        self.connection.execute(
            "INSERT INTO collection_target_failure "
            "(id, source, resource_type, target_key, cursor, target_payload, "
            "source_url, error_message, attempts, status, first_failed_at, "
            "last_failed_at, resolved_at, last_run_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'PENDING', ?, ?, NULL, ?) "
            "ON CONFLICT(source, resource_type, target_key) DO UPDATE SET "
            "cursor=excluded.cursor, target_payload=excluded.target_payload, "
            "source_url=excluded.source_url, "
            "error_message=excluded.error_message, "
            "attempts=collection_target_failure.attempts + 1, "
            "status='PENDING', last_failed_at=excluded.last_failed_at, "
            "resolved_at=NULL, last_run_id=excluded.last_run_id",
            (
                str(uuid.uuid4()),
                source,
                resource_type,
                target_key,
                cursor,
                json.dumps(target, ensure_ascii=False, separators=(",", ":")),
                source_url,
                error_message,
                now,
                now,
                run_id,
            ),
        )
        self.connection.commit()

    def resolve(
        self,
        source: str,
        resource_type: str,
        target_key: str,
        run_id: str,
    ) -> None:
        now = utc_now()
        self.connection.execute(
            "UPDATE collection_target_failure SET status='RESOLVED', "
            "resolved_at=?, last_run_id=? WHERE source=? AND resource_type=? "
            "AND target_key=? AND status='PENDING'",
            (now, run_id, source, resource_type, target_key),
        )
        self.connection.commit()

    def pending(self, source: str, resource_type: str) -> list[dict]:
        rows = self.connection.execute(
            "SELECT cursor, target_key, target_payload FROM "
            "collection_target_failure WHERE source=? AND resource_type=? "
            "AND status='PENDING' ORDER BY cursor, target_key",
            (source, resource_type),
        ).fetchall()
        pending = []
        for row in rows:
            target = json.loads(row["target_payload"])
            target["_cursor"] = int(row["cursor"])
            target["_target_key"] = row["target_key"]
            pending.append(target)
        return pending

    def pending_count(self, source: str, resource_type: str) -> int:
        return int(
            self.connection.execute(
                "SELECT COUNT(*) FROM collection_target_failure "
                "WHERE source=? AND resource_type=? AND status='PENDING'",
                (source, resource_type),
            ).fetchone()[0]
        )
