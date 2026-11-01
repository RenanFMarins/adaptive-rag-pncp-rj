from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.query.model import Query


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("queries.id"), index=True)
    rating: Mapped[int]
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    query: Mapped[Query] = relationship(back_populates="feedback")


class PrivateQueryFeedback(Base):
    """Avaliação mínima ligada ao histórico privado do usuário."""

    __tablename__ = "private_query_feedback"
    __table_args__ = (
        CheckConstraint("rating IN (-1, 1)", name="ck_private_feedback_rating"),
        CheckConstraint(
            "reason_code IS NULL OR reason_code IN "
            "('helpful', 'incorrect', 'incomplete', 'outdated', 'other')",
            name="ck_private_feedback_reason",
        ),
        ForeignKeyConstraint(
            ["history_event_id", "user_id"],
            ["query_history_events.id", "query_history_events.user_id"],
            ondelete="CASCADE",
            name="fk_private_feedback_history_owner",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    history_event_id: Mapped[int] = mapped_column(
        unique=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    rating: Mapped[int] = mapped_column(nullable=False)
    reason_code: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
