# FoodPlatform 数据契约映射

本文描述当前 React 前端、FastAPI Schema、MySQL业务表和Neo4j知识节点之间的字段契约。运行时业务数据以MySQL和Neo4j为权威来源，前端通过API响应模型消费数据。

## 商品列表

| 前端/API字段 | MySQL来源 | Neo4j来源 | 说明 |
|---|---|---|---|
| `id` | `product.id` | 不使用 | 仅用于MySQL内部和当前前端展示 |
| `product_code` | `product.product_code` | `FoodProduct.product_code` | 对外商品业务标识 |
| `name` | `product.product_name` | `FoodProduct.name` | 商品名称 |
| `subtitle` | `product.subtitle` | 不使用 | 可为空 |
| `brand` / `brand_code` | `brand.brand_name/brand_code` | `Brand.brand_code` | 通过 `product.brand_id` 关联 |
| `category` / `category_code` | `category.category_name/category_code` | `Category.category_code` | 通过 `product.category_id` 关联 |
| `merchant` | `merchant.merchant_name` | 不使用 | 商品所属商家 |
| `main_image_url` | `product_image.image_url` | 不使用 | `image_type='MAIN'` 的有效图片 |
| `sale_price` | 当前有效 `product_price.amount` | 不使用 | `price_type='SALE'` |
| `stock_quantity` | `product_inventory.available_qty-locked_qty` | 不使用 | 库存事实仅在MySQL维护 |
| `average_rating` | `product_review.rating` 聚合 | 不使用 | 只统计已发布评价 |
| `review_count` | `product_review` 聚合 | 不使用 | 无评价时由API返回空语义或数量 |
| `sales_count` | 有效 `order_item.quantity` 聚合 | 不使用 | 排除待支付和已取消订单 |

普通商品列表只返回商品事实，不携带当前用户的智能筛选匹配状态。

## 商品详情

| API字段 | MySQL来源 | 说明 |
|---|---|---|
| `description` | `product.description` | 可为空 |
| `raw_ingredient_text` | `product.raw_ingredient_text` | 保留包装原始文本 |
| `contains` | `product_ingredient_snapshot.relation_type='CONTAINS'` | 明确含有 |
| `may_contain` | `relation_type='MAY_CONTAIN'` | 可能含有 |
| `unknown` | `relation_type='UNKNOWN'` | 未识别或证据不足 |
| `nutrition` | `product_nutrition` | 每项保留 `value/unit/basis` |
| `images` | `product_image` | 主图、详情图和标签图 |
| `specs` | `product_spec`、`product_price`、`product_inventory` | 规格、当前价格和库存 |
| `allergen_notice` | `product.allergen_notice` | 包装过敏原提示 |
| `info_source` | `product.info_source` | 信息来源说明 |

原始配料文本与结构化成分必须分别保存和返回，不能相互覆盖。

## 知识图谱

| MySQL业务编码 | Neo4j节点或关系 |
|---|---|
| `product.product_code` | `FoodProduct.product_code` |
| `product_ingredient_snapshot.entity_code` | `Ingredient.ingredient_code` 或 `Additive.additive_code` |
| `brand.brand_code` | `Brand.brand_code` |
| `category.category_code` | `Category.category_code` |
| `product_nutrition.nutrient_code` | `Nutrient.nutrient_code` |
| 风险业务编码 | `RiskTag.risk_tag_code` |

主要关系：

- `FOOD_PRODUCT_CONTAINS_INGREDIENT`
- `FOOD_PRODUCT_MAY_CONTAIN`
- `FOOD_PRODUCT_HAS_ADDITIVE`
- `FOOD_PRODUCT_HAS_NUTRIENT`
- `FOOD_PRODUCT_BELONGS_TO_BRAND`
- `FOOD_PRODUCT_BELONGS_TO_CATEGORY`
- `INGREDIENT_ALIAS_OF`
- `INGREDIENT_DERIVED_FROM`
- `INGREDIENT_HAS_RISK`
- `INGREDIENT_CAN_SUBSTITUTE`
- `ENTITY_FROM_SOURCE`

关系证据使用 `source_code`、`audit_status` 和 `confidence`。API节点ID由标签和业务编码组成，不依赖Neo4j内部ID。

## 智能筛选

`POST /api/v1/filter/analyze` 输出统一 `FilterConditions`：

- `category_code`
- `exclude_categories`
- `exclude_ingredients`
- `preferred_ingredients`
- `nutrition_targets`
- `max_price`

`POST /api/v1/filter/search` 使用相同条件，并返回：

- `MATCH`：满足当前已知条件
- `RISK`：可能含有用户排除成分
- `NOT_MATCH`：明确命中排除条件或违反营养、价格硬约束
- `UNKNOWN`：商品事实或证据不足

商品自身的成分事实不等于用户筛选结论。只有与当前用户条件发生匹配时，才生成筛选状态和解释。

## 用户与角色

| API字段 | MySQL来源 |
|---|---|
| `user.id` | `sys_user.id` |
| `user.user_code` | `sys_user.user_code` |
| `user.username` | `sys_user.username` |
| `user.email` | `sys_user.email` |
| `user.status` | `sys_user.status` |
| `user.roles` | `sys_user_role` + `sys_role` |

数据库角色 `PLATFORM_ADMIN` 在API中映射为 `ADMIN`。用户、地址、收藏、购物车、订单和偏好均通过JWT中的 `user_id` 隔离。

## 商家与管理员

- 商家身份：`sys_user.id → merchant.owner_user_id`
- 商家商品：`product.merchant_id → merchant.id`
- 商家订单：`order_info.merchant_id → merchant.id`
- 管理员用户状态：`sys_user.status`
- 商品审核：`product.review_status` 与 `product_audit`

商家接口不得接受前端传入的商家ID作为数据范围依据；管理员用户状态接口只更新状态，不修改密码、角色或删除标记。

## 订单与评价

| API数据 | MySQL来源 |
|---|---|
| 订单 | `order_info` |
| 订单商品 | `order_item` |
| 支付记录 | `payment_record` |
| 地址快照 | `order_info.receiver_snapshot` |
| 商品评价 | `product_review` |

订单项保存商品编码、名称、规格、价格、图片和成分版本快照。用户只能评价自己已完成订单中尚未评价的商品。