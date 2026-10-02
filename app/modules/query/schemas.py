from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pergunta: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=100)


class SourceResponse(BaseModel):
    rank: int
    chunk_id: str
    relevance_score: float
    metadata: dict[str, Any]


class GenerateResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
