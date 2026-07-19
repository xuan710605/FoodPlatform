from collections.abc import Mapping
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker


SORT_COLUMNS = {
    "created_at": "p.created_at",
    "updated_at": "p.updated_at",
    "name": "p.product_name",
    "price": "sale_price",
    "stock": "stock_quantity",
}


class ProductRepository:
    def __init__(self, session_factory: sessionmaker[Session]):
        self._factory = session_factory

    def exists(self, product_code: str) -> bool:
        with self._factory() as session:
            return session.execute(
                text("SELECT 1 FROM product WHERE product_code=:code AND is_deleted=0"),
                {"code": product_code},
            ).first() is not None

    def list_products(self, filters: Mapping[str, Any]) -> tuple[int, list[dict[str, Any]]]:
        where = ["p.is_deleted=0", "p.review_status='APPROVED'"]
        params: dict[str, Any] = {}
        if filters.get("status"):
            where.append("p.sale_status=:status")
            params["status"] = filters["status"]
        else:
            where.append("p.sale_status='ON_SALE'")
        for field, column in (("category_code", "c.category_code"), ("brand_code", "b.brand_code"), ("merchant_id", "p.merchant_id")):
            if filters.get(field) is not None:
                where.append(f"{column}=:{field}")
                params[field] = filters[field]
        if filters.get("keyword"):
            where.append("(p.product_name LIKE :keyword OR p.product_code LIKE :keyword)")
            params["keyword"] = f"%{filters['keyword']}%"

        predicate = " AND ".join(where)
        sort_column = SORT_COLUMNS[filters["sort_by"]]
        sort_order = "DESC" if filters["sort_order"] == "desc" else "ASC"
        params.update(limit=filters["page_size"], offset=(filters["page"] - 1) * filters["page_size"])
        base = """
        FROM product p
        JOIN brand b ON b.id=p.brand_id
        JOIN category c ON c.id=p.category_id
        JOIN merchant m ON m.id=p.merchant_id
        LEFT JOIN product_spec s ON s.product_id=p.id AND s.is_default=1 AND s.status='ACTIVE'
        LEFT JOIN product_inventory inv ON inv.spec_id=s.id AND inv.warehouse_code='DEFAULT'
        """
        price = """
        (SELECT pp.amount FROM product_price pp WHERE pp.spec_id=s.id AND pp.price_type=:price_type
          AND pp.status='ACTIVE' AND pp.valid_from<=CURRENT_TIMESTAMP(3)
          AND (pp.valid_to IS NULL OR pp.valid_to>CURRENT_TIMESTAMP(3))
          ORDER BY pp.valid_from DESC, pp.id DESC LIMIT 1)
        """
        query = text(f"""
        SELECT p.id,p.product_code,p.product_name AS name,p.subtitle,
          b.brand_name AS brand,b.brand_code,c.category_name AS category,c.category_code,
          m.merchant_name AS merchant,p.merchant_id,
          (SELECT pi.image_url FROM product_image pi WHERE pi.product_id=p.id AND pi.image_type='MAIN'
             AND pi.status='ACTIVE' ORDER BY pi.sort_order,pi.id LIMIT 1) AS main_image_url,
          {price.replace(':price_type', "'SALE'")} AS sale_price,
          {price.replace(':price_type', "'LIST'")} AS market_price,
          CASE WHEN inv.id IS NULL THEN NULL ELSE GREATEST(inv.available_qty-inv.locked_qty,0) END AS stock_quantity,
          CASE WHEN inv.id IS NULL THEN NULL WHEN inv.available_qty-inv.locked_qty>0 THEN 1 ELSE 0 END AS sellable,
          p.review_status AS audit_status,p.sale_status,
          (SELECT MAX(psn.version_no) FROM product_ingredient_snapshot psn WHERE psn.product_id=p.id AND psn.effective_to IS NULL) AS ingredient_version,
          p.created_at,p.updated_at
        {base} WHERE {predicate}
        ORDER BY {sort_column} {sort_order}, p.id ASC LIMIT :limit OFFSET :offset
        """)
        with self._factory() as session:
            total = session.execute(text(f"SELECT COUNT(DISTINCT p.id) {base} WHERE {predicate}"), params).scalar_one()
            rows = session.execute(query, params).mappings().all()
            return int(total), [dict(row) for row in rows]

    def get_detail(self, product_code: str) -> dict[str, Any] | None:
        with self._factory() as session:
            base = session.execute(text("""
                SELECT p.id,p.product_code,p.product_name AS name,p.subtitle,p.description,
                  b.brand_name AS brand,b.brand_code,c.category_name AS category,c.category_code,
                  m.merchant_code,m.merchant_name,p.raw_ingredient_text,p.allergen_notice,
                  (SELECT MAX(x.version_no) FROM product_ingredient_snapshot x
                   WHERE x.product_id=p.id AND x.effective_to IS NULL) AS ingredient_version,
                  p.graph_sync_status,p.review_status AS audit_status,p.sale_status,p.created_at,p.updated_at
                FROM product p JOIN brand b ON b.id=p.brand_id JOIN category c ON c.id=p.category_id
                JOIN merchant m ON m.id=p.merchant_id
                WHERE p.product_code=:code AND p.is_deleted=0
            """), {"code": product_code}).mappings().first()
            if base is None:
                return None
            product_id = base["id"]
            specs = self._rows(session, """
                SELECT s.spec_code,s.spec_name,s.unit_name,s.net_content_value,s.net_content_unit,s.is_default,
                  (SELECT pp.amount FROM product_price pp WHERE pp.spec_id=s.id AND pp.price_type='SALE' AND pp.status='ACTIVE'
                   AND pp.valid_from<=CURRENT_TIMESTAMP(3) AND (pp.valid_to IS NULL OR pp.valid_to>CURRENT_TIMESTAMP(3))
                   ORDER BY pp.valid_from DESC,pp.id DESC LIMIT 1) AS sale_price,
                  (SELECT pp.amount FROM product_price pp WHERE pp.spec_id=s.id AND pp.price_type='LIST' AND pp.status='ACTIVE'
                   AND pp.valid_from<=CURRENT_TIMESTAMP(3) AND (pp.valid_to IS NULL OR pp.valid_to>CURRENT_TIMESTAMP(3))
                   ORDER BY pp.valid_from DESC,pp.id DESC LIMIT 1) AS market_price,
                  (SELECT pp.currency FROM product_price pp WHERE pp.spec_id=s.id AND pp.price_type='SALE' AND pp.status='ACTIVE'
                   AND pp.valid_from<=CURRENT_TIMESTAMP(3) AND (pp.valid_to IS NULL OR pp.valid_to>CURRENT_TIMESTAMP(3))
                   ORDER BY pp.valid_from DESC,pp.id DESC LIMIT 1) AS currency,
                  CASE WHEN i.id IS NULL THEN NULL ELSE GREATEST(i.available_qty-i.locked_qty,0) END AS stock_quantity,
                  CASE WHEN i.id IS NULL THEN NULL WHEN i.available_qty-i.locked_qty>0 THEN 1 ELSE 0 END AS sellable
                FROM product_spec s LEFT JOIN product_inventory i ON i.spec_id=s.id AND i.warehouse_code='DEFAULT'
                WHERE s.product_id=:id AND s.status='ACTIVE' ORDER BY s.is_default DESC,s.id
            """, product_id)
            images = self._rows(session, "SELECT image_type,image_url,alt_text,sort_order FROM product_image WHERE product_id=:id AND status='ACTIVE' ORDER BY sort_order,id", product_id)
            nutrition = self._rows(session, "SELECT nutrient_code,nutrient_name,nutrient_value AS value,unit,basis,basis_quantity,source_code FROM product_nutrition WHERE product_id=:id AND audit_status='APPROVED' ORDER BY id", product_id)
            ingredients = self._rows(session, """
                SELECT entity_code,normalized_name AS name,entity_type,relation_type,confidence,source_code,audit_status
                FROM product_ingredient_snapshot WHERE product_id=:id AND effective_to IS NULL
                  AND version_no=(SELECT MAX(v.version_no) FROM product_ingredient_snapshot v WHERE v.product_id=:id AND v.effective_to IS NULL)
                  AND audit_status='APPROVED' AND relation_type IN ('CONTAINS','MAY_CONTAIN')
                ORDER BY relation_type,entity_code
            """, product_id)
            result = dict(base)
            result["merchant"] = {"merchant_code": result.pop("merchant_code"), "name": result.pop("merchant_name")}
            result.update(specs=specs, images=images, nutrition=nutrition,
                          contains=[x for x in ingredients if x["relation_type"] == "CONTAINS"],
                          may_contain=[x for x in ingredients if x["relation_type"] == "MAY_CONTAIN"])
            return result

    @staticmethod
    def _rows(session: Session, sql: str, product_id: int) -> list[dict[str, Any]]:
        return [dict(row) for row in session.execute(text(sql), {"id": product_id}).mappings().all()]
