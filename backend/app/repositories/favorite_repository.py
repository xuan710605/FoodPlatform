from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

class FavoriteRepository:
    def __init__(self, session_factory: sessionmaker[Session]): self._factory=session_factory
    @staticmethod
    def _select_sql(where:str)->str:
        return f"""SELECT f.id,p.id product_id,p.product_code,p.product_name name,b.brand_name brand,c.category_name category,
        (SELECT image_url FROM product_image WHERE product_id=p.id AND image_type='MAIN' AND status='ACTIVE' ORDER BY sort_order,id LIMIT 1) main_image_url,
        (SELECT pp.amount FROM product_spec s JOIN product_price pp ON pp.spec_id=s.id WHERE s.product_id=p.id AND s.status='ACTIVE' AND pp.price_type='SALE' AND pp.status='ACTIVE' AND pp.valid_from<=CURRENT_TIMESTAMP(3) AND (pp.valid_to IS NULL OR pp.valid_to>CURRENT_TIMESTAMP(3)) ORDER BY s.is_default DESC,pp.valid_from DESC,pp.id DESC LIMIT 1) sale_price,
        p.sale_status,p.review_status audit_status,f.created_at FROM favorite f JOIN product p ON p.id=f.product_id JOIN brand b ON b.id=p.brand_id JOIN category c ON c.id=p.category_id WHERE {where}"""
    def list(self,user_id:int)->list[dict[str,Any]]:
        with self._factory() as session:return [dict(x) for x in session.execute(text(self._select_sql("f.user_id=:u AND p.is_deleted=0")+" ORDER BY f.created_at DESC"),{"u":user_id}).mappings().all()]
    def get(self,user_id:int,product_code:str)->dict[str,Any]|None:
        with self._factory() as session:
            row=session.execute(text(self._select_sql("f.user_id=:u AND p.product_code=:code")),{"u":user_id,"code":product_code}).mappings().first();return dict(row) if row else None
    def add(self,user_id:int,product_code:str)->dict[str,Any]|None:
        with self._factory.begin() as session:
            product_id=session.execute(text("SELECT id FROM product WHERE product_code=:code AND is_deleted=0"),{"code":product_code}).scalar_one_or_none()
            if product_id is None:return None
            session.execute(text("INSERT INTO favorite(user_id,product_id) VALUES(:u,:p) ON DUPLICATE KEY UPDATE updated_at=CURRENT_TIMESTAMP(3)"),{"u":user_id,"p":product_id})
        return self.get(user_id,product_code)
    def delete(self,user_id:int,product_code:str)->bool:
        with self._factory.begin() as session:
            result=session.execute(text("DELETE f FROM favorite f JOIN product p ON p.id=f.product_id WHERE f.user_id=:u AND p.product_code=:code"),{"u":user_id,"code":product_code});return result.rowcount>0
