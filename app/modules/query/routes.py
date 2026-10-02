from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.model import User
from app.modules.query.schemas import (
    GenerateRequest,
    GenerateResponse,
    SourceResponse,
)
from src.generate import gerar_resposta_rag


router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/generate", response_model=GenerateResponse)
def generate(
    request: GenerateRequest,
    db: Annotated[Session, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
):
    resultado = gerar_resposta_rag(
        db=db,
        pergunta=request.pergunta,
        top_k=request.top_k,
        persistir=True,
    )

    return GenerateResponse(
        answer=resultado.answer,
        sources=[
            SourceResponse(
                rank=rank,
                chunk_id=source.chunk_id,
                relevance_score=source.rrf_score,
                metadata=source.metadata,
            )
            for rank, source in enumerate(resultado.sources, start=1)
        ],
    )
