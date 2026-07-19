// Compatibility target: Neo4j 2026.06.0. Run verify.cypher after importing the graph.
CREATE CONSTRAINT food_product_code_unique IF NOT EXISTS
FOR (n:FoodProduct) REQUIRE n.product_code IS UNIQUE;

CREATE CONSTRAINT ingredient_code_unique IF NOT EXISTS
FOR (n:Ingredient) REQUIRE n.ingredient_code IS UNIQUE;

CREATE CONSTRAINT additive_code_unique IF NOT EXISTS
FOR (n:Additive) REQUIRE n.additive_code IS UNIQUE;

CREATE CONSTRAINT nutrient_code_unique IF NOT EXISTS
FOR (n:Nutrient) REQUIRE n.nutrient_code IS UNIQUE;

CREATE CONSTRAINT brand_code_unique IF NOT EXISTS
FOR (n:Brand) REQUIRE n.brand_code IS UNIQUE;

CREATE CONSTRAINT category_code_unique IF NOT EXISTS
FOR (n:Category) REQUIRE n.category_code IS UNIQUE;

CREATE CONSTRAINT risk_tag_code_unique IF NOT EXISTS
FOR (n:RiskTag) REQUIRE n.risk_tag_code IS UNIQUE;

CREATE CONSTRAINT data_source_code_unique IF NOT EXISTS
FOR (n:DataSource) REQUIRE n.source_code IS UNIQUE;

CREATE INDEX food_product_name_index IF NOT EXISTS
FOR (n:FoodProduct) ON (n.name);

CREATE INDEX food_product_audit_status_index IF NOT EXISTS
FOR (n:FoodProduct) ON (n.audit_status);

CREATE INDEX ingredient_standard_name_index IF NOT EXISTS
FOR (n:Ingredient) ON (n.standard_name);

CREATE INDEX ingredient_audit_status_index IF NOT EXISTS
FOR (n:Ingredient) ON (n.audit_status);

CREATE INDEX additive_standard_name_index IF NOT EXISTS
FOR (n:Additive) ON (n.standard_name);

CREATE INDEX brand_name_index IF NOT EXISTS
FOR (n:Brand) ON (n.name);

CREATE INDEX category_name_index IF NOT EXISTS
FOR (n:Category) ON (n.name);
