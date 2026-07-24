# FoodPlatform FastAPI 后端

FoodPlatform 后端为消费者端、商家端和管理员端提供统一的 FastAPI 服务，负责认证授权、商品与食品信息、智能筛选、购物交易和多角色工作台业务。

## 技术与架构

- FastAPI
- Pydantic v2 / pydantic-settings
- SQLAlchemy 2 / PyMySQL
- Neo4j 官方 Python Driver
- JWT / bcrypt
- HTTPX
- pytest

后端采用同步分层架构：

```text
API Router
    ↓
Service
    ↓
Repository
    ↓
MySQL / Neo4j / Qwen
```

- Router 负责参数校验、认证依赖和响应模型。
- Service 负责业务编排、状态规则和统一业务异常。
- Repository 负责参数化 SQL、Cypher 查询和事务。
- MySQL 是用户、商品、库存、订单、评价和审核数据的权威来源。
- Neo4j 提供食品成分、别名、衍生、风险和来源关系。
- Qwen 只补充自然语言条件解析，不直接修改数据库或判断商品交易状态。

## API 模块

基础前缀为 `/api/v1`。

### 基础与健康检查

- `/`
- `/api/v1/health`
- `/api/v1/health/live`
- `/api/v1/health/ready`

### 认证与用户

- `/api/v1/auth/register`
- `/api/v1/auth/login`
- `/api/v1/auth/token`
- `/api/v1/users/me`
- `/api/v1/users/preferences`
- `/api/v1/preferences`
- `/api/v1/addresses`
- `/api/v1/favorites`

认证使用 bcrypt 密码哈希和 JWT Bearer Token。数据库角色 `PLATFORM_ADMIN` 在 API 中映射为 `ADMIN`；商家接口要求 `MERCHANT`，管理员接口要求 `ADMIN`。

### 商品与知识图谱

- `/api/v1/products`
- `/api/v1/products/{product_code}`
- `/api/v1/products/{product_code}/graph`
- `/api/v1/categories`
- `/api/v1/brands`
- `/api/v1/reviews`

商品详情分别返回原始配料文本、结构化成分、营养数据和信息来源。图谱接口使用业务编码，不暴露 Neo4j 内部节点 ID。

### 智能筛选

- `POST /api/v1/filter/analyze`
- `POST /api/v1/filter/search`

智能解析先提取受控硬条件，再按配置调用 Qwen 补充复杂语义。Qwen 超时、上游失败、JSON 无效或 Schema 校验失败时自动返回规则解析结果。筛选严格区分明确含有、可能含有和信息不足。

### 购物与订单

- `/api/v1/cart`
- `/api/v1/orders`
- `/api/v1/addresses`
- `/api/v1/favorites`
- `/api/v1/reviews`

订单创建会校验当前价格和库存、保存商品与规格快照并在事务内扣减库存。支付接口为项目内模拟支付，不连接真实支付渠道。

### 商家工作台

- `GET /api/v1/merchant/dashboard`
- `GET/POST /api/v1/merchant/products`
- `PUT /api/v1/merchant/products/{product_code}`
- `PUT /api/v1/merchant/products/{product_code}/sale-status`
- `GET /api/v1/merchant/orders`
- `PUT /api/v1/merchant/orders/{order_id}/status`

商家身份通过当前 JWT 用户关联 `merchant.owner_user_id`，只能访问自己的商品和订单。

### 管理员工作台

- `GET /api/v1/admin/dashboard`
- `GET /api/v1/admin/users`
- `PUT /api/v1/admin/users/{user_id}/status`
- `GET /api/v1/admin/products`
- `PUT /api/v1/admin/products/{product_code}/approve`

管理员可查看平台统计、按用户名或邮箱搜索用户、启停用户以及审核商品。接口不提供密码修改、角色修改或用户删除。

## 数据库连接

### MySQL

- 使用 SQLAlchemy Engine 和连接池。
- 启用 `pool_pre_ping` 检测失效连接。
- Session 按操作创建并释放。
- 写操作使用事务，异常自动回滚。
- 应用账号不应使用 root，最小权限配置见 [docs/mysql-user.md](docs/mysql-user.md)。

### Neo4j

- 应用启动时创建 Driver，关闭时释放。
- 每次查询显式指定 `NEO4J_DATABASE`。
- Cypher 使用参数化业务编码。
- 图谱接口只读，不执行知识图谱增删改。

## 环境变量

复制模板：

```powershell
Copy-Item .env.example .env
```

必须在本地 `.env` 中配置：

```env
MYSQL_HOST=
MYSQL_PORT=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=

NEO4J_URI=
NEO4J_USER=
NEO4J_PASSWORD=
NEO4J_DATABASE=

JWT_SECRET=
CORS_ORIGINS=

QWEN_ENABLED=false
QWEN_API_KEY=
QWEN_MODEL=
QWEN_BASE_URL=
QWEN_TIMEOUT_SECONDS=8
```

`MYSQL_PASSWORD`、`NEO4J_PASSWORD` 和 `JWT_SECRET` 是必需配置。仅在启用 Qwen 时配置 `QWEN_API_KEY`。所有密钥由 `SecretStr` 管理，不应写入日志或提交到 Git。

## 安装与启动

```powershell
Set-Location D:\CodexProjects\FoodPlatform
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install --upgrade pip
backend\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

访问：

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- OpenAPI：`http://127.0.0.1:8000/openapi.json`

## 测试

```powershell
Set-Location D:\CodexProjects\FoodPlatform\backend
.\.venv\Scripts\python.exe -m pytest
```

当前代码最近一次完整验证为 `86 passed`。单元测试使用依赖替身，不读取真实数据库密码，也不会清理本地数据库。

真实环境就绪检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

当 MySQL 或 Neo4j 不可用时，就绪接口返回 503 并标识异常组件，但不会返回密码、连接串或数据库堆栈。

## 安全说明

- 不提交 `.env`、虚拟环境、日志、Token、API Key 或数据库备份。
- 不在日志中输出 Authorization、密码或数据库连接凭据。
- 所有用户数据接口通过 JWT 中的 `user_id` 隔离。
- 商家和管理员写接口同时执行前端路由保护与后端角色检查。