from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class QueryHistoryEvent(Base):
    """Metadados mínimos de uma consulta, sem pergunta ou resposta bruta."""

    __tablename__ = "query_history_events"
    __table_args__ = (
        CheckConstraint(
            "status IN ('success', 'error', 'refused')",
            name="ck_query_history_status",
        ),
        CheckConstraint(
            "question_length >= 0",
            name="ck_query_history_question_length",
        ),
        CheckConstraint(
            "result_count >= 0",
            name="ck_query_history_result_count",
        ),
        Index(
            "idx_query_history_user_created",
            "user_id",
            "created_at",
        ),
        Index("idx_query_history_expires", "expires_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    route: Mapped[str | None] = mapped_column(String(16))
    entity: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    question_length: Mapped[int] = mapped_column(nullable=False)
    result_count: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
