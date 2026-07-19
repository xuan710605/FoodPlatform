// Delete only graph data in the selected application database.
// Constraints, indexes, users and the system database are not removed.
MATCH (n)
WHERE n:FoodProduct OR n:Ingredient OR n:Additive OR n:Nutrient
   OR n:Brand OR n:Category OR n:RiskTag OR n:DataSource
DETACH DELETE n;
