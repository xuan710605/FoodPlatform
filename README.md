# FoodPlatform

AI 驱动食品智能电商平台

## 项目介绍

FoodPlatform 是一个融合 AI 自然语言理解、食品知识分析和电商业务流程的智能食品平台。系统面向消费者提供商品浏览、搜索、成分与营养筛选、收藏、购物车、订单和评价等完整流程，并通过食品知识图谱和 Qwen 大语言模型，将用户的自然语言需求转换为可执行的结构化条件，给出可解释的匹配、风险和信息不足结论。

食品成分偏好与筛选结果仅用于商品信息辅助，不构成医学建议；实际信息应以商品包装标签为准。

## 技术栈

### 前端

- React
- TypeScript
- Vite
- React Router
- Cytoscape.js：知识图谱可视化
- Recharts：图表展示
- Lucide React：图标组件

### 后端

- FastAPI
- Pydantic v2 / pydantic-settings
- SQLAlchemy 2
- PyMySQL
- JWT、bcrypt
- Neo4j 官方 Python Driver
- HTTPX
- pytest

### 数据与智能能力

- MySQL：关系型业务数据库
- Neo4j：食品知识图谱
- Qwen 大语言模型：自然语言筛选条件解析

## 核心功能

### 消费者端

- 用户注册、登录与 JWT 登录态恢复
- 商品浏览、分类筛选与关键词搜索
- 商品详情、配料、营养、来源和知识图谱查看
- 用户食品成分偏好管理
- 商品收藏
- 购物车数量管理
- 收货地址与结算
- 订单创建、查询、取消、模拟支付和确认收货
- 已完成订单商品评价与评价查询
- 用户中心及个人业务数据隔离

### 智能能力

- 自然语言食品筛选
- Qwen 语义解析
- 确定性规则解析与失败降级
- 用户食品偏好合并
- 食品成分与潜在风险分析
- 糖、脂肪、蛋白质和钠等动态营养条件筛选
- 商品价格与分类条件筛选
- 可解释的匹配原因和证据
- `MATCH`、`RISK`、`NOT_MATCH`、`UNKNOWN` 四类结果

## 系统架构

```text
React Frontend
      ↓ HTTP / JSON / JWT
FastAPI Backend API
      ↓
MySQL + Neo4j
      ↓
Qwen（可选启用，失败时回退规则解析）
```

后端使用清晰的分层结构：

```text
API Router
    ↓
Service
    ↓
Repository
    ↓
MySQL / Neo4j
```

- 前端负责交互、路由、状态管理和结果展示。
- FastAPI 提供认证、商品、筛选、用户和交易接口。
- MySQL 保存用户、商品事实与交易数据。
- Neo4j 保存食品成分、别名、衍生和风险关系。
- Qwen 只参与自然语言条件解析，不直接修改商品事实或执行数据库操作。

## 智能筛选流程

```text
用户输入自然语言
        ↓
Qwen / 受控规则解析
        ↓
结构化 FilterConditions
        ↓
商品分类、价格、成分和营养匹配
        ↓
MATCH / RISK / NOT_MATCH / UNKNOWN
```

判定语义：

- `MATCH`：满足当前已知筛选条件。
- `RISK`：商品可能含有用户排除的成分。
- `NOT_MATCH`：商品明确含有排除成分，或不满足价格、营养等硬条件。
- `UNKNOWN`：成分、营养、价格或知识证据不足，不能判断为安全或匹配。

明确的用户条件由受控规则优先保留，Qwen 不能覆盖已识别的排除成分和营养硬约束。Qwen 超时、接口失败、JSON 无效或校验失败时，系统自动使用规则解析结果继续运行。

## 数据设计

### MySQL 负责

- 用户、角色和权限
- 用户资料、食品偏好和收货地址
- 商家、品牌和商品分类
- 商品、规格、图片、价格和库存
- 原始配料文本与结构化成分快照
- 商品营养数据
- 收藏、购物车和浏览业务
- 订单、订单项和支付记录
- 商品评价
- 商品审核、异常记录和审计日志

商品原始配料文本与结构化成分分别保存。订单项保存商品名称、规格、价格和成分版本快照，避免后续商品修改影响历史订单。

### Neo4j 负责

- 食品商品、成分、添加剂、营养、品牌和分类节点
- 食品明确包含成分关系
- 食品可能包含成分关系
- 成分别名和衍生关系
- 成分风险关系
- 成分替代关系和数据来源

MySQL 与 Neo4j 通过 `product_code`、`ingredient_code`、`brand_code`、`category_code` 等业务编码关联，不依赖 Neo4j 内部节点 ID。

数据库设计、初始化顺序和验证方式见 [database/README.md](database/README.md) 与 [database/DATABASE_DESIGN.md](database/DATABASE_DESIGN.md)。

