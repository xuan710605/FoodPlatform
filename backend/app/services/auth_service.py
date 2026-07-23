import time
import uuid
from typing import Any

import bcrypt
import jwt
from jwt import InvalidTokenError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.config import Settings
from app.core.exceptions import AppError
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, repository: UserRepository, settings: Settings):
        self.repository = repository
        self.settings = settings

    def register(self, username: str, email: str, password: str, nickname: str | None) -> dict[str, Any]:
        try:
            if self.repository.username_exists(username):
                raise AppError("USERNAME_ALREADY_EXISTS", "Username is already registered", 409)
            if self.repository.email_exists(email):
                raise AppError("EMAIL_ALREADY_EXISTS", "Email is already registered", 409)
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("ascii")
            return self.repository.create_consumer(username, email, password_hash, nickname or username)
        except AppError:
            raise
        except IntegrityError as exc:
            raise AppError("USER_ALREADY_EXISTS", "Username or email is already registered", 409) from exc
        except (SQLAlchemyError, RuntimeError) as exc:
            raise AppError("MYSQL_UNAVAILABLE", "User database is unavailable", 503) from exc

    def login(self, identity: str, password: str) -> dict[str, Any]:
        try:
            user = self.repository.find_for_login(identity)
        except (SQLAlchemyError, RuntimeError) as exc:
            raise AppError("MYSQL_UNAVAILABLE", "User database is unavailable", 503) from exc
        if user is None or not self._verify_password(password, user.get("password_hash", "")):
            raise AppError("INVALID_CREDENTIALS", "Invalid username/email or password", 401)
        if user["status"] != "ACTIVE":
            raise AppError("USER_DISABLED", "User account is not active", 403)
        public_user = {key: value for key, value in user.items() if key != "password_hash"}
        token, expires_in = self._issue_token(public_user)
        try:
            self.repository.record_login(user["id"])
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "User database is unavailable", 503) from exc
        return {"access_token": token, "token_type": "bearer", "expires_in": expires_in, "user": public_user}

    def authenticate_token(self, token: str) -> dict[str, Any]:
        try:
            claims = jwt.decode(
                token,
                self.settings.jwt_secret.get_secret_value(),
                algorithms=[self.settings.jwt_algorithm],
                options={"require": ["sub", "user_id", "username", "roles", "exp", "iat", "jti"]},
            )
            user_id = int(claims["user_id"])
            if claims["sub"] != str(user_id):
                raise InvalidTokenError("subject mismatch")
        except (InvalidTokenError, ValueError, TypeError, KeyError) as exc:
            raise AppError("INVALID_TOKEN", "Access token is invalid or expired", 401) from exc
        try:
            user = self.repository.get_identity(user_id)
        except (SQLAlchemyError, RuntimeError) as exc:
            raise AppError("MYSQL_UNAVAILABLE", "User database is unavailable", 503) from exc
        if user is None or user["status"] != "ACTIVE":
            raise AppError("INVALID_TOKEN", "Access token user is unavailable", 401)
        return user

    def _issue_token(self, user: dict[str, Any]) -> tuple[str, int]:
        issued_at = int(time.time())
        expires_in = self.settings.jwt_access_token_minutes * 60
        payload = {
            "sub": str(user["id"]),
            "user_id": user["id"],
            "username": user["username"],
            "roles": user["roles"],
            "iat": issued_at,
            "exp": issued_at + expires_in,
            "jti": str(uuid.uuid4()),
        }
        token = jwt.encode(payload, self.settings.jwt_secret.get_secret_value(), algorithm=self.settings.jwt_algorithm)
        return token, expires_in

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
        except (ValueError, UnicodeError):
            return False
