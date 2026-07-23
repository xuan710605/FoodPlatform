from fastapi import APIRouter, Depends, Request

from app.core.responses import SuccessResponse
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserIdentity

router = APIRouter()


@router.get(
    "/me",
    response_model=SuccessResponse[UserIdentity],
    summary="Current user",
    description="Returns the active authenticated user's public identity and current roles.",
)
def me(request: Request, current_user: UserIdentity = Depends(get_current_user)) -> dict:
    return {"success": True, "data": current_user, "message": "ok", "request_id": request.state.request_id}
