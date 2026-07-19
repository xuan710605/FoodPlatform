// Neo4j 5.x query examples. Set parameters in Neo4j Browser before running, e.g.:
// :param product_code => 'FP0001';
// :param ingredient_code => 'ING002';

// 1. Query every explicit ingredient of a product.
MATCH (p:FoodProduct {product_code: $product_code})
MATCH (p)-[r:FOOD_PRODUCT_CONTAINS_INGREDIENT]->(i:Ingredient)
RETURN p.product_code, p.name, i.ingredient_code, i.standard_name,
       r.raw_fragment, r.confidence, r.source_code, r.audit_status
ORDER BY r.sequence, i.standard_name;

// 2. Determine whether a product explicitly contains a specified ingredient,
// including aliases and derived ingredients. Returns deterministic evidence.
MATCH (p:FoodProduct {product_code: $product_code})
MATCH (target:Ingredient {ingredient_code: $ingredient_code})
OPTIONAL MATCH path=(p)-[:FOOD_PRODUCT_CONTAINS_INGREDIENT]->(actual:Ingredient)
  -[:INGREDIENT_ALIAS_OF|INGREDIENT_DERIVED_FROM*0..3]->(target)
RETURN p.product_code, target.ingredient_code,
       CASE WHEN path IS NULL THEN false ELSE true END AS explicitly_contains,
       [n IN nodes(path) | coalesce(n.product_code, n.ingredient_code)] AS evidence_path;

// 3. Query aliases of an ingredient.
MATCH (alias:Ingredient)-[r:INGREDIENT_ALIAS_OF]->(standard:Ingredient {ingredient_code: $ingredient_code})
RETURN alias.ingredient_code, alias.standard_name, r.source_code, r.audit_status;

// 4. Query direct and transitive derivatives of an ingredient.
MATCH path=(derived:Ingredient)-[:INGREDIENT_DERIVED_FROM*1..4]->(base:Ingredient {ingredient_code: $ingredient_code})
RETURN derived.ingredient_code, derived.standard_name, length(path) AS depth,
       [rel IN relationships(path) | rel.source_code] AS sources
ORDER BY depth, derived.standard_name;

// 5. Query risk tags associated with an ingredient.
MATCH (i:Ingredient {ingredient_code: $ingredient_code})-[r:INGREDIENT_HAS_RISK]->(risk:RiskTag)
RETURN i.standard_name, risk.risk_tag_code, risk.name, risk.severity,
       r.source_code, r.audit_status;

// 6. Query products that do not explicitly contain or possibly contain an ingredient
// or any audited aliases/derivatives. This is not an absolute safety guarantee.
MATCH (p:FoodProduct)
WHERE p.audit_status = 'APPROVED'
  AND NOT EXISTS {
    MATCH (p)-[:FOOD_PRODUCT_CONTAINS_INGREDIENT|FOOD_PRODUCT_MAY_CONTAIN]->(actual:Ingredient)
    MATCH (target:Ingredient {ingredient_code: $ingredient_code})
    WHERE actual = target
       OR EXISTS { MATCH (actual)-[:INGREDIENT_ALIAS_OF|INGREDIENT_DERIVED_FROM*1..3]->(target) }
  }
RETURN p.product_code, p.name, p.match_status
ORDER BY p.product_code;

// 7. Query products carrying a may-contain warning for an ingredient.
MATCH (p:FoodProduct)-[r:FOOD_PRODUCT_MAY_CONTAIN]->(i:Ingredient {ingredient_code: $ingredient_code})
RETURN p.product_code, p.name, r.raw_fragment, r.source_code, r.audit_status;

// 8. Query substitute ingredients in either direction.
MATCH (i:Ingredient {ingredient_code: $ingredient_code})-[r:INGREDIENT_CAN_SUBSTITUTE]-(substitute:Ingredient)
RETURN substitute.ingredient_code, substitute.standard_name,
       r.context, r.source_code, r.audit_status;

// 9. Query complete paths from a product to risk tags.
MATCH path=(p:FoodProduct {product_code: $product_code})
  -[:FOOD_PRODUCT_CONTAINS_INGREDIENT|FOOD_PRODUCT_MAY_CONTAIN|FOOD_PRODUCT_HAS_ADDITIVE]->(entity)
  -[:INGREDIENT_HAS_RISK*1..2]->(risk:RiskTag)
RETURN path, [n IN nodes(path) | coalesce(n.name, n.standard_name)] AS readable_path;

// 10. Query all one-hop graph relations of a product.
MATCH (p:FoodProduct {product_code: $product_code})-[r]-(neighbor)
RETURN type(r) AS relation_type, properties(r) AS relation_properties,
       labels(neighbor) AS neighbor_labels, properties(neighbor) AS neighbor_properties
ORDER BY relation_type;

// 11. Query products affected by a changed ingredient relation.
MATCH (changed:Ingredient {ingredient_code: $ingredient_code})
MATCH path=(p:FoodProduct)-[:FOOD_PRODUCT_CONTAINS_INGREDIENT|FOOD_PRODUCT_MAY_CONTAIN]->(used:Ingredient)
  -[:INGREDIENT_ALIAS_OF|INGREDIENT_DERIVED_FROM*0..4]->(changed)
RETURN DISTINCT p.product_code, p.name, p.audit_status,
       [n IN nodes(path) | coalesce(n.product_code, n.ingredient_code)] AS impact_path
ORDER BY p.product_code;
