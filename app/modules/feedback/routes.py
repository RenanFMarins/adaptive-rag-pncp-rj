from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.model import User
from app.modules.feedback import services
from app.modules.feedback.schemas import FeedbackCreate, FeedbackResponse


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
    responses={401: {"description": "Autenticação necessária"}},
)


def _not_found(exc: services.FeedbackTargetNotFound) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


@router.post("", response_model=FeedbackResponse)
def create_or_update_feedback(
    data: FeedbackCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> FeedbackResponse:
    try:
        feedback = services.save_feedback(db, user_id=user.id, data=data)
    except services.FeedbackTargetNotFound as exc:
        raise _not_found(exc) from None
    return FeedbackResponse.model_validate(feedback)


@router.get("/{history_id}", response_model=FeedbackResponse)
def read_feedback(
    history_id: Annotated[int, Path(gt=0, le=2**63 - 1)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> FeedbackResponse:
    try:
        feedback = services.get_feedback(
            db,
            user_id=user.id,
            history_id=history_id,
        )
    except services.FeedbackTargetNotFound as exc:
        raise _not_found(exc) from None
    return FeedbackResponse.model_validate(feedback)


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_feedback(
    history_id: Annotated[int, Path(gt=0, le=2**63 - 1)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    try:
        services.delete_feedback(
            db,
            user_id=user.id,
            history_id=history_id,
        )
    except services.FeedbackTargetNotFound as exc:
        raise _not_found(exc) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
