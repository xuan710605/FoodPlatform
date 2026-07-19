# FoodPlatform FastAPI backend

Version `0.3.0` provides the backend foundation and the first read-only APIs. It does not implement authentication, orders, payment, Qwen, graph writes, or frontend integration.

## Architecture

```text
API routes -> Services -> Repositories -> MySQL / Neo4j
```

- MySQL is the source of product, price, inventory, raw ingredient, nutrition, and audit-state facts.
- Neo4j supplies approved knowledge relationships and explanatory risk paths.
- External identifiers are business codes such as `product_code`; Neo4j internal IDs are never exposed.
- The implementation is synchronous throughout. SQLAlchemy's bounded connection pool and the Neo4j driver's pool keep the code easy to maintain for this course project without mixing sync and async database APIs.

## Requirements and verified dependency set

The local installation was performed with Python 3.14.6. The resolved core versions were FastAPI 0.128.8, Uvicorn 0.40.0, Pydantic 2.12.5, pydantic-settings 2.12.0, SQLAlchemy 2.0.51, PyMySQL 1.1.3, cryptography 46.0.7, Neo4j Driver 6.1.0, pytest 9.0.3, and HTTPX 0.28.1. `pyproject.toml` uses narrow version ranges rather than unbounded `latest` dependencies.

## Setup

```powershell
Set-Location D:\CodexProjects\FoodPlatform
python -m venv backend\.venv
Copy-Item backend\.env.example backend\.env
Set-Location backend
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Edit `backend/.env` and replace both `change_me` values. Never commit that file. The application requires `MYSQL_PASSWORD` and `NEO4J_PASSWORD`; missing values produce a configuration validation error without printing a secret.

Recommended minimum MySQL account setup (run manually as a database administrator and choose a strong password):

```sql
CREATE USER IF NOT EXISTS 'food_platform_app'@'localhost' IDENTIFIED BY 'replace_with_a_strong_secret';
GRANT SELECT ON food_platform.* TO 'food_platform_app'@'localhost';
```

The API never changes users or the root password. For this read-only stage, `SELECT` is sufficient.

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

Registration, login, JWT authorization, preferences, cart, orders, payment, merchant/admin writes, Qwen calls, graph mutation, background jobs, Docker deployment, and frontend API replacement remain intentionally out of scope.

## Troubleshooting

- PowerShell blocks activation: use the process-scoped execution-policy command above or call `.venv\Scripts\python.exe` directly.
- MySQL connection refused: verify the service, host/port, database, and least-privilege account; do not switch the code default to root.
- Neo4j authentication failed: verify `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE` in `.env`.
- Port 8000 is occupied: choose another `--port` and update the caller.
- CORS rejected: add the exact trusted frontend origin to comma-separated `CORS_ORIGINS`; wildcard origins are rejected.

Do not commit `.env`, `.venv`, logs, caches, passwords, or database data files.
