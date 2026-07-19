# FoodPlatform 数据库初始化

本目录提供可独立导入的 MySQL 8.0 与 Neo4j 5.x 演示数据库，不连接前端、不调用 Qwen，也不依赖后端服务。

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
│  └─ clear.cypher
├─ DATABASE_DESIGN.md
├─ data-mapping.md
├─ er-diagram.mmd
├─ er-diagram.md
└─ init-database.ps1
```

## 前置条件

- MySQL Server/Client 8.0，`mysql` 已加入 `PATH`。
- Neo4j 5.x，`cypher-shell` 已加入 `PATH`。
- 执行账户具有建库、建表、建视图/过程和写图权限。

## PowerShell 一键初始化

密码参数为 `SecureString`；省略时脚本会安全提示输入，不会把密码硬编码到文件或命令行。

```powershell
Set-Location D:\CodexProjects\FoodPlatfrom
$mysqlPassword = Read-Host 'MySQL password' -AsSecureString
$neo4jPassword = Read-Host 'Neo4j password' -AsSecureString
.\database\init-database.ps1 `
  -MySqlHost 127.0.0.1 -MySqlPort 3306 -MySqlUser root -MySqlPassword $mysqlPassword `
  -Neo4jAddress neo4j://localhost:7687 -Neo4jUser neo4j -Neo4jPassword $neo4jPassword
```

只初始化其中一个数据库：

```powershell
.\database\init-database.ps1 -SkipNeo4j
.\database\init-database.ps1 -SkipMySql
```

脚本顺序为 MySQL `schema → drop → schema → seed → views → procedures`，Neo4j `constraints → clear → seed`。首次执行两次 schema 是为了让 `drop.sql` 始终可以安全 `USE food_platform`，从而保证首次和重复初始化走同一路径。

## 手工导入

MySQL Workbench 中按上述 MySQL 顺序逐文件执行。Neo4j Browser 中按 `constraints.cypher`、`clear.cypher`、`seed.cypher` 执行；常用验证和业务查询见 `queries.cypher`。

命令行也可以执行：

```powershell
mysql -h 127.0.0.1 -P 3306 -u root -p < database/mysql/schema.sql
$env:NEO4J_PASSWORD = Read-Host 'Neo4j password'
cypher-shell -a neo4j://localhost:7687 -u neo4j -f database/neo4j/constraints.cypher
```

## 演示账号

演示用户包括消费者 `linxiaoman`，商家 `merchant_zhiwei`，平台管理员 `gulan_admin`，知识管理员 `zhouyan_knowledge` 和运维 `zhaoning_ops`；统一测试密码为 `password`。数据库中只保存 bcrypt 测试哈希，不保存明文。该哈希仅用于本地演示，禁止用于生产环境。

## 清理与安全

`mysql/drop.sql` 只删除 `food_platform` 中本项目对象，不删除数据库本身。`neo4j/clear.cypher` 只删除 FoodPlatform 的八类节点及其关系，不删除 Neo4j 系统数据库。执行清理前仍应确认连接目标，生产环境应使用备份与最小权限账号。
