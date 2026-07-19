# 前端 Mock 与数据库映射

前端 `src/mock/data.ts` 是演示展示数据，数据库 seed 尽量保持商品 ID、名称、品牌、分类和业务含义一致。运行时接入后端后应以数据库为权威源。

| Mock 字段 | MySQL | Neo4j | 说明 |
|---|---|---|---|
| `product.id` | `product.id` | `FoodProduct.product_code` | ID 1–20 映射 `FP0001`–`FP0020`，跨库不用内部 ID |
| `product.name` | `product.product_name` | `FoodProduct.name` | 审核通过后同步 |
| `product.brand` | `brand.brand_name`，`product.brand_id` | `(FoodProduct)-[:FOOD_PRODUCT_BELONGS_TO_BRAND]->(Brand)` | 以 `brand_code` 对齐 |
| `product.category` | `category.category_name`，`product.category_id` | `(FoodProduct)-[:FOOD_PRODUCT_BELONGS_TO_CATEGORY]->(Category)` | 以 `category_code` 对齐 |
| `product.price` | 当前有效 `product_price.sale_price` | 不保存 | 交易价格只属于 MySQL |
| `product.stock` | `product_inventory.available_quantity` | 不保存 | 库存只属于 MySQL |
| `product.image` / `images` | `product_image.image_url` | 不保存 | 主图由 `is_primary` 标识 |
| `product.ingredients` | 原文：`product.raw_ingredient_text`；结构化：`product_ingredient_snapshot` | `Ingredient` 及 `FOOD_PRODUCT_CONTAINS_INGREDIENT` / `FOOD_PRODUCT_MAY_CONTAIN` | 原文与标准化结果分开保留 |
| `product.additives` | `product_ingredient_snapshot.entity_type='ADDITIVE'` | `Additive` 及 `FOOD_PRODUCT_HAS_ADDITIVE` | 使用 `additive_code` |
| `product.nutrition` | `product_nutrition(value, unit, basis)` | `FOOD_PRODUCT_HAS_NUTRIENT` 关系的 `value/unit/basis` | 缺失值保持 NULL/不建关系，不伪造 |
| `product.riskTags` | 可在配料快照/审核结果 JSON 中缓存 | `Ingredient-[:INGREDIENT_HAS_RISK]->RiskTag` | 风险由已审核路径解释 |
| `product.matchStatus` | 查询结果可写 `ai_filter_history.result_summary` | 可作演示属性 `FoodProduct.match_status` | 真实状态应按用户条件动态计算，不是永久商品事实 |
| `product.rating` | `product_review.rating` 聚合视图 | 不保存 | `vw_product_average_rating` 计算 |
| `product.reviewCount` | `product_review` 聚合 | 不保存 | 不直接信任前端计数 |
| `orders[]` | `order_info` + `order_item` + `payment_record` | 不保存 | 订单项保存商品交易快照 |
| `reviews[]` | `product_review` | 不保存 | 审核状态控制展示 |
| `filterHistory[]` | `ai_filter_history`，可关联 `ai_conversation` | 不保存查询历史 | 条件 JSON 区分硬约束、软偏好、待确认 |
| `anomalies[]` | `anomaly_record` | 仅已审核的修复结果入图 | 异常处置过程留在 MySQL |
| `reviewTasks[]` | `product_audit` + `workflow_task` | 发布后关系带 `audit_status/version` | 审核历史不可覆盖 |
| `auditLogs[]` | `audit_log` | 不保存 | 记录前后值、原因与操作者 |

## 统一业务键

- 商品：`product.product_code` ↔ `FoodProduct.product_code`
- 成分：`product_ingredient_snapshot.entity_code` ↔ `Ingredient.ingredient_code`
- 添加剂：`entity_code` ↔ `Additive.additive_code`
- 品牌：`brand.brand_code` ↔ `Brand.brand_code`
- 分类：`category.category_code` ↔ `Category.category_code`
- 风险：审核/缓存 JSON 中的代码 ↔ `RiskTag.risk_tag_code`

`matchStatus` 的业务规则为：硬排除成分命中 `CONTAINS` 时不匹配；命中 `MAY_CONTAIN` 时存在风险；事实缺失、冲突或低置信度时信息不足；其余条件满足才是完全匹配。
