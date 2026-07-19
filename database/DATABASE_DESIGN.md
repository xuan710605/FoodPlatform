# FoodPlatform 数据库设计

## 1. 数据库架构

平台采用 MySQL 8.0 + Neo4j 5.x 的双数据库架构。MySQL 数据库名为 `food_platform`，负责账户、交易、商品事实、审核与审计；Neo4j 负责食品、配料、添加剂、风险、营养及来源之间的可解释关系。当前目录只提供可独立导入的初始化文件，不依赖前端、后端或外部服务。

## 2. MySQL 与 Neo4j 的职责边界

| 数据 | 权威存储 | 说明 |
|---|---|---|
| 用户、权限、地址、偏好 | MySQL | 隐私数据及授权事实 |
| 商品名称、规格、价格、库存、订单 | MySQL | 交易事实，必须在事务内更新 |
| 原始配料文本、营养表、商家提交版本 | MySQL | 保留原始证据和审核历史 |
| 标准成分、别名、衍生、替代、风险路径 | Neo4j | 知识事实和图查询 |
| AI 查询、解析条件、调用日志 | MySQL | Qwen 仅产生建议，不直接改写商品事实 |
| 图谱审核历史 | MySQL `knowledge_audit` | Neo4j 保存已发布关系，MySQL 保存审批过程 |

价格、库存与订单状态不得从 Neo4j 推断；知识关系不得用 MySQL 临时拼接结果替代。

## 3. 核心实体

- 身份域：用户、角色、权限、用户资料、地址、成分偏好。
- 商品域：商家、品牌、分类、商品、规格、图片、价格、库存、原始/结构化配料、营养。
- 交易域：购物车、收藏、浏览历史、订单、订单项、支付、评价。
- 治理域：商品审核、知识审核、异常、反馈、工作流、审计日志。
- AI 域：会话、筛选历史、模型调用日志。解析结果区分硬约束、软偏好与待确认条件。

## 4. 核心表说明

共 36 张表。`product` 保留 `raw_ingredient_text` 和 `neo4j_node_key`；`product_ingredient_snapshot` 保存可追溯的结构化配料关系；`order_item` 保存商品名、规格、单价与图片快照，避免商品变更破坏历史订单。`product_price` 支持生效区间，`product_inventory` 通过 `version_no` 支持乐观锁，`inventory_change_log` 保留库存流水。

状态字段采用可读 `VARCHAR`，例如商品 `DRAFT/PENDING/APPROVED/REJECTED`、订单 `PENDING_PAYMENT/PAID/SHIPPED/COMPLETED/CANCELLED`。逻辑删除实体使用 `is_deleted` 与 `deleted_at`。

## 5. 表关系

用户通过中间表关联角色；角色通过中间表关联权限。商家、品牌和分类分别与商品关联；商品拥有多个规格、图片、价格、库存、配料快照、营养值、评价与审核记录。用户拥有购物车、收藏、历史、订单和 AI 会话；订单包含订单项及支付记录。详细关系见 [er-diagram.md](./er-diagram.md)。

## 6. 知识图谱节点与关系

节点标签为 `FoodProduct`、`Ingredient`、`Additive`、`Nutrient`、`Brand`、`Category`、`RiskTag`、`DataSource`。核心关系包括：

- `FOOD_PRODUCT_CONTAINS_INGREDIENT`、`FOOD_PRODUCT_MAY_CONTAIN`
- `FOOD_PRODUCT_HAS_ADDITIVE`、`FOOD_PRODUCT_HAS_NUTRIENT`
- `FOOD_PRODUCT_BELONGS_TO_BRAND`、`FOOD_PRODUCT_BELONGS_TO_CATEGORY`
- `INGREDIENT_ALIAS_OF`、`INGREDIENT_DERIVED_FROM`
- `INGREDIENT_HAS_RISK`、`INGREDIENT_CAN_SUBSTITUTE`
- `ENTITY_FROM_SOURCE`

关系携带来源、审核状态、置信度或版本等证据属性。显式包含排除成分判定为“不匹配”；“可能含有”判定为“存在风险”；缺失、冲突或低置信度判定为“信息不足”。

