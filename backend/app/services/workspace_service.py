from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppError
from app.repositories.workspace_repository import WorkspaceRepository


class WorkspaceService:
    def __init__(self, repository: WorkspaceRepository):
        self.repository = repository

    @staticmethod
    def _raise_error(result: dict[str, Any] | None, missing_code: str, missing_message: str) -> dict[str, Any]:
        if result is None:
            raise AppError(missing_code, missing_message, 404)
        errors = {
            "PRODUCT_NOT_FOUND": ("PRODUCT_NOT_FOUND", "Product not found", 404),
            "ORDER_NOT_FOUND": ("ORDER_NOT_FOUND", "Order not found", 404),
            "BRAND_NOT_AVAILABLE": ("BRAND_NOT_AVAILABLE", "Brand is not available to this merchant", 409),
            "CATEGORY_NOT_FOUND": ("CATEGORY_NOT_FOUND", "Category not found", 404),
            "PRODUCT_NOT_APPROVED": ("PRODUCT_NOT_APPROVED", "Only approved products can be put on sale", 409),
            "INVALID_ORDER_STATUS": ("INVALID_ORDER_STATUS", "Order status transition is not allowed", 409),
            "PRODUCT_NOT_PENDING": ("PRODUCT_NOT_PENDING", "Only pending products can be approved", 409),
            "USER_NOT_FOUND": ("USER_NOT_FOUND", "User not found", 404),
        }
        if result.get("error") in errors:
            code, message, status = errors[result["error"]]
            raise AppError(code, message, status)
        return result

    def _call(self, function, *args):
        try:
            return function(*args)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Workspace database is unavailable", 503) from exc

    def merchant_dashboard(self, user_id: int) -> dict[str, Any]:
        result = self._call(self.repository.merchant_dashboard, user_id)
        return self._raise_error(result, "MERCHANT_NOT_FOUND", "Merchant profile not found")

    def merchant_products(self, user_id: int) -> list[dict[str, Any]]:
        result = self._call(self.repository.merchant_products, user_id)
        if result is None:
            raise AppError("MERCHANT_NOT_FOUND", "Merchant profile not found", 404)
        return result

    def create_product(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        result = self._call(self.repository.create_product, user_id, payload)
        return self._raise_error(result, "MERCHANT_NOT_FOUND", "Merchant profile not found")

    def update_product(self, user_id: int, product_code: str, payload: dict[str, Any]) -> dict[str, Any]:
        result = self._call(self.repository.update_product, user_id, product_code, payload)
        return self._raise_error(result, "MERCHANT_NOT_FOUND", "Merchant profile not found")

    def update_sale_status(self, user_id: int, product_code: str, sale_status: str) -> dict[str, Any]:
        result = self._call(self.repository.update_sale_status, user_id, product_code, sale_status)
        return self._raise_error(result, "MERCHANT_NOT_FOUND", "Merchant profile not found")

    def merchant_orders(self, user_id: int) -> list[dict[str, Any]]:
        result = self._call(self.repository.merchant_orders, user_id)
        if result is None:
            raise AppError("MERCHANT_NOT_FOUND", "Merchant profile not found", 404)
        return result

    def update_order_status(self, user_id: int, order_id: int, status: str) -> dict[str, Any]:
        result = self._call(self.repository.update_merchant_order_status, user_id, order_id, status)
        return self._raise_error(result, "MERCHANT_NOT_FOUND", "Merchant profile not found")

    def admin_dashboard(self) -> dict[str, Any]:
        return self._call(self.repository.admin_dashboard)

    def admin_users(self, keyword: str | None) -> list[dict[str, Any]]:
        return self._call(self.repository.admin_users, keyword)

    def update_admin_user_status(self, user_id: int, status: str) -> dict[str, Any]:
        result = self._call(self.repository.update_admin_user_status, user_id, status)
        return self._raise_error(result, "USER_NOT_FOUND", "User not found")

    def admin_products(self, review_status: str | None) -> list[dict[str, Any]]:
        return self._call(self.repository.admin_products, review_status)

    def approve_product(self, admin_id: int, product_code: str, opinion: str | None) -> dict[str, Any]:
        result = self._call(self.repository.approve_product, admin_id, product_code, opinion)
        return self._raise_error(result, "PRODUCT_NOT_FOUND", "Product not found")