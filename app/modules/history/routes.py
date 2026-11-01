from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.model import User
from app.modules.history import services
from app.modules.history.schemas import QueryHistoryListResponse


router = APIRouter(
    prefix="/history",
    tags=["History"],
    responses={401: {"description": "Autenticação necessária"}},
)


@router.get("", response_model=QueryHistoryListResponse)
def list_history(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    offset: Annotated[int, Query(ge=0, le=2**63 - 1)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> QueryHistoryListResponse:
    events, total = services.list_query_history(
        db,
        user_id=user.id,
        offset=offset,
        limit=limit,
    )
    return QueryHistoryListResponse(
        items=events,
        total=total,
        retention_days=settings.query_history_retention_days,
    )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_event(
    event_id: Annotated[int, Path(gt=0, le=2**63 - 1)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    if not services.delete_query_history_event(
        db,
        user_id=user.id,
        event_id=event_id,
    ):
        raise HTTPException(status_code=404, detail="Evento de histórico não encontrado.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_history(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    services.delete_all_query_history(db, user_id=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
