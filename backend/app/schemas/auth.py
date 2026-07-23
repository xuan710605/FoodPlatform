from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


RoleName = Literal["CONSUMER", "MERCHANT", "ADMIN", "KNOWLEDGE_ADMIN", "OPS"]


class RegisterRequest(BaseModel):
    username: str = Field(min_length=4, max_length=64, pattern=r"^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    nickname: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_bcrypt_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return value


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128, description="Username or email")
    password: str = Field(min_length=1, max_length=72)


class UserIdentity(BaseModel):
    id: int
    user_code: str
    username: str
    email: str | None
    user_type: str
    status: str
    roles: list[RoleName]
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserIdentity


class TokenClaims(BaseModel):
    sub: str
    user_id: int
    username: str
    roles: list[RoleName]
    exp: int
    iat: int
    jti: str
