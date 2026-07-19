# FoodPlatform 数据库初始化

本目录提供可独立导入的 MySQL 9.7.1 与 Neo4j 2026.06.0 演示数据库，不连接前端、不调用 Qwen，也不依赖后端服务。

## 文件

```text
database/
├─ mysql/
│  ├─ schema.sql       # 数据库、36 张表、约束和索引
│  ├─ seed.sql         # 与前端 Mock 对齐的演示数据
│  ├─ drop.sql         # 按外键逆序清表
│  ├─ views.sql        # 6 个常用视图
│  └─ procedures.sql   # 5 个事务/审计存储过程
├─ neo4j/
│  ├─ constraints.cypher
│  ├─ seed.cypher
│  ├─ queries.cypher
│  ├─ clear.cypher
│  └─ verify.cypher
├─ DATABASE_DESIGN.md
├─ data-mapping.md
├─ er-diagram.mmd
├─ er-diagram.md
└─ init-database.ps1
```

## 前置条件

- MySQL Server/Client，`mysql` 已加入 `PATH`。
- Neo4j 命令行工具，`cypher-shell` 已加入 `PATH`。
- 执行账户具有建库、建表、建视图/过程和写图权限。

## PowerShell 一键初始化

密码参数为 `SecureString`；省略时脚本会安全提示输入，不会把密码硬编码到文件或命令行。

```powershell
Set-Location D:\CodexProjects\FoodPlatform
$mysqlPassword = Read-Host 'MySQL password' -AsSecureString
$neo4jPassword = Read-Host 'Neo4j password' -AsSecureString
.\database\init-database.ps1 `
  -MySqlHost 127.0.0.1 -MySqlPort 3306 -MySqlUser root -MySqlPassword $mysqlPassword `
  -Neo4jAddress neo4j://localhost:7687 -Neo4jDatabase neo4j -Neo4jUser neo4j -Neo4jPassword $neo4jPassword
```

只初始化其中一个数据库：

```powershell
.\database\init-database.ps1 -SkipNeo4j
.\database\init-database.ps1 -SkipMySql
```

脚本顺序为 MySQL `schema → drop → schema → seed → views → procedures`，Neo4j `constraints → clear → seed → verify`。首次执行两次 schema 是为了让 `drop.sql` 始终可以安全 `USE food_platform`，从而保证首次和重复初始化走同一路径。

## 手工导入

MySQL Workbench 中按上述 MySQL 顺序逐文件执行。Neo4j Browser 中按 `constraints.cypher`、`clear.cypher`、`seed.cypher` 执行；常用验证和业务查询见 `queries.cypher`。

命令行也可以执行：

```powershell
mysql -h 127.0.0.1 -P 3306 -u root -p < database/mysql/schema.sql
$env:NEO4J_PASSWORD = Read-Host 'Neo4j password'
cypher-shell -a neo4j://localhost:7687 -u neo4j --database neo4j -f database/neo4j/constraints.cypher
```

## 演示账号

演示用户包括消费者 `linxiaoman`，商家 `merchant_zhiwei`，平台管理员 `gulan_admin`，知识管理员 `zhouyan_knowledge` 和运维 `zhaoning_ops`；统一测试密码为 `password`。数据库中只保存 bcrypt 测试哈希，不保存明文。该哈希仅用于本地演示，禁止用于生产环境。

## 清理与安全

`mysql/drop.sql` 只删除 `food_platform` 中本项目对象，不删除数据库本身。`neo4j/clear.cypher` 只删除 FoodPlatform 的八类节点及其关系，不删除 Neo4j 系统数据库。执行清理前仍应确认连接目标，生产环境应使用备份与最小权限账号。

## 兼容目标与自动验证

当前兼容目标为 MySQL 9.7.1 与 Neo4j 2026.06.0。MySQL 脚本及五个存储过程已在隔离的 MySQL 9.7.1 实例中实际执行；Neo4j 2026.06.0 的配置校验已通过，但本机现有服务因未提供有效认证凭据，尚未完成图数据实际导入，不能据此宣称导入测试通过。

初始化会清除目标库中的演示数据。执行前请确认主机、端口和 `-Neo4jDatabase` 指向可清理的目标数据库，并先备份必要数据。脚本顺序为：

- MySQL：`schema.sql` → `drop.sql` → `schema.sql` → `seed.sql` → `views.sql` → `procedures.sql`，随后验证 36 张基础表、6 个视图、5 个过程和 20 件商品。
- Neo4j：`constraints.cypher` → `clear.cypher` → `seed.cypher` → `verify.cypher`。验证预期为 FoodProduct 20、Ingredient 64、Additive 11、Nutrient 10、Brand 15、Category 10、RiskTag 12、DataSource 5，总节点 147，并输出每类关系数量。

单独验证 Neo4j：

```powershell
$env:NEO4J_PASSWORD = Read-Host 'Neo4j password'
cypher-shell -a neo4j://localhost:7687 -u neo4j --database neo4j -f database/neo4j/verify.cypher
Remove-Item Env:NEO4J_PASSWORD
```

手工验证 MySQL 对象：

```sql
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='food_platform' AND table_type='BASE TABLE';
SELECT COUNT(*) FROM information_schema.views WHERE table_schema='food_platform';
SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema='food_platform' AND routine_type='PROCEDURE';
SELECT COUNT(*) FROM food_platform.product WHERE is_deleted=0;
```

`FOOD_PRODUCT_CONTAINS_INGREDIENT` 表示明确含有，`FOOD_PRODUCT_MAY_CONTAIN` 表示标签声明的潜在交叉接触；没有任一关系只能判定为信息不足，不能判定绝对安全。原始配料保存在 MySQL `product.raw_ingredient_text`，标准化成分保存在 `product_ingredient_snapshot` 和已审核图关系中。所有跨库关联使用业务编码，禁止依赖 Neo4j 内部节点 ID。