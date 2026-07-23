from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppError


class OrderService:
    def __init__(self, repository, address_repository=None):
        self.repository = repository
        self.address_repository = address_repository

    def create(self, user_id, payload):
        if self.address_repository is None:
            raise AppError("ADDRESS_SERVICE_UNAVAILABLE", "Address service is unavailable", 503)
        try:
            address = self.address_repository.get_for_user(user_id, payload["address_code"])
            if address is None:
                raise AppError("ADDRESS_NOT_FOUND", "Address not found", 404)
            receiver = {
                "address_code": address["address_code"],
                "name": address["receiver_name"],
                "phone": address["receiver_phone"],
                "province": address["province"],
                "city": address["city"],
                "district": address["district"],
                "detail_address": address["detail_address"],
                "postal_code": address.get("postal_code"),
                "address": "".join([
                    address["province"],
                    address["city"],
                    address["district"],
                    address["detail_address"],
                ]),
            }
            result = self.repository.create_order(
                user_id,
                payload.get("cart_item_ids"),
                receiver,
                payload.get("buyer_remark"),
            )
        except AppError:
            raise
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Order database is unavailable", 503) from exc
        return self._validate(result)

    def list(self, user_id, page, page_size):
        try:
            return self.repository.list_orders(user_id, page, page_size)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Order database is unavailable", 503) from exc

    def get(self, user_id, order_id):
        try:
            result = self.repository.get_order(user_id, order_id)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Order database is unavailable", 503) from exc
        if result is None:
            raise AppError("ORDER_NOT_FOUND", "Order not found", 404)
        return result

    def pay(self, user_id, order_id, channel):
        try:
            result = self.repository.pay_order(user_id, order_id, channel)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Order database is unavailable", 503) from exc
        return self._validate(result)

    def cancel(self, user_id, order_id):
        try:
            result = self.repository.cancel_order(user_id, order_id)
        except SQLAlchemyError as exc:
            raise AppError("MYSQL_UNAVAILABLE", "Order database is unavailable", 503) from exc
        return self._validate(result)

    @staticmethod
    def _validate(result):
        if result is None:
            raise AppError("ORDER_NOT_FOUND", "Order not found", 404)
        errors = {
            "CART_EMPTY": ("CART_EMPTY", "No selected cart items", 409),
            "MULTIPLE_MERCHANTS": ("MULTIPLE_MERCHANTS", "Create one order per merchant", 409),
            "INSUFFICIENT_STOCK": ("INSUFFICIENT_STOCK", "Insufficient product stock", 409),
            "INVALID_ORDER_STATUS": ("INVALID_ORDER_STATUS", "Order status does not allow this operation", 409),
            "ALREADY_RESTORED": ("INVENTORY_ALREADY_RESTORED", "Inventory has already been restored", 409),
        }
        if result.get("error") in errors:
            code, message, status = errors[result["error"]]
            raise AppError(code, message, status, {key: value for key, value in result.items() if key != "error"} or None)
        return result