## 运行方式

### 1. 环境要求

- Node.js 与 pnpm
- Python 3.12–3.14
- MySQL
- Neo4j
- Qwen API Key（可选）

### 2. 初始化数据库

数据库脚本位于 `database/`。初始化脚本会清理目标演示数据库，执行前必须确认连接目标并备份需要保留的数据。

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

应用账号建议使用最小权限，参考 [backend/docs/mysql-user.md](backend/docs/mysql-user.md)。

### 3. 配置后端环境变量

创建本地配置文件：

```powershell
Copy-Item backend\.env.example backend\.env
```

编辑 `backend/.env`，配置：

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=food_platform_app
MYSQL_PASSWORD=your_local_password
MYSQL_DATABASE=food_platform

NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_local_password
NEO4J_DATABASE=neo4j

JWT_SECRET=replace_with_at_least_32_random_characters
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

QWEN_ENABLED=false
QWEN_API_KEY=
QWEN_MODEL=qwen-plus
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_TIMEOUT_SECONDS=8
```

`backend/.env` 已被 Git 忽略。禁止提交真实数据库密码、JWT Secret、Token 或 Qwen API Key。未启用 Qwen 时，智能筛选使用受控规则解析。

### 4. 启动后端

```powershell
Set-Location D:\CodexProjects\FoodPlatform
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install --upgrade pip
backend\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

接口文档：

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- OpenAPI：`http://127.0.0.1:8000/openapi.json`

### 5. 启动前端

新建 PowerShell 窗口：

```powershell
Set-Location D:\CodexProjects\FoodPlatform
pnpm install
$env:VITE_API_BASE_URL='http://127.0.0.1:8000'
pnpm dev
```

访问 `http://127.0.0.1:5173`。

生产构建：

```powershell
pnpm build
pnpm preview
```

未设置 `VITE_API_BASE_URL` 时，前端默认请求 `http://127.0.0.1:8000`。

## 项目目录结构

```text
FoodPlatform/
├─ backend/
│  ├─ app/
│  │  ├─ api/             # FastAPI 路由
│  │  ├─ core/            # 配置、日志、响应和异常
│  │  ├─ db/              # MySQL 与 Neo4j 连接
│  │  ├─ dependencies/    # JWT 与角色依赖
│  │  ├─ models/          # 数据模型
│  │  ├─ repositories/    # 数据访问层
│  │  ├─ schemas/         # Pydantic 请求与响应模型
│  │  ├─ services/        # 业务与智能筛选编排
│  │  └─ main.py          # FastAPI 应用入口
│  ├─ docs/               # 后端专项文档
│  ├─ tests/              # pytest 测试
│  ├─ .env.example
│  ├─ pyproject.toml
│  └─ README.md
├─ database/
│  ├─ mysql/              # Schema、Seed、视图和存储过程
│  ├─ neo4j/              # 约束、Seed、查询和验证脚本
│  ├─ DATABASE_DESIGN.md
│  ├─ data-mapping.md
│  └─ init-database.ps1
├─ src/
│  ├─ components/         # 通用、商品和地址组件
│  ├─ layouts/            # 消费者及工作台布局
│  ├─ pages/              # 消费者、商家、管理员和知识页面
│  ├─ services/           # 前端 API 服务
│  ├─ store/              # 全局用户与业务状态
│  ├─ styles/             # 全局样式
│  ├─ types/              # TypeScript 类型
│  ├─ App.tsx             # 路由入口
│  └─ main.tsx
├─ package.json
├─ pnpm-lock.yaml
├─ vite.config.ts
└─ README.md
```

## 测试结果

在 `final-product-polish` 分支、提交 `641e566c827bc0cd232fd7b9eeef50c8893f5887` 基础上执行：

```powershell
backend\.venv\Scripts\python.exe -m pytest backend
pnpm build
```

当前实际结果：

- 后端测试：`80 passed in 4.71s`
- 前端 TypeScript 检查与 Vite 生产构建：成功
- Vite 构建提示主 JavaScript 产物超过 500 kB；这是体积优化提示，不影响当前构建完成

普通单元测试使用依赖替身，不读取真实数据库密码，也不会清理本地数据库。真实运行前仍需正确配置 MySQL、Neo4j 和后端环境变量。

## 安全说明

- 不提交 `.env`、密码、JWT Secret、Token、API Key 或数据库备份。
- 用户密码仅保存 bcrypt 哈希。
- API 不向客户端返回数据库堆栈或连接凭据。
- Qwen 仅补充语义解析，不能覆盖受控硬条件或修改商品事实。
- 模拟支付接口仅用于项目演示，不连接真实支付平台。
