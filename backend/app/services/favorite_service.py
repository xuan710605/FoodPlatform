from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import AppError

class FavoriteService:
    def __init__(self,repository):self.repository=repository
    def list(self,user_id):
        try:return self.repository.list(user_id)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Favorite database is unavailable",503) from exc
    def add(self,user_id,product_code):
        try:result=self.repository.add(user_id,product_code)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Favorite database is unavailable",503) from exc
        if result is None:raise AppError("PRODUCT_NOT_FOUND","Product not found",404)
        return result
    def delete(self,user_id,product_code):
        try:deleted=self.repository.delete(user_id,product_code)
        except SQLAlchemyError as exc:raise AppError("MYSQL_UNAVAILABLE","Favorite database is unavailable",503) from exc
        if not deleted:raise AppError("FAVORITE_NOT_FOUND","Favorite not found",404)
