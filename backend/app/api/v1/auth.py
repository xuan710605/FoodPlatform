from fastapi import APIRouter, Request, status

from app.core.responses import SuccessResponse
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserIdentity

router = APIRouter()


@router.post(
    "/register",
    response_model=SuccessResponse[UserIdentity],
    status_code=status.HTTP_201_CREATED,
    summary="Register consumer",
    description="Creates an ACTIVE consumer account with a bcrypt password hash and the CONSUMER role.",
)
def register(request: Request, payload: RegisterRequest) -> dict:
    user = request.app.state.auth_service.register(
        payload.username,
        str(payload.email).lower(),
        payload.password,
        payload.nickname,
    )
    return {"success": True, "data": user, "message": "registered", "request_id": request.state.request_id}


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="Login",
    description="Authenticates by username or email and returns a signed bearer JWT.",
)
def login(request: Request, payload: LoginRequest) -> dict:
    result = request.app.state.auth_service.login(payload.username, payload.password)
    return {"success": True, "data": result, "message": "authenticated", "request_id": request.state.request_id}
