from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import sqlite3
import uuid

from src.ingestion.checkpoint import (
    SyncJobSpec,
    SyncWindowSpec,
    normalized_watermark,
)
from src.obs import utc_now


class LeaseConflictError(RuntimeError):
    pass


class LeaseExpiredError(RuntimeError):
    pass


class WindowCompletedError(RuntimeError):
    pass


class WindowContinuityError(RuntimeError):
    pass


@dataclass(frozen=True)
class WindowLease:
    window_id: str
    owner: str
    token: str
    expires_at: str


def _utc_datetime(value: datetime | str | None = None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _utc_text(value: datetime | str | None = None) -> str:
    return _utc_datetime(value).isoformat(timespec="microseconds")


class SyncRepository:
    """Estado v2 de sincronização, independente do checkpoint legado."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    @contextmanager
    def _immediate(self):
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    def register_job(self, spec: SyncJobSpec):
        now = utc_now()
        self.connection.execute(
            "INSERT OR IGNORE INTO sync_job "
            "(id, source, mode, base_id, resource_type, endpoint, uf, modality, "
            "config_hash, config_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                spec.job_id,
                spec.source,
                spec.mode,
                spec.base_id,
                spec.resource_type,
                spec.endpoint,
                spec.uf,
                spec.modality,
                spec.configuration_hash,
                spec.configuration_json,
                now,
            ),
        )
        self.connection.commit()
        row = self.get_job(spec.job_id)
        if row is None or row["config_json"] != spec.configuration_json:
            raise ValueError("Identidade do job conflita com outra configuração")
        return row

    def get_job(self, job_id: str):
        return self.connection.execute(
            "SELECT * FROM sync_job WHERE id = ?", (job_id,)
        ).fetchone()

    def create_window(self, spec: SyncWindowSpec):
        if self.get_job(spec.job_id) is None:
            raise ValueError("Job não registrado para a janela")
        now = utc_now()
        self.connection.execute(
            "INSERT OR IGNORE INTO sync_window "
            "(id, job_id, window_start, window_end, status, created_at, "
            "updated_at) VALUES (?, ?, ?, ?, 'PENDING', ?, ?)",
            (
                spec.window_id,
                spec.job_id,
                spec.start,
                spec.end,
                now,
                now,
            ),
        )
        self.connection.commit()
        return self.get_window(spec.window_id)

    def get_window(self, window_id: str):
        return self.connection.execute(
            "SELECT * FROM sync_window WHERE id = ?", (window_id,)
        ).fetchone()

    def acquire_window(
        self,
        window_id: str,
        owner: str,
        lease_seconds: float = 300,
        run_id: str | None = None,
        now: datetime | str | None = None,
        allow_completed: bool = False,
    ) -> WindowLease:
        if not owner.strip():
            raise ValueError("Lease requer proprietário")
        if lease_seconds <= 0:
            raise ValueError("Lease deve possuir duração positiva")
        current_time = _utc_datetime(now)
        expires_at = current_time + timedelta(seconds=lease_seconds)
        token = str(uuid.uuid4())
        with self._immediate():
            row = self.get_window(window_id)
            if row is None:
                raise ValueError("Janela não encontrada")
            if row["status"] == "COMPLETED" and not allow_completed:
                raise WindowCompletedError("Janela já concluída")
            if row["status"] == "RUNNING" and row["lease_expires_at"]:
                previous_expiry = _utc_datetime(row["lease_expires_at"])
                if previous_expiry > current_time:
                    raise LeaseConflictError(
                        f"Janela pertence ao worker {row['lease_owner']}"
                    )
            self.connection.execute(
                "UPDATE sync_window SET status='RUNNING', active_run_id=?, "
                "lease_owner=?, lease_token=?, lease_expires_at=?, "
                "attempt_count=attempt_count+1, error_message=NULL, "
                "completed_at=NULL, updated_at=? WHERE id=?",
                (
                    run_id,
                    owner,
                    token,
                    expires_at.isoformat(timespec="microseconds"),
                    current_time.isoformat(timespec="microseconds"),
                    window_id,
                ),
            )
        return WindowLease(
            window_id,
            owner,
            token,
            expires_at.isoformat(timespec="microseconds"),
        )

    def attach_run(
        self,
        window_id: str,
        lease_token: str,
        run_id: str,
        now: datetime | str | None = None,
    ) -> None:
        current_time = _utc_datetime(now)
        with self._immediate():
            self._require_lease(window_id, lease_token, current_time)
            run = self.connection.execute(
                "SELECT status FROM ingestion_run WHERE id=?", (run_id,)
            ).fetchone()
            if run is None or run["status"] != "RUNNING":
                raise ValueError("A janela só aceita uma execução RUNNING")
            self.connection.execute(
                "UPDATE sync_window SET active_run_id=?, updated_at=? WHERE id=?",
                (run_id, current_time.isoformat(timespec="microseconds"), window_id),
            )

    def renew_lease(
        self,
        window_id: str,
        lease_token: str,
        lease_seconds: float = 300,
        now: datetime | str | None = None,
    ) -> WindowLease:
        current_time = _utc_datetime(now)
        expires_at = current_time + timedelta(seconds=lease_seconds)
        with self._immediate():
            row = self._require_lease(window_id, lease_token, current_time)
            self.connection.execute(
                "UPDATE sync_window SET lease_expires_at=?, updated_at=? "
                "WHERE id=?",
                (
                    expires_at.isoformat(timespec="microseconds"),
                    current_time.isoformat(timespec="microseconds"),
                    window_id,
                ),
            )
        return WindowLease(
            window_id,
            row["lease_owner"],
            lease_token,
            expires_at.isoformat(timespec="microseconds"),
        )

    def register_target(
        self, window_id: str, target_key: str, fingerprint: str
    ):
        if not target_key or not fingerprint:
            raise ValueError("Alvo requer identidade e fingerprint")
        window = self.get_window(window_id)
        if window is None:
            raise ValueError("Janela não encontrada")
        if window["status"] == "COMPLETED":
            raise WindowCompletedError(
                "Alvos de uma janela concluída são imutáveis"
            )
        now = utc_now()
        self.connection.execute(
            "INSERT INTO sync_target_progress "
            "(window_id, target_key, target_fingerprint, status, created_at, "
            "updated_at) VALUES (?, ?, ?, 'PENDING', ?, ?) "
            "ON CONFLICT(window_id, target_key) DO UPDATE SET "
            "target_fingerprint=excluded.target_fingerprint, "
            "status=CASE WHEN sync_target_progress.target_fingerprint <> "
            "excluded.target_fingerprint THEN 'PENDING' "
            "ELSE sync_target_progress.status END, "
            "active_run_id=CASE WHEN sync_target_progress.target_fingerprint <> "
            "excluded.target_fingerprint THEN NULL "
            "ELSE sync_target_progress.active_run_id END, "
            "error_message=CASE WHEN sync_target_progress.target_fingerprint <> "
            "excluded.target_fingerprint THEN NULL "
            "ELSE sync_target_progress.error_message END, "
            "completed_at=CASE WHEN sync_target_progress.target_fingerprint <> "
            "excluded.target_fingerprint THEN NULL "
            "ELSE sync_target_progress.completed_at END, updated_at=excluded.updated_at",
            (window_id, target_key, fingerprint, now, now),
        )
        self.connection.commit()
        return self.get_target(window_id, target_key)

    def get_target(self, window_id: str, target_key: str):
        return self.connection.execute(
            "SELECT * FROM sync_target_progress "
            "WHERE window_id=? AND target_key=?",
            (window_id, target_key),
        ).fetchone()

    def claim_target(
        self,
        window_id: str,
        target_key: str,
        lease_token: str,
        now: datetime | str | None = None,
    ) -> bool:
        current_time = _utc_datetime(now)
        with self._immediate():
            window = self._require_lease(window_id, lease_token, current_time)
            self._require_active_run(window)
            target = self.get_target(window_id, target_key)
            if target is None:
                raise ValueError("Alvo não registrado")
            if (
                target["status"] == "COMPLETED"
                and target["processed_fingerprint"]
                == target["target_fingerprint"]
            ):
                return False
            self.connection.execute(
                "UPDATE sync_target_progress SET status='RUNNING', "
                "active_run_id=?, error_message=NULL, updated_at=? "
                "WHERE window_id=? AND target_key=?",
                (
                    window["active_run_id"],
                    current_time.isoformat(timespec="microseconds"),
                    window_id,
                    target_key,
                ),
            )
        return True

    def complete_target(
        self,
        window_id: str,
        target_key: str,
        lease_token: str,
        now: datetime | str | None = None,
    ) -> None:
        current_time = _utc_datetime(now)
        with self._immediate():
            window = self._require_lease(
                window_id, lease_token, current_time
            )
            self._require_active_run(window)
            target = self.get_target(window_id, target_key)
            if target is None or target["status"] != "RUNNING":
                raise ValueError("Somente um alvo RUNNING pode ser concluído")
            self._mark_target_completed(
                window_id,
                target_key,
                target["target_fingerprint"],
                current_time,
                window["active_run_id"],
            )

    def confirm_target(
        self,
        window_id: str,
        target_key: str,
        fingerprint: str,
        lease_token: str,
        cursor: str | None = None,
        now: datetime | str | None = None,
    ) -> None:
        """Confirma o alvo somente após seus RAWs terem sido persistidos."""

        current_time = _utc_datetime(now)
        with self._immediate():
            window = self._require_lease(
                window_id, lease_token, current_time
            )
            self._require_active_run(window)
            existing = self.get_target(window_id, target_key)
            if existing is None:
                self.connection.execute(
                    "INSERT INTO sync_target_progress "
                    "(window_id, target_key, target_fingerprint, "
                    "processed_fingerprint, status, active_run_id, created_at, "
                    "updated_at, completed_at) "
                    "VALUES (?, ?, ?, ?, 'COMPLETED', ?, ?, ?, ?)",
                    (
                        window_id,
                        target_key,
                        fingerprint,
                        fingerprint,
                        window["active_run_id"],
                        current_time.isoformat(timespec="microseconds"),
                        current_time.isoformat(timespec="microseconds"),
                        current_time.isoformat(timespec="microseconds"),
                    ),
                )
            else:
                if existing["target_fingerprint"] != fingerprint:
                    raise ValueError(
                        "Fingerprint do alvo mudou durante o processamento"
                    )
                self._mark_target_completed(
                    window_id,
                    target_key,
                    fingerprint,
                    current_time,
                    window["active_run_id"],
                )
            if cursor is not None:
                self.connection.execute(
                    "UPDATE sync_window SET progress_cursor=?, updated_at=? "
                    "WHERE id=?",
                    (
                        str(cursor),
                        current_time.isoformat(timespec="microseconds"),
                        window_id,
                    ),
                )

    def update_cursor(
        self,
        window_id: str,
        cursor: str,
        lease_token: str,
        now: datetime | str | None = None,
    ) -> None:
        current_time = _utc_datetime(now)
        with self._immediate():
            window = self._require_lease(
                window_id, lease_token, current_time
            )
            self._require_active_run(window)
            self.connection.execute(
                "UPDATE sync_window SET progress_cursor=?, updated_at=? "
                "WHERE id=?",
                (
                    str(cursor),
                    current_time.isoformat(timespec="microseconds"),
                    window_id,
                ),
            )

    def list_pending_targets(self, window_id: str):
        return self.connection.execute(
            "SELECT * FROM sync_target_progress WHERE window_id=? AND "
            "(status <> 'COMPLETED' OR processed_fingerprint IS NULL OR "
            "processed_fingerprint <> target_fingerprint) ORDER BY target_key",
            (window_id,),
        ).fetchall()

    def fail_window(
        self,
        window_id: str,
        lease_token: str,
        error: str,
        now: datetime | str | None = None,
    ) -> None:
        current_time = _utc_datetime(now)
        with self._immediate():
            self._require_lease(window_id, lease_token, current_time)
            now_text = current_time.isoformat(timespec="microseconds")
            self.connection.execute(
                "UPDATE sync_target_progress SET status='FAILED', "
                "error_message=?, updated_at=? "
                "WHERE window_id=? AND status='RUNNING'",
                (error, now_text, window_id),
            )
            self.connection.execute(
                "UPDATE sync_window SET status='FAILED', error_message=?, "
                "lease_owner=NULL, lease_token=NULL, lease_expires_at=NULL, "
                "updated_at=? WHERE id=?",
                (error, now_text, window_id),
            )

    def complete_window(
        self,
        window_id: str,
        lease_token: str,
        watermark_value: datetime | date | str,
        tie_breaker: str = "",
        now: datetime | str | None = None,
    ) -> None:
        current_time = _utc_datetime(now)
        watermark_text = normalized_watermark(watermark_value)
        with self._immediate():
            window = self._require_lease(
                window_id, lease_token, current_time
            )
            run_id = window["active_run_id"]
            run = self.connection.execute(
                "SELECT status FROM ingestion_run WHERE id=?", (run_id,)
            ).fetchone()
            if run is None or run["status"] != "SUCCESS":
                raise ValueError(
                    "Watermark exige execução vinculada e concluída com SUCCESS"
                )
            incomplete = self.connection.execute(
                "SELECT COUNT(*) FROM sync_target_progress WHERE window_id=? "
                "AND (status <> 'COMPLETED' OR processed_fingerprint IS NULL "
                "OR processed_fingerprint <> target_fingerprint)",
                (window_id,),
            ).fetchone()[0]
            if incomplete:
                raise ValueError("Janela possui alvos incompletos")
            current = self.connection.execute(
                "SELECT * FROM sync_watermark WHERE job_id=?",
                (window["job_id"],),
            ).fetchone()
            candidate = (watermark_text, str(tie_breaker))
            existing = (
                (current["watermark_value"], current["tie_breaker"])
                if current is not None
                else None
            )
            self._require_watermark_matches_window(window, watermark_text)
            if existing is None or candidate > existing:
                self._require_contiguous_coverage(window, current)
            now_text = current_time.isoformat(timespec="microseconds")
            self.connection.execute(
                "UPDATE sync_window SET status='COMPLETED', "
                "lease_owner=NULL, lease_token=NULL, lease_expires_at=NULL, "
                "error_message=NULL, completed_at=?, updated_at=? WHERE id=?",
                (now_text, now_text, window_id),
            )
            if existing is None or candidate > existing:
                self.connection.execute(
                    "INSERT INTO sync_watermark "
                    "(job_id, watermark_value, tie_breaker, last_window_id, "
                    "confirmed_run_id, updated_at) VALUES (?, ?, ?, ?, ?, ?) "
                    "ON CONFLICT(job_id) DO UPDATE SET "
                    "watermark_value=excluded.watermark_value, "
                    "tie_breaker=excluded.tie_breaker, "
                    "last_window_id=excluded.last_window_id, "
                    "confirmed_run_id=excluded.confirmed_run_id, "
                    "updated_at=excluded.updated_at",
                    (
                        window["job_id"],
                        watermark_text,
                        str(tie_breaker),
                        window_id,
                        run_id,
                        now_text,
                    ),
                )

    @staticmethod
    def _require_watermark_matches_window(window, watermark_text: str) -> None:
        watermark_date = (
            datetime.fromisoformat(watermark_text).date().isoformat()
        )
        if watermark_date != window["window_end"]:
            raise WindowContinuityError(
                "Watermark deve pertencer à data final da janela: "
                f"esperado={window['window_end']}, recebido={watermark_date}"
            )

    def _require_contiguous_coverage(self, window, current) -> None:
        covered_date = None
        if current is not None:
            covered_date = datetime.fromisoformat(
                current["watermark_value"]
            ).date()
            next_uncovered = covered_date + timedelta(days=1)
            window_start = date.fromisoformat(window["window_start"])
            if window_start > next_uncovered:
                raise WindowContinuityError(
                    "Janela deixa lacuna após o watermark confirmado: "
                    f"watermark={covered_date.isoformat()}, "
                    f"window_start={window['window_start']}"
                )

        parameters: list[str] = [
            window["job_id"],
            window["id"],
            window["window_start"],
            window["window_start"],
            window["window_end"],
        ]
        coverage_filter = ""
        if covered_date is not None:
            coverage_filter = "AND window_end > ? "
            parameters.append(covered_date.isoformat())
        blocker = self.connection.execute(
            "SELECT id, window_start, window_end, status FROM sync_window "
            "WHERE job_id=? AND id<>? AND status<>'COMPLETED' AND ("
            "window_start < ? OR (window_start = ? AND window_end < ?)) "
            f"{coverage_filter}"
            "ORDER BY window_start, window_end, id LIMIT 1",
            parameters,
        ).fetchone()
        if blocker is not None:
            raise WindowContinuityError(
                "Janela anterior ainda não foi concluída: "
                f"id={blocker['id']}, status={blocker['status']}, "
                f"intervalo={blocker['window_start']}..{blocker['window_end']}"
            )

    def get_watermark(self, job_id: str):
        return self.connection.execute(
            "SELECT * FROM sync_watermark WHERE job_id=?", (job_id,)
        ).fetchone()

    def recoverable_windows(
        self, job_id: str, now: datetime | str | None = None
    ):
        now_text = _utc_text(now)
        return self.connection.execute(
            "SELECT * FROM sync_window WHERE job_id=? AND ("
            "status IN ('PENDING', 'FAILED') OR "
            "(status='RUNNING' AND lease_expires_at <= ?)) "
            "ORDER BY window_start, window_end",
            (job_id, now_text),
        ).fetchall()

    def require_active_lease(
        self,
        window_id: str,
        lease_token: str,
        run_id: str,
        now: datetime | str | None = None,
    ):
        """Aplica fencing ao efeito protegido pela transação atual.

        A validação deve compartilhar a transação de escrita com o
        efeito protegido. Desse modo, outro worker não pode recuperar a janela
        entre a verificação do token e o commit desse efeito.
        """

        if not self.connection.in_transaction:
            raise RuntimeError(
                "Validação de lease para escrita exige transação ativa"
            )
        window = self._require_lease(
            window_id, lease_token, _utc_datetime(now)
        )
        self._require_active_run(window)
        if window["active_run_id"] != run_id:
            raise LeaseConflictError(
                "Lease não está vinculado a esta execução"
            )
        return window

    def _require_lease(
        self, window_id: str, lease_token: str, now: datetime
    ):
        row = self.get_window(window_id)
        if (
            row is None
            or row["status"] != "RUNNING"
            or row["lease_token"] != lease_token
        ):
            raise LeaseConflictError("Lease não pertence a esta execução")
        if not row["lease_expires_at"] or _utc_datetime(
            row["lease_expires_at"]
        ) <= now:
            raise LeaseExpiredError("Lease da janela expirou")
        return row

    def _mark_target_completed(
        self,
        window_id: str,
        target_key: str,
        fingerprint: str,
        now: datetime,
        run_id: str | None,
    ) -> None:
        now_text = now.isoformat(timespec="microseconds")
        self.connection.execute(
            "UPDATE sync_target_progress SET target_fingerprint=?, "
            "processed_fingerprint=?, status='COMPLETED', error_message=NULL, "
            "active_run_id=?, completed_at=?, updated_at=? "
            "WHERE window_id=? AND target_key=?",
            (
                fingerprint,
                fingerprint,
                run_id,
                now_text,
                now_text,
                window_id,
                target_key,
            ),
        )

    def _require_active_run(self, window) -> None:
        run_id = window["active_run_id"]
        run = self.connection.execute(
            "SELECT status FROM ingestion_run WHERE id=?", (run_id,)
        ).fetchone()
        if run is None or run["status"] != "RUNNING":
            raise ValueError(
                "Confirmação de progresso exige ingestion_run RUNNING"
            )
