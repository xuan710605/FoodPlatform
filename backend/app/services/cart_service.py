from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import AppError

class CartService:
    def __init__(self,repository): self.repository=repository
    def get(self,user_id):
        try:return self.repository.get_cart(user_id)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Cart database is unavailable",503) from exc
    def add(self,user_id,payload):
        try: result=self.repository.add_cart_item(user_id,**payload)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Cart database is unavailable",503) from exc
        return self._validate(result)
    def update(self,user_id,item_id,quantity):
        try: result=self.repository.update_cart_item(user_id,item_id,quantity)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Cart database is unavailable",503) from exc
        if result is None:raise AppError("CART_ITEM_NOT_FOUND","Cart item not found",404)
        return self._validate(result)
    def delete(self,user_id,item_id):
        try: deleted=self.repository.delete_cart_item(user_id,item_id)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Cart database is unavailable",503) from exc
        if not deleted:raise AppError("CART_ITEM_NOT_FOUND","Cart item not found",404)
    @staticmethod
    def _validate(result):
        if result.get("error")=="PRODUCT_NOT_SELLABLE":raise AppError("PRODUCT_NOT_SELLABLE","Product or specification is not sellable",404)
        if result.get("error")=="INSUFFICIENT_STOCK":raise AppError("INSUFFICIENT_STOCK","Insufficient product stock",409,{"available":result.get("available",0)})
        return result
