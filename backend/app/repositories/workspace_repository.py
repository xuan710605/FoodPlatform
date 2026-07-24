import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

DB_TO_API_STATUS = {"PENDING_SHIPMENT": "PAID", "SHIPPED": "SHIPPING"}


class WorkspaceRepository:
    def __init__(self, session_factory: sessionmaker[Session]):
        self._factory = session_factory

    @staticmethod
    def _merchant(session: Session, user_id: int) -> dict[str, Any] | None:
        row = session.execute(text("""
            SELECT id,merchant_code,merchant_name,status
            FROM merchant WHERE owner_user_id=:user_id
        """), {"user_id": user_id}).mappings().first()
        return dict(row) if row else None

    def merchant_dashboard(self, user_id: int) -> dict[str, Any] | None:
        with self._factory() as session:
            merchant = self._merchant(session, user_id)
            if merchant is None:
                return None
            row = session.execute(text("""
                SELECT
                  (SELECT COUNT(*) FROM product WHERE merchant_id=:id AND is_deleted=0) product_count,
                  (SELECT COUNT(*) FROM product WHERE merchant_id=:id AND is_deleted=0 AND sale_status='ON_SALE') on_sale_count,
                  (SELECT COUNT(*) FROM product WHERE merchant_id=:id AND is_deleted=0 AND review_status='PENDING') pending_review_count,
                  (SELECT COUNT(*) FROM order_info WHERE merchant_id=:id) order_count,
                  (SELECT COUNT(*) FROM order_info WHERE merchant_id=:id AND order_status NOT IN ('PENDING_PAYMENT','CANCELLED')) paid_order_count,
                  (SELECT COALESCE(SUM(paid_amount),0) FROM order_info WHERE merchant_id=:id AND order_status NOT IN ('PENDING_PAYMENT','CANCELLED')) sales_amount
            """), {"id": merchant["id"]}).mappings().one()
            return merchant | dict(row)

    def merchant_products(self, user_id: int) -> list[dict[str, Any]] | None:
        with self._factory() as session:
            merchant = self._merchant(session, user_id)
            if merchant is None:
                return None
            rows = session.execute(text("""
                SELECT p.product_code,p.product_name name,p.subtitle,p.description,p.raw_ingredient_text,p.allergen_notice,b.brand_name brand,b.brand_code,
                       c.category_name category,c.category_code,
                       (SELECT spec_name FROM product_spec WHERE product_id=p.id AND is_default=1 LIMIT 1) spec_name,
                       (SELECT unit_name FROM product_spec WHERE product_id=p.id AND is_default=1 LIMIT 1) unit_name,
                       (SELECT image_url FROM product_image WHERE product_id=p.id AND image_type='MAIN' AND status='ACTIVE' ORDER BY sort_order,id LIMIT 1) image_url,
                       p.sale_status,p.review_status,
                       (SELECT pp.amount FROM product_price pp JOIN product_spec ps ON ps.id=pp.spec_id
                        WHERE ps.product_id=p.id AND ps.is_default=1 AND pp.price_type='SALE'
                          AND pp.status='ACTIVE' AND pp.valid_from<=CURRENT_TIMESTAMP(3)
                          AND (pp.valid_to IS NULL OR pp.valid_to>CURRENT_TIMESTAMP(3))
                        ORDER BY pp.valid_from DESC,pp.id DESC LIMIT 1) sale_price,
                       (SELECT GREATEST(pi.available_qty-pi.locked_qty,0)
                        FROM product_inventory pi JOIN product_spec ps ON ps.id=pi.spec_id
                        WHERE ps.product_id=p.id AND ps.is_default=1 ORDER BY pi.id LIMIT 1) stock_quantity,
                       p.updated_at
                FROM product p JOIN brand b ON b.id=p.brand_id JOIN category c ON c.id=p.category_id
                WHERE p.merchant_id=:id AND p.is_deleted=0 ORDER BY p.updated_at DESC,p.id DESC
            """), {"id": merchant["id"]}).mappings().all()
            return [dict(row) for row in rows]

    @staticmethod
    def _master_ids(session: Session, merchant_id: int, payload: dict[str, Any]) -> tuple[int | None, int | None]:
        brand_id = session.execute(text("""
            SELECT id FROM brand WHERE brand_code=:code AND status='ACTIVE'
              AND (merchant_id IS NULL OR merchant_id=:merchant_id)
        """), {"code": payload["brand_code"], "merchant_id": merchant_id}).scalar_one_or_none()
        category_id = session.execute(text(
            "SELECT id FROM category WHERE category_code=:code AND status='ACTIVE'"
        ), {"code": payload["category_code"]}).scalar_one_or_none()
        return brand_id, category_id

    def create_product(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        with self._factory.begin() as session:
            merchant = self._merchant(session, user_id)
            if merchant is None:
                return None
            brand_id, category_id = self._master_ids(session, merchant["id"], payload)
            if brand_id is None:
                return {"error": "BRAND_NOT_AVAILABLE"}
            if category_id is None:
                return {"error": "CATEGORY_NOT_FOUND"}
            product_code = "FP" + str(uuid.uuid4().int % 10**12).zfill(12)
            result = session.execute(text("""
                INSERT INTO product
                  (product_code,merchant_id,brand_id,category_id,product_name,subtitle,description,
                   raw_ingredient_text,allergen_notice,match_status,info_source,sale_status,
                   review_status,neo4j_node_key,graph_sync_status)
                VALUES (:code,:merchant_id,:brand_id,:category_id,:name,:subtitle,:description,
                   :raw_ingredient_text,:allergen_notice,'INFORMATION_INSUFFICIENT','商家提交',
                   'DRAFT','PENDING',:code,'PENDING')
            """), payload | {"code": product_code, "merchant_id": merchant["id"], "brand_id": brand_id, "category_id": category_id})
            product_id = int(result.lastrowid)
            spec_code = "SPEC" + uuid.uuid4().hex[:20].upper()
            spec_id = int(session.execute(text("""
                INSERT INTO product_spec (spec_code,product_id,spec_name,unit_name,status,is_default)
                VALUES (:code,:product_id,:name,:unit_name,'ACTIVE',1)
            """), {"code": spec_code, "product_id": product_id, "name": payload["spec_name"], "unit_name": payload["unit_name"]}).lastrowid)
            session.execute(text("""
                INSERT INTO product_price (product_id,spec_id,price_type,amount,currency,valid_from,status)
                VALUES (:product_id,:spec_id,'SALE',:amount,'CNY',CURRENT_TIMESTAMP(3),'ACTIVE')
            """), {"product_id": product_id, "spec_id": spec_id, "amount": payload["price"]})
            session.execute(text("""
                INSERT INTO product_inventory (product_id,spec_id,warehouse_code,available_qty,locked_qty,inventory_status)
                VALUES (:product_id,:spec_id,'DEFAULT',:quantity,0,
                  CASE WHEN :quantity=0 THEN 'OUT_OF_STOCK' WHEN :quantity<=10 THEN 'LOW' ELSE 'NORMAL' END)
            """), {"product_id": product_id, "spec_id": spec_id, "quantity": payload["stock_quantity"]})
            if payload.get("image_url"):
                session.execute(text("""
                    INSERT INTO product_image (product_id,spec_id,image_type,image_url,alt_text,sort_order,status)
                    VALUES (:product_id,:spec_id,'MAIN',:url,:name,0,'ACTIVE')
                """), {"product_id": product_id, "spec_id": spec_id, "url": payload["image_url"], "name": payload["name"]})
            session.execute(text("""
                INSERT INTO product_audit (audit_code,product_id,product_version,audit_stage,audit_status,submitted_by,submitted_at)
                VALUES (:code,:product_id,1,'MANUAL_REVIEW','PENDING',:user_id,CURRENT_TIMESTAMP(3))
            """), {"code": "PA" + uuid.uuid4().hex[:20].upper(), "product_id": product_id, "user_id": user_id})
            return {"product_code": product_code}

    def update_product(self, user_id: int, product_code: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        with self._factory.begin() as session:
            merchant = self._merchant(session, user_id)
            if merchant is None:
                return None
            product = session.execute(text("""
                SELECT p.id,ps.id spec_id FROM product p
                LEFT JOIN product_spec ps ON ps.product_id=p.id AND ps.is_default=1
                WHERE p.product_code=:code AND p.merchant_id=:merchant_id AND p.is_deleted=0 FOR UPDATE
            """), {"code": product_code, "merchant_id": merchant["id"]}).mappings().first()
            if product is None:
                return {"error": "PRODUCT_NOT_FOUND"}
            brand_id, category_id = self._master_ids(session, merchant["id"], payload)
            if brand_id is None:
                return {"error": "BRAND_NOT_AVAILABLE"}
            if category_id is None:
                return {"error": "CATEGORY_NOT_FOUND"}
            if product["spec_id"] is None:
                raise RuntimeError("default product specification is missing")
            session.execute(text("""
                UPDATE product SET brand_id=:brand_id,category_id=:category_id,product_name=:name,
                  subtitle=:subtitle,description=:description,raw_ingredient_text=:raw_ingredient_text,
                  allergen_notice=:allergen_notice,review_status='PENDING',sale_status='DRAFT',graph_sync_status='PENDING'
                WHERE id=:product_id
            """), payload | {"brand_id": brand_id, "category_id": category_id, "product_id": product["id"]})
            session.execute(text("UPDATE product_spec SET spec_name=:name,unit_name=:unit WHERE id=:id"), {"name": payload["spec_name"], "unit": payload["unit_name"], "id": product["spec_id"]})
            session.execute(text("UPDATE product_price SET status='INACTIVE',valid_to=CURRENT_TIMESTAMP(3) WHERE spec_id=:id AND price_type='SALE' AND status='ACTIVE'"), {"id": product["spec_id"]})
            session.execute(text("""
                INSERT INTO product_price (product_id,spec_id,price_type,amount,currency,valid_from,status)
                VALUES (:product_id,:spec_id,'SALE',:amount,'CNY',CURRENT_TIMESTAMP(3),'ACTIVE')
            """), {"product_id": product["id"], "spec_id": product["spec_id"], "amount": payload["price"]})
            session.execute(text("""
                UPDATE product_inventory SET available_qty=:quantity,locked_qty=LEAST(locked_qty,:quantity),
                  inventory_status=CASE WHEN :quantity=0 THEN 'OUT_OF_STOCK' WHEN :quantity<=warning_threshold THEN 'LOW' ELSE 'NORMAL' END,
                  version_no=version_no+1 WHERE spec_id=:spec_id AND warehouse_code='DEFAULT'
            """), {"quantity": payload["stock_quantity"], "spec_id": product["spec_id"]})
            image = session.execute(text("""
                SELECT id FROM product_image
                WHERE product_id=:product_id AND image_type='MAIN'
                ORDER BY sort_order,id LIMIT 1 FOR UPDATE
            """), {"product_id": product["id"]}).scalar_one_or_none()
            if payload.get("image_url"):
                if image is None:
                    session.execute(text("""
                        INSERT INTO product_image (product_id,spec_id,image_type,image_url,alt_text,sort_order,status)
                        VALUES (:product_id,:spec_id,'MAIN',:url,:name,0,'ACTIVE')
                    """), {"product_id": product["id"], "spec_id": product["spec_id"], "url": payload["image_url"], "name": payload["name"]})
                else:
                    session.execute(text("""
                        UPDATE product_image SET image_url=:url,alt_text=:name,status='ACTIVE' WHERE id=:id
                    """), {"url": payload["image_url"], "name": payload["name"], "id": image})
            elif image is not None:
                session.execute(text("UPDATE product_image SET status='INACTIVE' WHERE id=:id"), {"id": image})
            version = session.execute(text("SELECT COALESCE(MAX(product_version),0)+1 FROM product_audit WHERE product_id=:id"), {"id": product["id"]}).scalar_one()
            session.execute(text("""
                INSERT INTO product_audit (audit_code,product_id,product_version,audit_stage,audit_status,submitted_by,submitted_at)
                VALUES (:code,:product_id,:version,'MANUAL_REVIEW','PENDING',:user_id,CURRENT_TIMESTAMP(3))
            """), {"code": "PA" + uuid.uuid4().hex[:20].upper(), "product_id": product["id"], "version": version, "user_id": user_id})
            return {"product_code": product_code}

    def update_sale_status(self, user_id: int, product_code: str, sale_status: str) -> dict[str, Any] | None:
        with self._factory.begin() as session:
            merchant = self._merchant(session, user_id)
            if merchant is None:
                return None
            product = session.execute(text("""
                SELECT id,review_status FROM product WHERE product_code=:code AND merchant_id=:merchant_id AND is_deleted=0 FOR UPDATE
            """), {"code": product_code, "merchant_id": merchant["id"]}).mappings().first()
            if product is None:
                return {"error": "PRODUCT_NOT_FOUND"}
            if sale_status == "ON_SALE" and product["review_status"] != "APPROVED":
                return {"error": "PRODUCT_NOT_APPROVED"}
            session.execute(text("UPDATE product SET sale_status=:status WHERE id=:id"), {"status": sale_status, "id": product["id"]})
            return {"product_code": product_code, "sale_status": sale_status}

    def merchant_orders(self, user_id: int) -> list[dict[str, Any]] | None:
        with self._factory() as session:
            merchant = self._merchant(session, user_id)
            if merchant is None:
                return None
            rows = session.execute(text("""
                SELECT o.id,o.order_no,u.username buyer,o.order_status,o.payable_amount,o.paid_amount,
                  (SELECT COALESCE(SUM(quantity),0) FROM order_item WHERE order_id=o.id) item_count,
                  o.placed_at,o.paid_at,o.shipped_at,o.completed_at
                FROM order_info o JOIN sys_user u ON u.id=o.user_id
                WHERE o.merchant_id=:id ORDER BY o.placed_at DESC,o.id DESC
            """), {"id": merchant["id"]}).mappings().all()
            result=[]
            for row in rows:
                item=dict(row); db_status=item.pop("order_status"); item["status"]=DB_TO_API_STATUS.get(db_status,db_status); result.append(item)
            return result

    def update_merchant_order_status(self, user_id: int, order_id: int, target: str) -> dict[str, Any] | None:
        with self._factory.begin() as session:
            merchant = self._merchant(session, user_id)
            if merchant is None:
                return None
            row = session.execute(text("SELECT id,order_status FROM order_info WHERE id=:id AND merchant_id=:merchant_id FOR UPDATE"), {"id": order_id, "merchant_id": merchant["id"]}).mappings().first()
            if row is None:
                return {"error": "ORDER_NOT_FOUND"}
            transition = {("PENDING_SHIPMENT","SHIPPING"):("SHIPPED","shipped_at"),("SHIPPED","COMPLETED"):("COMPLETED","completed_at")}.get((row["order_status"],target))
            if transition is None:
                return {"error": "INVALID_ORDER_STATUS"}
            db_status,column=transition
            session.execute(text(f"UPDATE order_info SET order_status=:status,{column}=CURRENT_TIMESTAMP(3) WHERE id=:id"), {"status": db_status, "id": order_id})
            return {"id": order_id, "status": target}

    def admin_dashboard(self) -> dict[str, Any]:
        with self._factory() as session:
            return dict(session.execute(text("""
                SELECT (SELECT COUNT(*) FROM sys_user WHERE is_deleted=0) user_count,
                  (SELECT COUNT(*) FROM merchant) merchant_count,
                  (SELECT COUNT(*) FROM product WHERE is_deleted=0) product_count,
                  (SELECT COUNT(*) FROM product WHERE is_deleted=0 AND review_status='PENDING') pending_product_count,
                  (SELECT COUNT(*) FROM order_info) order_count
            """)).mappings().one())

    def admin_users(self, keyword: str | None) -> list[dict[str, Any]]:
        with self._factory() as session:
            normalized = keyword.strip() if keyword else None
            rows=session.execute(text("""
                SELECT u.id,u.user_code,u.username,u.email,u.user_type,u.status,u.created_at,
                  GROUP_CONCAT(DISTINCT r.role_code ORDER BY r.id) role_codes
                FROM sys_user u LEFT JOIN sys_user_role ur ON ur.user_id=u.id AND (ur.expires_at IS NULL OR ur.expires_at>CURRENT_TIMESTAMP(3))
                LEFT JOIN sys_role r ON r.id=ur.role_id AND r.status='ACTIVE'
                WHERE u.is_deleted=0
                  AND (:keyword IS NULL OR u.username LIKE CONCAT('%',:keyword,'%') OR u.email LIKE CONCAT('%',:keyword,'%'))
                GROUP BY u.id,u.user_code,u.username,u.email,u.user_type,u.status,u.created_at ORDER BY u.created_at DESC,u.id DESC
            """), {"keyword": normalized}).mappings().all()
            result=[]
            for row in rows:
                item=dict(row); roles=(item.pop("role_codes") or item["user_type"]).split(","); item["roles"]=["ADMIN" if role=="PLATFORM_ADMIN" else role for role in roles]; result.append(item)
            return result

    def update_admin_user_status(self, user_id: int, target_status: str) -> dict[str, Any]:
        with self._factory.begin() as session:
            row = session.execute(text("""
                SELECT id FROM sys_user WHERE id=:user_id AND is_deleted=0 FOR UPDATE
            """), {"user_id": user_id}).mappings().first()
            if row is None:
                return {"error": "USER_NOT_FOUND"}
            session.execute(text("UPDATE sys_user SET status=:status WHERE id=:user_id"), {"status": target_status, "user_id": user_id})
            return {"id": user_id, "status": target_status}

    def admin_products(self, review_status: str | None) -> list[dict[str, Any]]:
        with self._factory() as session:
            rows=session.execute(text("""
                SELECT p.product_code,p.product_name name,m.merchant_code,m.merchant_name,b.brand_name brand,
                  c.category_name category,p.review_status,p.sale_status,
                  (SELECT MAX(submitted_at) FROM product_audit WHERE product_id=p.id) submitted_at,p.updated_at
                FROM product p JOIN merchant m ON m.id=p.merchant_id JOIN brand b ON b.id=p.brand_id JOIN category c ON c.id=p.category_id
                WHERE p.is_deleted=0 AND (:status IS NULL OR p.review_status=:status) ORDER BY p.updated_at DESC,p.id DESC
            """), {"status": review_status}).mappings().all()
            return [dict(row) for row in rows]

    def approve_product(self, admin_user_id: int, product_code: str, opinion: str | None) -> dict[str, Any] | None:
        with self._factory.begin() as session:
            product=session.execute(text("SELECT id,review_status FROM product WHERE product_code=:code AND is_deleted=0 FOR UPDATE"), {"code": product_code}).mappings().first()
            if product is None:
                return None
            if product["review_status"] != "PENDING":
                return {"error": "PRODUCT_NOT_PENDING"}
            session.execute(text("UPDATE product SET review_status='APPROVED' WHERE id=:id"), {"id": product["id"]})
            audit=session.execute(text("SELECT id FROM product_audit WHERE product_id=:id AND audit_status='PENDING' ORDER BY product_version DESC,id DESC LIMIT 1 FOR UPDATE"), {"id": product["id"]}).scalar_one_or_none()
            if audit is not None:
                session.execute(text("UPDATE product_audit SET audit_status='APPROVED',audit_opinion=:opinion,auditor_user_id=:admin,audited_at=CURRENT_TIMESTAMP(3) WHERE id=:id"), {"opinion": opinion, "admin": admin_user_id, "id": audit})
            return {"product_code": product_code, "review_status": "APPROVED"}