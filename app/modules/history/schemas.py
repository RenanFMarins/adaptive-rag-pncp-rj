from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QueryHistoryEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route: str | None
    entity: str | None
    status: str
    question_length: int = Field(ge=0)
    result_count: int = Field(ge=0)
    created_at: datetime
    expires_at: datetime


class QueryHistoryListResponse(BaseModel):
    items: list[QueryHistoryEventResponse]
    total: int = Field(ge=0)
    retention_days: int = Field(gt=0)
