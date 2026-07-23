from fastapi import APIRouter, Depends, Request

from app.core.responses import SuccessResponse
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserIdentity
from app.schemas.preference import UserFoodPreferences, UserFoodPreferencesUpdate

router = APIRouter()


@router.get(
    "/me",
    response_model=SuccessResponse[UserIdentity],
    summary="Current user",
    description="Returns the active authenticated user's public identity and current roles.",
)
def me(request: Request, current_user: UserIdentity = Depends(get_current_user)) -> dict:
    return {"success": True, "data": current_user, "message": "ok", "request_id": request.state.request_id}

@router.get(
    "/preferences",
    response_model=SuccessResponse[UserFoodPreferences],
    summary="Current user food preferences",
    description="Returns ingredient exclusions and soft preferences owned by the authenticated user.",
)
def get_food_preferences(request: Request, current_user: UserIdentity = Depends(get_current_user)) -> dict:
    data = request.app.state.preference_service.get_food_preferences(current_user.id)
    return {"success": True, "data": data, "message": "ok", "request_id": request.state.request_id}


@router.put(
    "/preferences",
    response_model=SuccessResponse[UserFoodPreferences],
    summary="Replace current user food preferences",
    description="Atomically replaces the authenticated user's ingredient exclusions and soft preferences.",
)
def replace_food_preferences(
    request: Request,
    payload: UserFoodPreferencesUpdate,
    current_user: UserIdentity = Depends(get_current_user),
) -> dict:
    data = request.app.state.preference_service.replace_food_preferences(current_user.id, payload.model_dump())
    return {"success": True, "data": data, "message": "saved", "request_id": request.state.request_id}