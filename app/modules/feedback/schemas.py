from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


FeedbackReason = Literal["helpful", "incorrect", "incomplete", "outdated", "other"]


class FeedbackCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    history_id: int = Field(gt=0)
    rating: Literal[-1, 1]
    reason_code: FeedbackReason | None = None


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    history_id: int = Field(validation_alias="history_event_id")
    rating: Literal[-1, 1]
    reason_code: FeedbackReason | None
    created_at: datetime
    updated_at: datetime
