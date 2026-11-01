from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.feedback.model import PrivateQueryFeedback
from app.modules.feedback.schemas import FeedbackCreate
from app.modules.history.model import QueryHistoryEvent


class FeedbackTargetNotFound(LookupError):
    pass


def _owned_history_event(
    db: Session,
    *,
    history_id: int,
    user_id: int,
) -> QueryHistoryEvent:
    current = datetime.now(timezone.utc).replace(tzinfo=None)
    event = db.scalar(
        select(QueryHistoryEvent).where(
            QueryHistoryEvent.id == history_id,
            QueryHistoryEvent.user_id == user_id,
            QueryHistoryEvent.expires_at > current,
        )
    )
    if event is None:
        raise FeedbackTargetNotFound("Consulta não encontrada no histórico do usuário.")
    return event


def save_feedback(
    db: Session,
    *,
    user_id: int,
    data: FeedbackCreate,
) -> PrivateQueryFeedback:
    _owned_history_event(db, history_id=data.history_id, user_id=user_id)
    feedback = db.scalar(
        select(PrivateQueryFeedback).where(
            PrivateQueryFeedback.history_event_id == data.history_id,
            PrivateQueryFeedback.user_id == user_id,
        )
    )
    if feedback is None:
        feedback = PrivateQueryFeedback(
            history_event_id=data.history_id,
            user_id=user_id,
            rating=data.rating,
            reason_code=data.reason_code,
        )
        db.add(feedback)
    else:
        feedback.rating = data.rating
        feedback.reason_code = data.reason_code
    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedback(
    db: Session,
    *,
    user_id: int,
    history_id: int,
) -> PrivateQueryFeedback:
    _owned_history_event(db, history_id=history_id, user_id=user_id)
    feedback = db.scalar(
        select(PrivateQueryFeedback).where(
            PrivateQueryFeedback.history_event_id == history_id,
            PrivateQueryFeedback.user_id == user_id,
        )
    )
    if feedback is None:
        raise FeedbackTargetNotFound("Avaliação não encontrada.")
    return feedback


def delete_feedback(
    db: Session,
    *,
    user_id: int,
    history_id: int,
) -> None:
    _owned_history_event(db, history_id=history_id, user_id=user_id)
    result = db.execute(
        delete(PrivateQueryFeedback).where(
            PrivateQueryFeedback.history_event_id == history_id,
            PrivateQueryFeedback.user_id == user_id,
        )
    )
    if not result.rowcount:
        db.rollback()
        raise FeedbackTargetNotFound("Avaliação não encontrada.")
    db.commit()
