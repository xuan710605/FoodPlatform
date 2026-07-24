# FoodPlatform 数据库初始化

本目录提供 FoodPlatform 当前 MySQL 与 Neo4j 数据模型、初始化数据、验证脚本和设计说明。数据库同时支撑消费者交易、商家经营、管理员治理和食品知识图谱功能。

## 数据库职责

- **MySQL**：用户、角色、商家、商品、价格、库存、地址、收藏、购物车、订单、评价、商品审核、AI记录和审计日志。
- **Neo4j**：食品、成分、添加剂、营养、品牌、分类、风险标签、来源及其知识关系。

跨库关联只使用 `product_code`、`ingredient_code`、`brand_code`、`category_code` 等业务编码，不依赖 Neo4j 内部节点 ID。

## 文件结构

```text
database/
├─ mysql/
│  ├─ schema.sql           # 数据库、36张基础表、约束与索引
│  ├─ drop.sql             # 按外键顺序删除项目表
│  ├─ seed.sql             # 当前平台演示业务数据
│  ├─ views.sql            # 6个常用视图
│  └─ procedures.sql       # 5个事务与审计存储过程
├─ neo4j/
│  ├─ constraints.cypher   # 业务键唯一约束与索引
│  ├─ clear.cypher         # 清理FoodPlatform图数据
│  ├─ seed.cypher          # 节点与关系初始化
│  ├─ queries.cypher       # 常用知识查询
│  └─ verify.cypher        # 只读一致性验证
├─ DATABASE_DESIGN.md
├─ data-mapping.md
├─ er-diagram.mmd
├─ er-diagram.md
└─ init-database.ps1
```

## 前置条件

- MySQL Server和MySQL命令行客户端
- Neo4j和 `cypher-shell`
- 执行初始化的管理员账号
- 可被脚本清理的目标数据库

初始化会清除目标库中的项目演示数据。执行前必须确认主机、端口和数据库，并备份需要保留的数据。

## PowerShell初始化

密码通过 `SecureString` 传入，不应写入命令、脚本或仓库：

```powershell
Set-Location D:\CodexProjects\FoodPlatform
$mysqlPassword = Read-Host 'MySQL password' -AsSecureString
$neo4jPassword = Read-Host 'Neo4j password' -AsSecureString
.\database\init-database.ps1 `
  -MySqlHost 127.0.0.1 `
  -MySqlPort 3306 `
  -MySqlUser root `
  -MySqlPassword $mysqlPassword `
  -Neo4jAddress neo4j://localhost:7687 `
  -Neo4jDatabase neo4j `
  -Neo4jUser neo4j `
  -Neo4jPassword $neo4jPassword
```

只初始化一个数据库：

```powershell
.\database\init-database.ps1 -SkipNeo4j
.\database\init-database.ps1 -SkipMySql
```

执行顺序：

```text
MySQL: schema.sql → drop.sql → schema.sql → seed.sql → views.sql → procedures.sql → 验证
Neo4j: constraints.cypher → clear.cypher → seed.cypher → verify.cypher
```

## 手工导入

MySQL Workbench按上述MySQL顺序逐个执行文件。Neo4j推荐使用 `cypher-shell -f` 执行完整脚本：

```powershell
cypher-shell -a neo4j://localhost:7687 -u neo4j --database neo4j -f database/neo4j/constraints.cypher
cypher-shell -a neo4j://localhost:7687 -u neo4j --database neo4j -f database/neo4j/clear.cypher
cypher-shell -a neo4j://localhost:7687 -u neo4j --database neo4j -f database/neo4j/seed.cypher
cypher-shell -a neo4j://localhost:7687 -u neo4j --database neo4j -f database/neo4j/verify.cypher
```

不要将密码直接写在命令或文档中。可使用安全提示或临时环境变量，并在执行后删除环境变量。

## 验证

MySQL预期对象：

- 36张基础表
- 6个视图
- 5个存储过程
- 20件初始化商品

```sql
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema='food_platform' AND table_type='BASE TABLE';
SELECT COUNT(*) FROM information_schema.views
WHERE table_schema='food_platform';
SELECT COUNT(*) FROM information_schema.routines
WHERE routine_schema='food_platform' AND routine_type='PROCEDURE';
SELECT COUNT(*) FROM food_platform.product WHERE is_deleted=0;
```

Neo4j `verify.cypher` 验证八类节点、业务编码唯一性、缺失编码和关键解释路径，并输出各关系类型数量。初始化数据预期包含147个项目节点。

当前脚本面向 MySQL 9.7.1 和 Neo4j 2026.06.0，项目最终联调环境的 MySQL、Neo4j与FastAPI就绪检查均已通过。

## 数据边界

- MySQL保存交易事实、原始配料文本和结构化成分快照。
- Neo4j保存已发布的知识关系与证据属性。
- `FOOD_PRODUCT_CONTAINS_INGREDIENT` 表示明确含有。
- `FOOD_PRODUCT_MAY_CONTAIN` 表示标签声明的潜在接触。
- 缺少关系只能判定为信息不足，不能判定绝对安全。
- 商品审核和知识审核记录必须保留历史。

详细设计见 [DATABASE_DESIGN.md](DATABASE_DESIGN.md)，字段契约见 [data-mapping.md](data-mapping.md)，实体关系见 [er-diagram.md](er-diagram.md)。

## 安全建议

- 初始化账号与应用账号分离。
- FastAPI使用最小权限应用账号，参考 [../backend/docs/mysql-user.md](../backend/docs/mysql-user.md)。
- 不提交密码、环境变量、Token、数据库数据目录或备份文件。
- 正式环境执行初始化前必须备份，且不得将初始化脚本指向生产库。