from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import AppError
class ReviewService:
    def __init__(self,repository):self.repository=repository
    def list_product(self,code,page,size):
        try:return self.repository.list_product(code,page,size)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Review database is unavailable",503) from exc
    def list_user(self,user_id,page,size):
        try:return self.repository.list_user(user_id,page,size)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Review database is unavailable",503) from exc
    def create(self,user_id,payload):
        try:result=self.repository.create(user_id,payload)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Review database is unavailable",503) from exc
        errors={"ORDER_ITEM_NOT_FOUND":("ORDER_ITEM_NOT_FOUND","Order item not found",404),"ORDER_NOT_COMPLETED":("ORDER_NOT_COMPLETED","Only completed orders can be reviewed",409),"ALREADY_REVIEWED":("ALREADY_REVIEWED","Order item has already been reviewed",409)}
        if result.get("error") in errors:
            code,message,status=errors[result["error"]];raise AppError(code,message,status)
        return result