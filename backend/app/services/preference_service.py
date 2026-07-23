from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import AppError
from app.repositories.preference_repository import PreferenceRepository


class PreferenceService:
    def __init__(self, repository: PreferenceRepository):
        self.repository = repository

    def list_preferences(self, user_id: int) -> list[dict[str, Any]]:
        try:
            return self.repository.list_for_user(user_id)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Preference database is unavailable", 503) from exc

    def create_preference(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return self.repository.create(user_id, payload)
        except IntegrityError as exc:
            raise AppError("PREFERENCE_ALREADY_EXISTS", "Preference already exists", 409) from exc
        except (SQLAlchemyError, RuntimeError) as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Preference database is unavailable", 503) from exc

    def delete_preference(self, user_id: int, preference_id: int) -> None:
        try:
            deleted = self.repository.delete_for_user(user_id, preference_id)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Preference database is unavailable", 503) from exc
        if not deleted:
            raise AppError("PREFERENCE_NOT_FOUND", "Preference not found", 404)