## 7. MySQL 与 Neo4j 同步方式

建议使用 Outbox/CDC：MySQL 商品审核通过后，在同一事务中落库商品版本与待发布工作流任务；异步同步器以业务键 `MERGE` Neo4j 节点和关系，成功后回写图谱版本及同步时间。失败任务进入 `workflow_task`/`anomaly_record` 重试，不回滚已经完成的交易事务。Neo4j 的知识修改先写 `knowledge_audit`，通过后发布并触发受影响商品重新核验。

## 8. 业务主键设计

跨库只使用稳定业务键：`product_code`、`ingredient_code`、`brand_code`、`category_code`、`additive_code`、`risk_tag_code`。MySQL 自增 `id` 仅用于库内连接；Neo4j 内部节点 ID 不对外暴露。演示商品保持前端 ID 1–20，并映射为 `FP0001`–`FP0020`。

## 9. 数据一致性策略

- MySQL 是商品事实和交易事实的唯一权威源。
- 同步使用业务键、版本号和幂等 `MERGE`；旧版本事件不得覆盖新版本。
- 图谱关系必须记录来源与审核状态；冲突进入异常中心。
- 定时对账商品代码、审核版本和营养/配料数量，差异生成 `anomaly_record`。
- AI 输出只写解析记录或待确认任务，人工/商家确认后才进入事实表。

## 10. 事务边界

创建订单、写订单快照、扣减库存与写库存流水属于一个 MySQL 事务；取消订单与恢复库存属于另一个事务。支付渠道回调后以支付流水号幂等更新。Neo4j 发布不参与 MySQL 分布式事务，采用最终一致性和可重放任务。存储过程提供演示级原子操作，正式后端仍应补充业务幂等键、鉴权与重试。

## 11. 初始化顺序

MySQL：`schema.sql`（确保数据库存在）→ `drop.sql` → `schema.sql` → `seed.sql` → `views.sql` → `procedures.sql`。Neo4j：`constraints.cypher` → `clear.cypher` → `seed.cypher`。`init-database.ps1` 已固化此顺序。

## 12. 备份与恢复

MySQL 建议每日全量 `mysqldump --single-transaction`，配合 binlog 做时间点恢复；恢复演练应验证外键、视图和过程。Neo4j 使用 `neo4j-admin database backup`，备份前记录应用图谱版本。双库恢复后按业务键和版本表对账，再开放写流量。

## 13. 数据库安全

应用使用最小权限独立账号，禁止以 root 连接；读写、迁移与同步账号分离。密码仅保存强哈希，seed 中 bcrypt 值只用于本地演示。生产环境通过密钥管理器注入凭据，启用 TLS、审计、备份加密及网络白名单。地址、手机号等敏感字段应应用层加密或脱敏，日志不得记录密码或完整个人信息。

## 14. 后端接口建议

按身份、商品、交易、治理、AI、图谱六个模块组织接口。写接口使用幂等键和资源版本；商品详情接口聚合 MySQL 事实与 Neo4j 已审核关系，并分别标注来源/更新时间。智能筛选接口返回解析条件、证据路径、匹配状态与降级状态；图谱不可用时应返回基础筛选结果而非伪造关系。

## 15. MySQL Workbench 导入

连接 MySQL 8.0 后依次打开并执行 `mysql/schema.sql`、`mysql/drop.sql`、再次执行 `mysql/schema.sql`、`mysql/seed.sql`、`mysql/views.sql`、`mysql/procedures.sql`。使用支持 UTF-8 的连接并确保账户具有创建数据库、表、视图和过程权限。也可直接运行 `init-database.ps1`。

## 16. Neo4j Browser 导入

连接目标 Neo4j 5.x 数据库，在 Browser 中依次粘贴执行 `constraints.cypher`、`clear.cypher`、`seed.cypher` 的语句。Browser 对超长多语句脚本可能需要逐条运行；命令行推荐使用 `cypher-shell -f`。`clear.cypher` 只删除本项目八类节点，不删除数据库、用户或系统数据。
