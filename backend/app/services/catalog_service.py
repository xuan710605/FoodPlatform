from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppError
from app.repositories.catalog_repository import CatalogRepository


class CatalogService:
    def __init__(self, repository: CatalogRepository):
        self.repository = repository

    def categories(self) -> list[dict[str, Any]]:
        try:
            return self.repository.list_categories()
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Catalog database is unavailable", 503) from exc

    def brands(self) -> list[dict[str, Any]]:
        try:
            return self.repository.list_brands()
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Catalog database is unavailable", 503) from exc
