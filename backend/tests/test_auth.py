from datetime import datetime, timezone

import bcrypt
import jwt
import pytest

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.dependencies.auth import require_role
from app.schemas.auth import UserIdentity
from app.services.auth_service import AuthService


class MemoryUserRepository:
    def __init__(self):
        self.user = None
        self.saved_hash = None
        self.login_recorded = False

    def username_exists(self, username):
        return self.user is not None and self.user["username"] == username

    def email_exists(self, email):
        return self.user is not None and self.user["email"] == email

    def create_consumer(self, username, email, password_hash, nickname):
        self.saved_hash = password_hash
        self.user = {
            "id": 31, "user_code": "USRTEST31", "username": username, "email": email,
            "user_type": "CONSUMER", "status": "ACTIVE", "roles": ["CONSUMER"],
            "created_at": datetime(2026, 7, 23, tzinfo=timezone.utc),
            "password_hash": password_hash,
        }
        return {key: value for key, value in self.user.items() if key != "password_hash"}

    def find_for_login(self, identity):
        if self.user and identity in {self.user["username"], self.user["email"]}:
            return dict(self.user)
        return None

    def get_identity(self, user_id):
        if self.user and self.user["id"] == user_id:
            return {key: value for key, value in self.user.items() if key != "password_hash"}
        return None

    def record_login(self, _user_id):
        self.login_recorded = True


@pytest.fixture
def auth_service():
    repository = MemoryUserRepository()
    return AuthService(repository, get_settings()), repository


def test_register_success_and_password_is_bcrypt(auth_service):
    service, repository = auth_service
    user = service.register("new_user", "new@example.test", "StrongPass123", None)
    assert user["roles"] == ["CONSUMER"]
    assert repository.saved_hash != "StrongPass123"
    assert repository.saved_hash.startswith("$2")
    assert bcrypt.checkpw(b"StrongPass123", repository.saved_hash.encode("ascii"))


def test_duplicate_email(auth_service):
    service, _ = auth_service
    service.register("new_user", "new@example.test", "StrongPass123", None)
    with pytest.raises(AppError) as raised:
        service.register("other_user", "new@example.test", "StrongPass456", None)
    assert raised.value.code == "EMAIL_ALREADY_EXISTS"


def test_login_success_returns_valid_jwt(auth_service):
    service, repository = auth_service
    service.register("new_user", "new@example.test", "StrongPass123", None)
    result = service.login("new_user", "StrongPass123")
    claims = jwt.decode(
        result["access_token"],
        get_settings().jwt_secret.get_secret_value(),
        algorithms=[get_settings().jwt_algorithm],
    )
    assert claims["user_id"] == 31
    assert claims["roles"] == ["CONSUMER"]
    assert repository.login_recorded


def test_login_wrong_password(auth_service):
    service, _ = auth_service
    service.register("new_user", "new@example.test", "StrongPass123", None)
    with pytest.raises(AppError) as raised:
        service.login("new_user", "wrong-password")
    assert raised.value.code == "INVALID_CREDENTIALS"


def test_authentication_and_role_guards(client):
    assert client.get("/api/v1/users/me").status_code == 401
    invalid = client.get("/api/v1/users/me", headers={"Authorization": "Bearer wrong"})
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "INVALID_TOKEN"
    valid = client.get("/api/v1/users/me", headers={"Authorization": "Bearer good-token"})
    assert valid.status_code == 200
    consumer = UserIdentity.model_validate(valid.json()["data"])
    admin_guard = require_role("ADMIN")
    with pytest.raises(AppError) as raised:
        admin_guard(current_user=consumer)
    assert raised.value.code == "INSUFFICIENT_ROLE"


def test_register_and_login_http_contract(client):
    registered = client.post("/api/v1/auth/register", json={
        "username": "api_user", "email": "api_user@example.com", "password": "StrongPass123"
    })
    assert registered.status_code == 201
    assert registered.json()["data"]["roles"] == ["CONSUMER"]
    logged_in = client.post("/api/v1/auth/login", json={
        "username": "api_user", "password": "StrongPass123"
    })
    assert logged_in.status_code == 200
    assert logged_in.json()["data"]["token_type"] == "bearer"
    assert logged_in.json()["data"]["access_token"] == "good-token"


def test_swagger_oauth2_form_login_and_authenticated_user(client):
    openapi = client.get("/openapi.json").json()
    password_flow = openapi["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]["password"]
    assert password_flow["tokenUrl"] == "/api/v1/auth/token"
    token_content = openapi["paths"]["/api/v1/auth/token"]["post"]["requestBody"]["content"]
    assert "application/x-www-form-urlencoded" in token_content

    logged_in = client.post("/api/v1/auth/token", data={
        "username": "api_user", "password": "StrongPass123"
    })
    assert logged_in.status_code == 200
    assert logged_in.json() == {"access_token": "good-token", "token_type": "bearer"}

    current_user = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {logged_in.json()['access_token']}"},
    )
    assert current_user.status_code == 200
    assert current_user.json()["data"]["username"] == "test_consumer"


def test_swagger_oauth2_form_login_wrong_password(client):
    response = client.post("/api/v1/auth/token", data={
        "username": "api_user", "password": "wrong-password"
    })
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_auth_cors_preflight(client):
    response = client.options("/api/v1/auth/login", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type",
    })
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "Authorization" in response.headers["access-control-allow-headers"]
