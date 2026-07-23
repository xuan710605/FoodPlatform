from typing import Any

from neo4j import Driver


RESOLVE_QUERY = """
MATCH (root:Ingredient)
WHERE root.audit_status = 'APPROVED'
  AND (toLower(root.name) = toLower($term) OR toLower(root.standard_name) = toLower($term))
OPTIONAL MATCH (alias:Ingredient)-[ar:INGREDIENT_ALIAS_OF]->(root)
WHERE ar.audit_status = 'APPROVED'
OPTIONAL MATCH (derived:Ingredient)-[dr:INGREDIENT_DERIVED_FROM*1..3]->(root)
WHERE all(rel IN dr WHERE rel.audit_status = 'APPROVED')
WITH root, collect(DISTINCT alias) + collect(DISTINCT derived) AS related
UNWIND [root] + related AS ingredient
WITH DISTINCT ingredient WHERE ingredient IS NOT NULL
OPTIONAL MATCH (ingredient)-[risk_rel:INGREDIENT_HAS_RISK]->(risk:RiskTag)
WHERE risk_rel.audit_status = 'APPROVED'
RETURN ingredient.ingredient_code AS ingredient_code,
       coalesce(ingredient.standard_name, ingredient.name) AS ingredient_name,
       collect(DISTINCT {risk_tag_code:risk.risk_tag_code,name:risk.name,risk_level:risk.risk_level}) AS risks
"""


class FilterGraphRepository:
    def __init__(self, driver: Driver, database: str):
        self._driver = driver
        self._database = database

    def resolve_exclusions(self, terms: list[str]) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = {}
        with self._driver.session(database=self._database) as session:
            for term in terms:
                result[term] = [record.data() for record in session.run(RESOLVE_QUERY, term=term)]
        return result