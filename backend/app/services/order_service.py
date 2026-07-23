from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import AppError

class OrderService:
    def __init__(self,repository): self.repository=repository
    def create(self,user_id,payload):
        if not payload["receiver"]:raise AppError("RECEIVER_REQUIRED","Receiver snapshot is required",422)
        try:result=self.repository.create_order(user_id,payload.get("cart_item_ids"),payload["receiver"],payload.get("buyer_remark"))
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Order database is unavailable",503) from exc
        return self._validate(result)
    def list(self,user_id,page,page_size):
        try:return self.repository.list_orders(user_id,page,page_size)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Order database is unavailable",503) from exc
    def get(self,user_id,order_id):
        try:result=self.repository.get_order(user_id,order_id)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Order database is unavailable",503) from exc
        if result is None:raise AppError("ORDER_NOT_FOUND","Order not found",404)
        return result
    def pay(self,user_id,order_id,channel):
        try:result=self.repository.pay_order(user_id,order_id,channel)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Order database is unavailable",503) from exc
        return self._validate(result)
    def cancel(self,user_id,order_id):
        try:result=self.repository.cancel_order(user_id,order_id)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Order database is unavailable",503) from exc
        return self._validate(result)
    @staticmethod
    def _validate(result):
        if result is None:raise AppError("ORDER_NOT_FOUND","Order not found",404)
        errors={"CART_EMPTY":("CART_EMPTY","No selected cart items",409),"MULTIPLE_MERCHANTS":("MULTIPLE_MERCHANTS","Create one order per merchant",409),"INSUFFICIENT_STOCK":("INSUFFICIENT_STOCK","Insufficient product stock",409),"INVALID_ORDER_STATUS":("INVALID_ORDER_STATUS","Order status does not allow this operation",409),"ALREADY_RESTORED":("INVENTORY_ALREADY_RESTORED","Inventory has already been restored",409)}
        if result.get("error") in errors:
            code,message,status=errors[result["error"]];raise AppError(code,message,status,{k:v for k,v in result.items() if k!="error"} or None)
        return result
