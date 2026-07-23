from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.responses import SuccessResponse
from app.schemas.auth import LoginRequest, OAuth2TokenResponse, RegisterRequest, TokenResponse, UserIdentity

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


@router.post(
    "/token",
    response_model=OAuth2TokenResponse,
    summary="OAuth2 password login",
    description="OAuth2 Password Flow token endpoint used by Swagger UI Authorize.",
)
def oauth2_token(request: Request, form: OAuth2PasswordRequestForm = Depends()) -> dict:
    result = request.app.state.auth_service.login(form.username, form.password)
    return {"access_token": result["access_token"], "token_type": result["token_type"]}
