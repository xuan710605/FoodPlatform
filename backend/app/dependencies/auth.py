from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import AppError
from app.schemas.auth import UserIdentity

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


def get_current_user(request: Request, token: str | None = Depends(oauth2_scheme)) -> UserIdentity:
    if not token:
        raise AppError("AUTHENTICATION_REQUIRED", "Bearer access token is required", 401)
    user = request.app.state.auth_service.authenticate_token(token)
    return UserIdentity.model_validate(user)



def get_optional_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
) -> UserIdentity | None:
    if not token:
        return None
    user = request.app.state.auth_service.authenticate_token(token)
    return UserIdentity.model_validate(user)

def require_role(*allowed_roles: str) -> Callable[[UserIdentity], UserIdentity]:
    allowed = set(allowed_roles)

    def dependency(current_user: UserIdentity = Depends(get_current_user)) -> UserIdentity:
        if not allowed.intersection(current_user.roles):
            raise AppError("INSUFFICIENT_ROLE", "User role is not permitted for this operation", 403)
        return current_user

    return dependency
