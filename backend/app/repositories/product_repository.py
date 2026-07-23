from collections.abc import Mapping
from typing import Any

from sqlalchemy import bindparam, text
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
        where.append("p.sale_status=:status" if filters.get("status") else "p.sale_status='ON_SALE'")
        if filters.get("status"): params["status"] = filters["status"]
        for field,column in (("category_code","c.category_code"),("category","c.category_name"),("brand_code","b.brand_code"),("brand","b.brand_name"),("merchant_id","p.merchant_id")):
            if filters.get(field) is not None: where.append(f"{column}=:{field}");params[field]=filters[field]
        if filters.get("keyword"):
            where.append("(p.product_name LIKE :keyword OR p.product_code LIKE :keyword)");params["keyword"]=f"%{filters['keyword']}%"
        sale_price = "(SELECT pp.amount FROM product_price pp WHERE pp.spec_id=s.id AND pp.price_type='SALE' AND pp.status='ACTIVE' AND pp.valid_from<=CURRENT_TIMESTAMP(3) AND (pp.valid_to IS NULL OR pp.valid_to>CURRENT_TIMESTAMP(3)) ORDER BY pp.valid_from DESC,pp.id DESC LIMIT 1)"
        for key,operator in (("price_min",">="),("price_max","<=")):
            if filters.get(key) is not None:where.append(f"{sale_price} {operator} :{key}");params[key]=filters[key]
        for index,name in enumerate(filters.get("excluded_ingredients") or []):
            key=f"excluded_{index}";where.append(f"NOT EXISTS (SELECT 1 FROM product_ingredient_snapshot pis WHERE pis.product_id=p.id AND pis.effective_to IS NULL AND pis.version_no=(SELECT MAX(pv.version_no) FROM product_ingredient_snapshot pv WHERE pv.product_id=p.id AND pv.effective_to IS NULL) AND pis.audit_status='APPROVED' AND pis.relation_type IN ('CONTAINS','MAY_CONTAIN') AND pis.normalized_name LIKE :{key})");params[key]=f"%{name}%"
        nutrients=(("sugar_max","NUT_SUGAR","<="),("fat_max","NUT_FAT","<="),("protein_min","NUT_PROTEIN",">="),("sodium_max","NUT_SODIUM","<="))
        for key,code,operator in nutrients:
            if filters.get(key) is not None:where.append(f"EXISTS (SELECT 1 FROM product_nutrition pn WHERE pn.product_id=p.id AND pn.nutrient_code='{code}' AND pn.audit_status='APPROVED' AND pn.nutrient_value {operator} :{key})");params[key]=filters[key]
        predicate=" AND ".join(where);sort_column=SORT_COLUMNS[filters["sort_by"]];sort_order="DESC" if filters["sort_order"]=="desc" else "ASC"
        params.update(limit=filters["page_size"],offset=(filters["page"]-1)*filters["page_size"])
        base="""FROM product p JOIN brand b ON b.id=p.brand_id JOIN category c ON c.id=p.category_id JOIN merchant m ON m.id=p.merchant_id LEFT JOIN product_spec s ON s.product_id=p.id AND s.is_default=1 AND s.status='ACTIVE' LEFT JOIN product_inventory inv ON inv.spec_id=s.id AND inv.warehouse_code='DEFAULT'"""
        query=text(f"""SELECT p.id,p.product_code,p.product_name name,p.subtitle,b.brand_name brand,b.brand_code,c.category_name category,c.category_code,m.merchant_name merchant,p.merchant_id,(SELECT AVG(pr.rating) FROM product_review pr WHERE pr.product_id=p.id AND pr.status='PUBLISHED') average_rating,(SELECT COUNT(*) FROM product_review pr WHERE pr.product_id=p.id AND pr.status='PUBLISHED') review_count,(SELECT COALESCE(SUM(oi.quantity),0) FROM order_item oi JOIN order_info o ON o.id=oi.order_id WHERE oi.product_id=p.id AND o.order_status NOT IN ('CANCELLED','PENDING_PAYMENT')) sales_count,(SELECT pi.image_url FROM product_image pi WHERE pi.product_id=p.id AND pi.image_type='MAIN' AND pi.status='ACTIVE' ORDER BY pi.sort_order,pi.id LIMIT 1) main_image_url,{sale_price} sale_price,(SELECT pp.amount FROM product_price pp WHERE pp.spec_id=s.id AND pp.price_type='LIST' AND pp.status='ACTIVE' AND pp.valid_from<=CURRENT_TIMESTAMP(3) AND (pp.valid_to IS NULL OR pp.valid_to>CURRENT_TIMESTAMP(3)) ORDER BY pp.valid_from DESC,pp.id DESC LIMIT 1) market_price,CASE WHEN inv.id IS NULL THEN NULL ELSE GREATEST(inv.available_qty-inv.locked_qty,0) END stock_quantity,CASE WHEN inv.id IS NULL THEN NULL WHEN inv.available_qty-inv.locked_qty>0 THEN 1 ELSE 0 END sellable,p.review_status audit_status,p.sale_status,(SELECT MAX(psn.version_no) FROM product_ingredient_snapshot psn WHERE psn.product_id=p.id AND psn.effective_to IS NULL) ingredient_version,p.created_at,p.updated_at {base} WHERE {predicate} ORDER BY {sort_column} {sort_order},p.id ASC LIMIT :limit OFFSET :offset""")
        with self._factory() as session:
            total = session.execute(text(f"SELECT COUNT(DISTINCT p.id) {base} WHERE {predicate}"), params).scalar_one()
            rows = session.execute(query, params).mappings().all()
            items = [dict(row) for row in rows]
            self._attach_ingredient_summaries(session, items)
            return int(total), items

    @staticmethod
    def _attach_ingredient_summaries(session: Session, items: list[dict[str, Any]]) -> None:
        for item in items:
            item.update(contains=[], may_contain=[], unknown=[])
        if not items:
            return
        statement = text("""
            SELECT pis.product_id,pis.entity_code,pis.normalized_name AS name,pis.entity_type,
              pis.relation_type,pis.confidence,pis.source_code,pis.audit_status
            FROM product_ingredient_snapshot pis
            WHERE pis.product_id IN :product_ids AND pis.effective_to IS NULL
              AND pis.version_no=(SELECT MAX(v.version_no) FROM product_ingredient_snapshot v
                                  WHERE v.product_id=pis.product_id AND v.effective_to IS NULL)
              AND pis.audit_status='APPROVED'
              AND pis.relation_type IN ('CONTAINS','MAY_CONTAIN','UNKNOWN')
            ORDER BY pis.product_id,pis.relation_type,pis.entity_code
        """).bindparams(bindparam("product_ids", expanding=True))
        grouped = {item["id"]: item for item in items}
        relation_keys = {"CONTAINS": "contains", "MAY_CONTAIN": "may_contain", "UNKNOWN": "unknown"}
        for row in session.execute(statement, {"product_ids": list(grouped)}).mappings():
            product = grouped.get(row["product_id"])
            if product is None:
                continue
            summary = dict(row)
            summary.pop("product_id")
            product[relation_keys[row["relation_type"]]].append(summary)
    def category_stats(self) -> list[dict[str, Any]]:
        with self._factory() as session:
            rows=session.execute(text("""SELECT c.category_code,c.category_name,COUNT(p.id) product_count FROM category c LEFT JOIN product p ON p.category_id=c.id AND p.is_deleted=0 AND p.review_status='APPROVED' AND p.sale_status='ON_SALE' WHERE c.status='ACTIVE' GROUP BY c.id,c.category_code,c.category_name,c.sort_order ORDER BY c.sort_order,c.id""")).mappings().all()
            return [dict(row) for row in rows]

    def get_detail(self, product_code: str) -> dict[str, Any] | None:
        with self._factory() as session:
            base = session.execute(text("""
                SELECT p.id,p.product_code,p.product_name AS name,p.subtitle,p.description,
                  b.brand_name AS brand,b.brand_code,c.category_name AS category,c.category_code,
                  m.merchant_code,m.merchant_name,p.raw_ingredient_text,p.allergen_notice,
                  p.match_status,p.match_reason,p.evidence_text,p.info_source,
                  (SELECT COALESCE(SUM(oi.quantity),0)
                   FROM order_item oi JOIN order_info o ON o.id=oi.order_id
                   WHERE oi.product_id=p.id
                     AND o.order_status NOT IN ('CANCELLED','PENDING_PAYMENT')) AS sales_count,
                  (SELECT AVG(pr.rating) FROM product_review pr
                   WHERE pr.product_id=p.id AND pr.status='PUBLISHED') AS average_rating,
                  (SELECT COUNT(*) FROM product_review pr
                   WHERE pr.product_id=p.id AND pr.status='PUBLISHED') AS review_count,
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
                  AND audit_status='APPROVED' AND relation_type IN ('CONTAINS','MAY_CONTAIN','UNKNOWN')
                ORDER BY relation_type,entity_code
            """, product_id)
            result = dict(base)
            result["merchant"] = {"merchant_code": result.pop("merchant_code"), "name": result.pop("merchant_name")}
            result.update(specs=specs, images=images, nutrition=nutrition,
                          contains=[x for x in ingredients if x["relation_type"] == "CONTAINS"],
                          may_contain=[x for x in ingredients if x["relation_type"] == "MAY_CONTAIN"],
                          unknown=[x for x in ingredients if x["relation_type"] == "UNKNOWN"])
            return result

    @staticmethod
    def _rows(session: Session, sql: str, product_id: int) -> list[dict[str, Any]]:
        return [dict(row) for row in session.execute(text(sql), {"id": product_id}).mappings().all()]
