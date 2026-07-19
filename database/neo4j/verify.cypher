// Read-only verification for cypher-shell. Compatibility target: Neo4j 2026.06.0.
// init-database.ps1 treats any result containing FAIL as a fatal validation error.

CALL dbms.components() YIELD name, versions, edition
RETURN 'neo4j_version' AS check_name, name AS component, versions[0] AS actual, edition, 'INFO' AS status;

MATCH (n:FoodProduct) RETURN 'FoodProduct_count' AS check_name, count(n) AS actual, 20 AS expected, CASE WHEN count(n)=20 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Ingredient) RETURN 'Ingredient_count' AS check_name, count(n) AS actual, 64 AS expected, CASE WHEN count(n)=64 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Additive) RETURN 'Additive_count' AS check_name, count(n) AS actual, 11 AS expected, CASE WHEN count(n)=11 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Nutrient) RETURN 'Nutrient_count' AS check_name, count(n) AS actual, 10 AS expected, CASE WHEN count(n)=10 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Brand) RETURN 'Brand_count' AS check_name, count(n) AS actual, 15 AS expected, CASE WHEN count(n)=15 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Category) RETURN 'Category_count' AS check_name, count(n) AS actual, 10 AS expected, CASE WHEN count(n)=10 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:RiskTag) RETURN 'RiskTag_count' AS check_name, count(n) AS actual, 12 AS expected, CASE WHEN count(n)=12 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:DataSource) RETURN 'DataSource_count' AS check_name, count(n) AS actual, 5 AS expected, CASE WHEN count(n)=5 THEN 'PASS' ELSE 'FAIL' END AS status;

MATCH (n)
WHERE n:FoodProduct OR n:Ingredient OR n:Additive OR n:Nutrient OR n:Brand OR n:Category OR n:RiskTag OR n:DataSource
RETURN 'total_project_nodes' AS check_name, count(n) AS actual, 147 AS expected,
       CASE WHEN count(n)=147 THEN 'PASS' ELSE 'FAIL' END AS status;

MATCH ()-[r]->()
RETURN type(r) AS relationship_type, count(r) AS actual, 'INFO' AS status
ORDER BY relationship_type;

MATCH (n:FoodProduct)
WITH count(n) AS total, count(DISTINCT n.product_code) AS distinct_codes,
     count(CASE WHEN n.product_code IS NULL OR trim(n.product_code)='' THEN 1 END) AS missing_codes
RETURN 'FoodProduct_business_codes' AS check_name, total, distinct_codes, missing_codes,
       CASE WHEN total=distinct_codes AND missing_codes=0 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Ingredient)
WITH count(n) AS total, count(DISTINCT n.ingredient_code) AS distinct_codes,
     count(CASE WHEN n.ingredient_code IS NULL OR trim(n.ingredient_code)='' THEN 1 END) AS missing_codes
RETURN 'Ingredient_business_codes' AS check_name, total, distinct_codes, missing_codes, CASE WHEN total=distinct_codes AND missing_codes=0 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Additive)
WITH count(n) AS total, count(DISTINCT n.additive_code) AS distinct_codes,
     count(CASE WHEN n.additive_code IS NULL OR trim(n.additive_code)='' THEN 1 END) AS missing_codes
RETURN 'Additive_business_codes' AS check_name, total, distinct_codes, missing_codes, CASE WHEN total=distinct_codes AND missing_codes=0 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Brand)
WITH count(n) AS total, count(DISTINCT n.brand_code) AS distinct_codes,
     count(CASE WHEN n.brand_code IS NULL OR trim(n.brand_code)='' THEN 1 END) AS missing_codes
RETURN 'Brand_business_codes' AS check_name, total, distinct_codes, missing_codes, CASE WHEN total=distinct_codes AND missing_codes=0 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Category)
WITH count(n) AS total, count(DISTINCT n.category_code) AS distinct_codes,
     count(CASE WHEN n.category_code IS NULL OR trim(n.category_code)='' THEN 1 END) AS missing_codes
RETURN 'Category_business_codes' AS check_name, total, distinct_codes, missing_codes, CASE WHEN total=distinct_codes AND missing_codes=0 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:Nutrient)
WITH count(n) AS total, count(DISTINCT n.nutrient_code) AS distinct_codes,
     count(CASE WHEN n.nutrient_code IS NULL OR trim(n.nutrient_code)='' THEN 1 END) AS missing_codes
RETURN 'Nutrient_business_codes' AS check_name, total, distinct_codes, missing_codes, CASE WHEN total=distinct_codes AND missing_codes=0 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:RiskTag)
WITH count(n) AS total, count(DISTINCT n.risk_tag_code) AS distinct_codes,
     count(CASE WHEN n.risk_tag_code IS NULL OR trim(n.risk_tag_code)='' THEN 1 END) AS missing_codes
RETURN 'RiskTag_business_codes' AS check_name, total, distinct_codes, missing_codes, CASE WHEN total=distinct_codes AND missing_codes=0 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (n:DataSource)
WITH count(n) AS total, count(DISTINCT n.source_code) AS distinct_codes,
     count(CASE WHEN n.source_code IS NULL OR trim(n.source_code)='' THEN 1 END) AS missing_codes
RETURN 'DataSource_business_codes' AS check_name, total, distinct_codes, missing_codes, CASE WHEN total=distinct_codes AND missing_codes=0 THEN 'PASS' ELSE 'FAIL' END AS status;

MATCH (:FoodProduct {product_code:'FP0017'})-[r:FOOD_PRODUCT_CONTAINS_INGREDIENT]->(:Ingredient {ingredient_code:'ING004'})
RETURN 'FP0017_contains_ING004' AS check_name, count(r) AS actual, 1 AS expected, CASE WHEN count(r)=1 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH (:FoodProduct {product_code:'FP0002'})-[r:FOOD_PRODUCT_MAY_CONTAIN]->(:Ingredient {ingredient_code:'ING002'})
RETURN 'FP0002_may_contain_ING002' AS check_name, count(r) AS actual, 1 AS expected, CASE WHEN count(r)=1 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH path=(:Ingredient {ingredient_code:'ING004'})-[:INGREDIENT_DERIVED_FROM*1..4]->(:Ingredient {ingredient_code:'ING002'})
RETURN 'ING004_derived_from_ING002' AS check_name, count(path) AS actual, 1 AS expected, CASE WHEN count(path)>=1 THEN 'PASS' ELSE 'FAIL' END AS status
UNION ALL MATCH path=(:FoodProduct {product_code:'FP0017'})-[:FOOD_PRODUCT_CONTAINS_INGREDIENT]->(:Ingredient)-[:INGREDIENT_HAS_RISK]->(:RiskTag {risk_tag_code:'RISK001'})
RETURN 'FP0017_to_RISK001_explainable_path' AS check_name, count(path) AS actual, 1 AS expected, CASE WHEN count(path)>=1 THEN 'PASS' ELSE 'FAIL' END AS status;

SHOW CONSTRAINTS;
SHOW INDEXES;