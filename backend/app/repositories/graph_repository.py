from typing import Any

from neo4j import Driver


DIRECT_QUERY = """
MATCH (p:FoodProduct {product_code: $product_code})
OPTIONAL MATCH (p)-[r]->(n)
WHERE type(r) IN [
  'FOOD_PRODUCT_CONTAINS_INGREDIENT','FOOD_PRODUCT_MAY_CONTAIN',
  'FOOD_PRODUCT_HAS_ADDITIVE','FOOD_PRODUCT_HAS_NUTRIENT',
  'FOOD_PRODUCT_BELONGS_TO_BRAND','FOOD_PRODUCT_BELONGS_TO_CATEGORY','ENTITY_FROM_SOURCE'
]
RETURN p.product_code AS product_code, p.name AS product_name,
       labels(n)[0] AS target_type,
       coalesce(n.ingredient_code,n.additive_code,n.nutrient_code,n.brand_code,
                n.category_code,n.risk_tag_code,n.source_code) AS target_code,
       coalesce(n.standard_name,n.name) AS target_name,
       n.risk_level AS risk_level, type(r) AS relation_type,
       r.confidence AS confidence, r.source_code AS source_code, r.audit_status AS audit_status
LIMIT $limit
"""

RISK_QUERY = """
MATCH (p:FoodProduct {product_code: $product_code})-[pr]->(i:Ingredient)-[rr:INGREDIENT_HAS_RISK]->(risk:RiskTag)
WHERE type(pr) IN ['FOOD_PRODUCT_CONTAINS_INGREDIENT','FOOD_PRODUCT_MAY_CONTAIN']
RETURN i.ingredient_code AS ingredient_code,
       coalesce(i.standard_name,i.name) AS ingredient_name,
       risk.risk_tag_code AS risk_code, risk.name AS risk_name, risk.risk_level AS risk_level,
       rr.confidence AS confidence, rr.source_code AS source_code, rr.audit_status AS audit_status
LIMIT $limit
"""


class GraphRepository:
    def __init__(self, driver: Driver, database: str):
        self._driver = driver
        self._database = database

    def get_product_graph(self, product_code: str, limit: int = 200) -> dict[str, Any] | None:
        with self._driver.session(database=self._database) as session:
            direct = [record.data() for record in session.run(DIRECT_QUERY, product_code=product_code, limit=limit)]
            if not direct:
                return None
            risks = [record.data() for record in session.run(RISK_QUERY, product_code=product_code, limit=limit)]
        return self._to_cytoscape(direct, risks)

    @staticmethod
    def _to_cytoscape(direct: list[dict[str, Any]], risks: list[dict[str, Any]]) -> dict[str, Any]:
        product_code = direct[0]["product_code"]
        product_id = f"FoodProduct:{product_code}"
        nodes: dict[str, dict[str, Any]] = {
            product_id: {"data": {"id": product_id, "type": "FoodProduct", "business_code": product_code, "label": direct[0]["product_name"]}}
        }
        edges: dict[str, dict[str, Any]] = {}
        contains = may_contain = 0
        for row in direct:
            if not row.get("target_code") or not row.get("relation_type"):
                continue
            target_id = f"{row['target_type']}:{row['target_code']}"
            nodes[target_id] = {"data": {"id": target_id, "type": row["target_type"], "business_code": row["target_code"], "label": row["target_name"], "risk_level": row.get("risk_level")}}
            edge_id = f"{product_id}->{target_id}:{row['relation_type']}"
            edges[edge_id] = {"data": {"id": edge_id, "source": product_id, "target": target_id, "type": row["relation_type"], "confidence": row.get("confidence"), "source_code": row.get("source_code"), "audit_status": row.get("audit_status")}}
            contains += row["relation_type"] == "FOOD_PRODUCT_CONTAINS_INGREDIENT"
            may_contain += row["relation_type"] == "FOOD_PRODUCT_MAY_CONTAIN"
        for row in risks:
            source_id = f"Ingredient:{row['ingredient_code']}"
            risk_id = f"RiskTag:{row['risk_code']}"
            nodes.setdefault(source_id, {"data": {"id": source_id, "type": "Ingredient", "business_code": row["ingredient_code"], "label": row["ingredient_name"]}})
            nodes[risk_id] = {"data": {"id": risk_id, "type": "RiskTag", "business_code": row["risk_code"], "label": row["risk_name"], "risk_level": row.get("risk_level")}}
            edge_id = f"{source_id}->{risk_id}:INGREDIENT_HAS_RISK"
            edges[edge_id] = {"data": {"id": edge_id, "source": source_id, "target": risk_id, "type": "INGREDIENT_HAS_RISK", "confidence": row.get("confidence"), "source_code": row.get("source_code"), "audit_status": row.get("audit_status")}}
        information_status = "SUFFICIENT" if contains or may_contain else "INSUFFICIENT"
        return {"nodes": list(nodes.values()), "edges": list(edges.values()), "summary": {"contains_count": contains, "may_contain_count": may_contain, "risk_count": len({r['risk_code'] for r in risks}), "information_status": information_status}}
