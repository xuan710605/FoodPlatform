from fastapi import APIRouter, Depends, Path, Request, status

from app.core.responses import SuccessResponse
from app.dependencies.auth import get_current_user
from app.schemas.address import AddressCreate, AddressItem, AddressUpdate
from app.schemas.auth import UserIdentity

router = APIRouter()


@router.get("", response_model=SuccessResponse[list[AddressItem]], summary="List my addresses")
def list_addresses(request: Request, user: UserIdentity = Depends(get_current_user)) -> dict:
    return {"success": True, "data": request.app.state.address_service.list(user.id), "message": "ok", "request_id": request.state.request_id}


@router.post("", response_model=SuccessResponse[AddressItem], status_code=status.HTTP_201_CREATED, summary="Create address")
def create_address(payload: AddressCreate, request: Request, user: UserIdentity = Depends(get_current_user)) -> dict:
    return {"success": True, "data": request.app.state.address_service.create(user.id, payload.model_dump()), "message": "created", "request_id": request.state.request_id}


@router.put("/{address_code}", response_model=SuccessResponse[AddressItem], summary="Update address")
def update_address(payload: AddressUpdate, request: Request, address_code: str = Path(min_length=1, max_length=40), user: UserIdentity = Depends(get_current_user)) -> dict:
    return {"success": True, "data": request.app.state.address_service.update(user.id, address_code, payload.model_dump()), "message": "updated", "request_id": request.state.request_id}


@router.delete("/{address_code}", response_model=SuccessResponse[dict[str, str]], summary="Delete address")
def delete_address(request: Request, address_code: str = Path(min_length=1, max_length=40), user: UserIdentity = Depends(get_current_user)) -> dict:
    request.app.state.address_service.delete(user.id, address_code)
    return {"success": True, "data": {"address_code": address_code}, "message": "deleted", "request_id": request.state.request_id}


@router.put("/{address_code}/default", response_model=SuccessResponse[AddressItem], summary="Set default address")
def set_default_address(request: Request, address_code: str = Path(min_length=1, max_length=40), user: UserIdentity = Depends(get_current_user)) -> dict:
    return {"success": True, "data": request.app.state.address_service.set_default(user.id, address_code), "message": "updated", "request_id": request.state.request_id}
