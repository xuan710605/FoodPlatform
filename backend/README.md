# FoodPlatform FastAPI backend

Version `0.3.0` provides the backend foundation, read-only product/graph APIs, authentication, user preferences, and basic catalog APIs. It does not implement orders, payment, Qwen, graph writes, deployment, or frontend integration.

## Architecture

```text
API routes -> Services -> Repositories -> MySQL / Neo4j
```

- MySQL is the source of product, price, inventory, raw ingredient, nutrition, and audit-state facts.
- Neo4j supplies approved knowledge relationships and explanatory risk paths.
- External identifiers are business codes such as `product_code`; Neo4j internal IDs are never exposed.
- The implementation is synchronous throughout. SQLAlchemy's bounded connection pool and the Neo4j driver's pool keep the code easy to maintain for this course project without mixing sync and async database APIs.

## Requirements and verified dependency set

The local installation was performed with Python 3.14.6. The resolved core versions were FastAPI 0.128.8, Uvicorn 0.40.0, Pydantic 2.12.5, pydantic-settings 2.12.0, SQLAlchemy 2.0.51, PyMySQL 1.1.3, cryptography 46.0.7, bcrypt 5.0.0, PyJWT 2.10.1, email-validator 2.3.0, Neo4j Driver 6.1.0, pytest 9.0.3, and HTTPX 0.28.1. `pyproject.toml` uses narrow version ranges rather than unbounded `latest` dependencies.

## Setup

```powershell
Set-Location D:\CodexProjects\FoodPlatform
python -m venv backend\.venv
Copy-Item backend\.env.example backend\.env
Set-Location backend
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Edit `backend/.env` and replace all credential placeholders, including a random `JWT_SECRET` of at least 32 characters. Never commit that file. The application requires `MYSQL_PASSWORD` and `NEO4J_PASSWORD`; missing values produce a configuration validation error without printing a secret.

Create `food_platform_app` manually with only `SELECT`, `INSERT`, `UPDATE`, `DELETE`, and `EXECUTE`; see [docs/mysql-user.md](docs/mysql-user.md). The API never creates database users, changes root credentials, or receives schema-management privileges.

## Run

```powershell
Set-Location D:\CodexProjects\FoodPlatform\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

If PowerShell activation is desired but blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then `.\.venv\Scripts\Activate.ps1`. Calling the virtual-environment Python directly does not require activation.

Swagger is at `http://127.0.0.1:8000/docs`; ReDoc is at `/redoc`; the schema is at `/openapi.json`.

## Implemented endpoints

- `GET /`
- `GET /api/v1/health`
- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `GET /api/v1/products`
- `GET /api/v1/products/{product_code}`
- `GET /api/v1/products/{product_code}/graph`

The product list returns only undeleted, approved products and defaults to `ON_SALE`. Sorting uses a server-side whitelist. Product details keep raw ingredient text separate from approved structured snapshots. The graph endpoint distinguishes `FOOD_PRODUCT_CONTAINS_INGREDIENT` from `FOOD_PRODUCT_MAY_CONTAIN`; absence of graph evidence means insufficient or unsynchronized information, never proof of safety.

## Tests

Unit tests use service and database substitutes and never read real credentials or clear databases:

```powershell
Set-Location D:\CodexProjects\FoodPlatform\backend
.\.venv\Scripts\python.exe -m pytest
```

For a local integration check, configure `backend/.env`, start Uvicorn, then run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/products?page=1&page_size=5'
Invoke-RestMethod http://127.0.0.1:8000/api/v1/products/FP0001
Invoke-RestMethod http://127.0.0.1:8000/api/v1/products/FP0017/graph
```

These calls are read-only and never initialize or clear either database.

## Not implemented in this stage

Cart, orders, payment, merchant/admin write APIs, Qwen calls, smart-filter rule execution, graph mutation, background jobs, Docker deployment, and frontend API replacement remain intentionally out of scope.

## Troubleshooting

- PowerShell blocks activation: use the process-scoped execution-policy command above or call `.venv\Scripts\python.exe` directly.
- MySQL connection refused: verify the service, host/port, database, and least-privilege account; do not switch the code default to root.
- Neo4j authentication failed: verify `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE` in `.env`.
- Port 8000 is occupied: choose another `--port` and update the caller.
- CORS rejected: add the exact trusted frontend origin to comma-separated `CORS_ORIGINS`; wildcard origins are rejected.

Do not commit `.env`, `.venv`, logs, caches, passwords, or database data files.

## Authentication and base business APIs

The second foundation stage adds bcrypt registration, JWT login, current-user lookup, role guards, user preferences, categories, and brands. Configure a random local `JWT_SECRET` of at least 32 characters in ignored `backend/.env`; only `HS256` is accepted and access tokens default to 60 minutes.

Implemented endpoints now also include:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`
- `GET /api/v1/preferences`
- `POST /api/v1/preferences`
- `DELETE /api/v1/preferences/{id}`
- `GET /api/v1/categories`
- `GET /api/v1/brands`

Database role `PLATFORM_ADMIN` is normalized to API role `ADMIN`; `CONSUMER`, `MERCHANT`, `KNOWLEDGE_ADMIN`, and the legacy `OPS` role retain their codes. `require_role()` is available for later `/admin/*` and `/merchant/*` routers.

The existing database has `user_ingredient_preference`, not a generic `user_preference` table. The API stores the requested preference category in `preference_source`: allergen and dietary restriction records use `EXCLUDE`, while nutrition targets use `PREFER`. Older `USER_INPUT` rows are mapped safely when read. No schema migration is performed.

See [docs/mysql-user.md](docs/mysql-user.md) for the manual least-privilege `food_platform_app` grant. The backend never creates that account automatically and never receives `DROP`, `ALTER`, or `CREATE` privileges.

## 确定性食品筛选基础接口

- `POST /api/v1/filter/analyze`：使用受控规则解析排除成分、营养目标、价格上限与分类，不调用Qwen。
- `POST /api/v1/filter/search`：组合MySQL商品事实与Neo4j成分别名、衍生及风险证据，返回 `MATCH`、`RISK`、`NOT_MATCH` 或 `UNKNOWN`。

`CONTAINS` 命中排除条件时为 `NOT_MATCH`，`MAY_CONTAIN` 命中时为 `RISK`；没有证据不能解释为安全。
## Shopping and order APIs

Authenticated consumers can use `GET /api/v1/cart`, `POST /api/v1/cart/items`, `PUT /api/v1/cart/items/{id}`, and `DELETE /api/v1/cart/items/{id}`. Orders are created from selected cart items with `POST /api/v1/orders`; `GET /api/v1/orders` and `GET /api/v1/orders/{order_id}` return only the current user's orders. Cancellation and mock payment use `POST /api/v1/orders/{order_id}/cancel` and `POST /api/v1/orders/{order_id}/pay`.

Order creation locks inventory rows in stable ID order, revalidates active prices and stock, writes immutable product/specification/price/ingredient-version snapshots, deducts inventory, and removes purchased cart rows in one transaction. A checkout containing multiple merchants must be split into separate orders. Mock payment records a `payment_record`; it never contacts a real payment provider.