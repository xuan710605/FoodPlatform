from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppError
from app.repositories.address_repository import AddressRepository


class AddressService:
    def __init__(self, repository: AddressRepository):
        self.repository = repository

    def list(self, user_id: int) -> list[dict[str, Any]]:
        try:
            return self.repository.list_for_user(user_id)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Address database is unavailable", 503) from exc

    def get(self, user_id: int, address_code: str) -> dict[str, Any]:
        try:
            item = self.repository.get_for_user(user_id, address_code)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Address database is unavailable", 503) from exc
        if item is None:
            raise AppError("ADDRESS_NOT_FOUND", "Address not found", 404)
        return item

    def create(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return self.repository.create(user_id, payload)
        except (SQLAlchemyError, RuntimeError) as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Address database is unavailable", 503) from exc

    def update(self, user_id: int, address_code: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            item = self.repository.update(user_id, address_code, payload)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Address database is unavailable", 503) from exc
        if item is None:
            raise AppError("ADDRESS_NOT_FOUND", "Address not found", 404)
        return item

    def delete(self, user_id: int, address_code: str) -> None:
        try:
            deleted = self.repository.delete(user_id, address_code)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Address database is unavailable", 503) from exc
        if not deleted:
            raise AppError("ADDRESS_NOT_FOUND", "Address not found", 404)

    def set_default(self, user_id: int, address_code: str) -> dict[str, Any]:
        try:
            item = self.repository.set_default(user_id, address_code)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Address database is unavailable", 503) from exc
        if item is None:
            raise AppError("ADDRESS_NOT_FOUND", "Address not found", 404)
        return item
