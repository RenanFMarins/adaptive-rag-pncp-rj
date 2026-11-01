from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import perf_event
from app.modules.history.model import QueryHistoryEvent
from src.query.schemas import QueryEntity, QueryRoute


_ALLOWED_STATUSES = frozenset({"success", "error", "refused"})
_ALLOWED_ROUTES = frozenset(item.value for item in QueryRoute)
_ALLOWED_ENTITIES = frozenset(item.value for item in QueryEntity)


def _utc_now_naive() -> datetime:
    """Mantém compatibilidade com DATETIME do SQLite sem perder a referência UTC."""

    return datetime.now(timezone.utc).replace(tzinfo=None)


def _remove_expired(db: Session, now: datetime) -> None:
    db.execute(
        delete(QueryHistoryEvent).where(QueryHistoryEvent.expires_at <= now)
    )


def record_query_event(
    db: Session,
    *,
    user_id: int,
    status: str,
    question_length: int,
    route: str | None = None,
    entity: str | None = None,
    result_count: int = 0,
    now: datetime | None = None,
) -> QueryHistoryEvent:
    """Persiste apenas metadados técnicos com retenção limitada."""

    if status not in _ALLOWED_STATUSES:
        raise ValueError("Status de histórico inválido.")
    if route is not None and route not in _ALLOWED_ROUTES:
        raise ValueError("Rota de histórico inválida.")
    if entity is not None and entity not in _ALLOWED_ENTITIES:
        raise ValueError("Entidade de histórico inválida.")
    if question_length < 0 or result_count < 0:
        raise ValueError("Contagens do histórico não podem ser negativas.")

    current = now or _utc_now_naive()
    _remove_expired(db, current)
    event = QueryHistoryEvent(
        user_id=user_id,
        route=route,
        entity=entity,
        status=status,
        question_length=question_length,
        result_count=result_count,
        expires_at=current + timedelta(days=settings.query_history_retention_days),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def record_query_event_safely(
    db: object,
    *,
    user_id: object,
    status: str,
    question_length: int,
    route: str | None = None,
    entity: str | None = None,
    result_count: int = 0,
) -> int | None:
    """Não deixa uma falha do histórico indisponibilizar a resposta principal."""

    if not isinstance(db, Session) or not isinstance(user_id, int):
        return None
    try:
        return record_query_event(
            db,
            user_id=user_id,
            status=status,
            question_length=question_length,
            route=route,
            entity=entity,
            result_count=result_count,
        ).id
    except Exception as exc:
        db.rollback()
        perf_event(
            "history_persistence",
            "error",
            exception=type(exc).__name__,
        )
        return None


def list_query_history(
    db: Session,
    *,
    user_id: int,
    offset: int,
    limit: int,
    now: datetime | None = None,
) -> tuple[list[QueryHistoryEvent], int]:
    current = now or _utc_now_naive()
    _remove_expired(db, current)
    db.commit()
    filters = (QueryHistoryEvent.user_id == user_id,)
    total = db.scalar(
        select(func.count(QueryHistoryEvent.id)).where(*filters)
    ) or 0
    events = list(
        db.scalars(
            select(QueryHistoryEvent)
            .where(*filters)
            .order_by(QueryHistoryEvent.created_at.desc(), QueryHistoryEvent.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return events, total


def delete_query_history_event(
    db: Session,
    *,
    user_id: int,
    event_id: int,
) -> bool:
    result = db.execute(
        delete(QueryHistoryEvent).where(
            QueryHistoryEvent.id == event_id,
            QueryHistoryEvent.user_id == user_id,
        )
    )
    db.commit()
    return bool(result.rowcount)


def delete_all_query_history(db: Session, *, user_id: int) -> int:
    result = db.execute(
        delete(QueryHistoryEvent).where(QueryHistoryEvent.user_id == user_id)
    )
    db.commit()
    return int(result.rowcount or 0)
