from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "credentials",
    "jwt",
    "openai_api_key",
    "password",
    "secret",
    "senha",
    "set-cookie",
    "token",
}

SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b"),
    re.compile(r"\bsk-proj-[A-Za-z0-9_\-]{12,}\b"),
    re.compile(r"\bsk-or-v1-[A-Za-z0-9_\-]{12,}\b"),
    re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9_\-\.=]{12,}"),
    re.compile(r"(?i)\b(api[_-]?key|token|password|senha|secret)\s*[:=]\s*[^\s,;]+"),
)


AuditTrace = dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_trace_id() -> str:
    return str(uuid4())


def sanitize_for_audit(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text.lower().replace("-", "_") in SENSITIVE_KEYS:
                sanitized[key_text] = "[REDACTED]"
            else:
                sanitized[key_text] = sanitize_for_audit(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_for_audit(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_for_audit(item) for item in value]
    if isinstance(value, str):
        sanitized = value
        for pattern in SECRET_PATTERNS:
            sanitized = pattern.sub("[REDACTED]", sanitized)
        return sanitized
    return value
