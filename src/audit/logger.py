from __future__ import annotations

import json
import os
from pathlib import Path

from src.audit.schemas import AuditTrace, sanitize_for_audit


DEFAULT_AUDIT_DIR = Path("logs/queries")


def audit_path(trace: AuditTrace, base_dir: Path = DEFAULT_AUDIT_DIR) -> Path:
    started_at = str(trace.get("started_at") or "")
    day = started_at[:10] if len(started_at) >= 10 else "unknown-date"
    trace_id = str(trace["trace_id"])
    return base_dir / day / f"{trace_id}.json"


def write_audit_trace(
    trace: AuditTrace,
    base_dir: str | Path = DEFAULT_AUDIT_DIR,
) -> Path:
    path = audit_path(trace, Path(base_dir))
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = sanitize_for_audit(trace)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    os.replace(temporary, path)
    return path
