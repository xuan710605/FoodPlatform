// FoodPlatform query examples. Compatibility target: Neo4j 2026.06.0.
// Supply parameters with cypher-shell (-P) or the application. Never use internal node IDs as business identifiers.

// 1. Explicit ingredients. raw_fragment remains in MySQL and is not fabricated in the graph.
MATCH (p:FoodProduct {product_code: $product_code})
MATCH (p)-[r:FOOD_PRODUCT_CONTAINS_INGREDIENT]->(i:Ingredient)
RETURN p.product_code, p.name, i.ingredient_code,
       coalesce(i.standard_name, i.name) AS ingredient_name,
       r.confidence, r.source_code, r.audit_status
ORDER BY i.ingredient_code;

// 2. Approved explicit-containment evidence. A false result is not an absolute safety guarantee.
MATCH (p:FoodProduct {product_code: $product_code})
MATCH (target:Ingredient {ingredient_code: $ingredient_code})
OPTIONAL MATCH path=(p)-[:FOOD_PRODUCT_CONTAINS_INGREDIENT]->(actual:Ingredient)
  -[:INGREDIENT_ALIAS_OF|INGREDIENT_DERIVED_FROM*0..3]->(target)
WHERE ALL(rel IN relationships(path) WHERE rel.audit_status = 'APPROVED')
RETURN p.product_code, target.ingredient_code,
       path IS NOT NULL AS explicitly_contains,
       CASE WHEN path IS NULL THEN 'NO_RECORDED_APPROVED_PATH' ELSE 'APPROVED_EVIDENCE_PATH' END AS evidence_status,
       CASE WHEN path IS NULL THEN [] ELSE [n IN nodes(path) | coalesce(n.product_code, n.ingredient_code)] END AS evidence_path;

// 3. Approved aliases and their evidence source.
MATCH (alias:Ingredient)-[r:INGREDIENT_ALIAS_OF]->(standard:Ingredient {ingredient_code: $ingredient_code})
RETURN alias.ingredient_code, coalesce(alias.standard_name, alias.name) AS alias_name,
       standard.ingredient_code, coalesce(standard.standard_name, standard.name) AS standard_name,
       r.source_code, r.audit_status
ORDER BY alias.ingredient_code;

// 4. Approved direct/transitive derivatives and evidence per edge.
MATCH path=(derived:Ingredient)-[:INGREDIENT_DERIVED_FROM*1..4]->(base:Ingredient {ingredient_code: $ingredient_code})
WHERE ALL(rel IN relationships(path) WHERE rel.audit_status = 'APPROVED')
RETURN derived.ingredient_code, coalesce(derived.standard_name, derived.name) AS derived_name,
       length(path) AS depth,
       [rel IN relationships(path) | {source_code: rel.source_code, audit_status: rel.audit_status}] AS evidence
ORDER BY depth, derived.ingredient_code;

// 5. Risk tags use the canonical risk_level property.
MATCH (i:Ingredient {ingredient_code: $ingredient_code})-[r:INGREDIENT_HAS_RISK]->(risk:RiskTag)
RETURN i.ingredient_code, coalesce(i.standard_name, i.name) AS ingredient_name,
       risk.risk_tag_code, risk.name, risk.risk_level,
       r.source_code, r.audit_status
ORDER BY risk.risk_tag_code;

// 6. No recorded explicit/may-contain relation is information absence, not an absolute safety assertion.
MATCH (target:Ingredient {ingredient_code: $ingredient_code})
MATCH (p:FoodProduct)
WHERE p.audit_status = 'APPROVED'
  AND NOT EXISTS {
    MATCH (p)-[:FOOD_PRODUCT_CONTAINS_INGREDIENT|FOOD_PRODUCT_MAY_CONTAIN]->(actual:Ingredient)
    WHERE actual = target
       OR EXISTS {
         MATCH path=(actual)-[:INGREDIENT_ALIAS_OF|INGREDIENT_DERIVED_FROM*1..3]->(target)
         WHERE ALL(rel IN relationships(path) WHERE rel.audit_status = 'APPROVED')
       }
  }
RETURN p.product_code, p.name, 'NO_RECORDED_RELATION' AS knowledge_result,
       false AS absolute_safety_guarantee
ORDER BY p.product_code;

// 7. A may-contain warning is distinct from confirmed containment.
MATCH (p:FoodProduct)-[r:FOOD_PRODUCT_MAY_CONTAIN]->(i:Ingredient {ingredient_code: $ingredient_code})
RETURN p.product_code, p.name, i.ingredient_code,
       coalesce(i.standard_name, i.name) AS ingredient_name,
       r.confidence, r.source_code, r.audit_status
ORDER BY p.product_code;

// 8. Substitute ingredients use the canonical context property.
MATCH (i:Ingredient {ingredient_code: $ingredient_code})-[r:INGREDIENT_CAN_SUBSTITUTE]-(substitute:Ingredient)
RETURN substitute.ingredient_code, coalesce(substitute.standard_name, substitute.name) AS substitute_name,
       r.context, r.source_code, r.audit_status
ORDER BY substitute.ingredient_code;

// 9. Explainable paths from a product to risk tags.
MATCH path=(p:FoodProduct {product_code: $product_code})
  -[:FOOD_PRODUCT_CONTAINS_INGREDIENT|FOOD_PRODUCT_MAY_CONTAIN]->(ingredient:Ingredient)
  -[:INGREDIENT_HAS_RISK]->(risk:RiskTag)
RETURN path,
       [n IN nodes(path) | coalesce(n.product_code, n.ingredient_code, n.risk_tag_code)] AS business_path,
       [n IN nodes(path) | coalesce(n.standard_name, n.name)] AS readable_path;

// 10. All one-hop product relations.
MATCH (p:FoodProduct {product_code: $product_code})-[r]-(neighbor)
RETURN type(r) AS relation_type, properties(r) AS relation_properties,
       labels(neighbor) AS neighbor_labels, properties(neighbor) AS neighbor_properties
ORDER BY relation_type;

// 11. Products affected by an approved changed ingredient relation.
MATCH (changed:Ingredient {ingredient_code: $ingredient_code})
MATCH path=(p:FoodProduct)-[:FOOD_PRODUCT_CONTAINS_INGREDIENT|FOOD_PRODUCT_MAY_CONTAIN]->(used:Ingredient)
  -[:INGREDIENT_ALIAS_OF|INGREDIENT_DERIVED_FROM*0..4]->(changed)
WHERE ALL(rel IN relationships(path) WHERE rel.audit_status = 'APPROVED')
RETURN DISTINCT p.product_code, p.name, p.audit_status,
       [n IN nodes(path) | coalesce(n.product_code, n.ingredient_code)] AS impact_path
ORDER BY p.product_code;