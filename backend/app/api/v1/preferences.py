from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, status

from app.core.responses import SuccessResponse
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserIdentity
from app.schemas.preference import PreferenceCreate, PreferenceItem

router = APIRouter()


@router.get(
    "",
    response_model=SuccessResponse[list[PreferenceItem]],
    summary="List preferences",
    description="Lists the current user's allergen, dietary restriction, and nutrition target preferences.",
)
def list_preferences(request: Request, current_user: UserIdentity = Depends(get_current_user)) -> dict:
    items = request.app.state.preference_service.list_preferences(current_user.id)
    return {"success": True, "data": items, "message": "ok", "request_id": request.state.request_id}


@router.post(
    "",
    response_model=SuccessResponse[PreferenceItem],
    status_code=status.HTTP_201_CREATED,
    summary="Create preference",
    description="Stores a preference in the existing user_ingredient_preference table.",
)
def create_preference(
    request: Request,
    payload: PreferenceCreate,
    current_user: UserIdentity = Depends(get_current_user),
) -> dict:
    item = request.app.state.preference_service.create_preference(current_user.id, payload.model_dump())
    return {"success": True, "data": item, "message": "created", "request_id": request.state.request_id}


@router.delete(
    "/{preference_id}",
    response_model=SuccessResponse[dict[str, int]],
    summary="Delete preference",
    description="Deletes one preference owned by the current user.",
)
def delete_preference(
    request: Request,
    preference_id: Annotated[int, Path(gt=0)],
    current_user: UserIdentity = Depends(get_current_user),
) -> dict:
    request.app.state.preference_service.delete_preference(current_user.id, preference_id)
    return {"success": True, "data": {"id": preference_id}, "message": "deleted", "request_id": request.state.request_id}
