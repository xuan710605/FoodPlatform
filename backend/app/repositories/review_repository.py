import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

class ReviewRepository:
    def __init__(self, factory: sessionmaker[Session]): self._factory=factory
    def list_product(self, product_code, page, page_size):
        with self._factory() as session:
            params={"code":product_code,"limit":page_size,"offset":(page-1)*page_size}
            total=session.execute(text("SELECT COUNT(*) FROM product_review r JOIN product p ON p.id=r.product_id WHERE p.product_code=:code AND r.status='PUBLISHED'"),params).scalar_one()
            rows=session.execute(text("""SELECT r.id,r.review_code,r.order_item_id,p.product_code,p.product_name,u.username,r.rating,r.review_text,r.reviewed_at FROM product_review r JOIN product p ON p.id=r.product_id JOIN sys_user u ON u.id=r.user_id WHERE p.product_code=:code AND r.status='PUBLISHED' ORDER BY r.reviewed_at DESC LIMIT :limit OFFSET :offset"""),params).mappings().all()
            return {"total":int(total),"page":page,"page_size":page_size,"items":[dict(x) for x in rows]}
    def list_user(self,user_id,page,page_size):
        with self._factory() as session:
            params={"u":user_id,"limit":page_size,"offset":(page-1)*page_size}
            total=session.execute(text("SELECT COUNT(*) FROM product_review WHERE user_id=:u"),params).scalar_one()
            rows=session.execute(text("""SELECT r.id,r.review_code,r.order_item_id,p.product_code,p.product_name,u.username,r.rating,r.review_text,r.reviewed_at FROM product_review r JOIN product p ON p.id=r.product_id JOIN sys_user u ON u.id=r.user_id WHERE r.user_id=:u ORDER BY r.reviewed_at DESC LIMIT :limit OFFSET :offset"""),params).mappings().all()
            return {"total":int(total),"page":page,"page_size":page_size,"items":[dict(x) for x in rows]}
    def create(self,user_id,payload):
        with self._factory.begin() as session:
            row=session.execute(text("""SELECT oi.id,oi.product_id,o.order_status,EXISTS(SELECT 1 FROM product_review r WHERE r.order_item_id=oi.id) reviewed FROM order_item oi JOIN order_info o ON o.id=oi.order_id WHERE oi.id=:item AND o.user_id=:u FOR UPDATE"""),{"item":payload["order_item_id"],"u":user_id}).mappings().first()
            if not row:return {"error":"ORDER_ITEM_NOT_FOUND"}
            if row["order_status"]!="COMPLETED":return {"error":"ORDER_NOT_COMPLETED"}
            if row["reviewed"]:return {"error":"ALREADY_REVIEWED"}
            code="REV"+uuid.uuid4().hex[:20].upper()
            review_id=session.execute(text("INSERT INTO product_review(review_code,order_item_id,user_id,product_id,rating,review_text,status,reviewed_at) VALUES(:code,:item,:u,:p,:rating,:body,'PUBLISHED',CURRENT_TIMESTAMP(3))"),{"code":code,"item":row["id"],"u":user_id,"p":row["product_id"],"rating":payload["rating"],"body":payload.get("review_text")}).lastrowid
        return self.get(review_id)
    def get(self,review_id):
        with self._factory() as session:
            row=session.execute(text("""SELECT r.id,r.review_code,r.order_item_id,p.product_code,p.product_name,u.username,r.rating,r.review_text,r.reviewed_at FROM product_review r JOIN product p ON p.id=r.product_id JOIN sys_user u ON u.id=r.user_id WHERE r.id=:id"""),{"id":review_id}).mappings().first();return dict(row) if row else None