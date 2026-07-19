from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppError
from app.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def list_products(self, filters: dict[str, Any]) -> dict[str, Any]:
        try:
            total, items = self.repository.list_products(filters)
        except (SQLAlchemyError, RuntimeError) as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Product database is unavailable", 503) from exc
        return {"total": total, "page": filters["page"], "page_size": filters["page_size"], "items": items}

    def get_detail(self, product_code: str) -> dict[str, Any]:
        try:
            product = self.repository.get_detail(product_code)
        except (SQLAlchemyError, RuntimeError) as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Product database is unavailable", 503) from exc
        if product is None:
            raise AppError("PRODUCT_NOT_FOUND", "Product not found", 404)
        return product
