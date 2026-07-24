# FoodPlatform

> 基于AI智能筛选与食品信息管理的多角色食品电商平台

## 项目简介

FoodPlatform 是一个面向食品消费场景的多角色电商平台，围绕商品信息、食品成分、营养数据和交易流程提供统一的前后端实现。

系统目前包含消费者、商家和管理员三类主要角色：消费者可以浏览与筛选食品、管理购物车并完成订单；商家可以维护自己的商品和处理订单；管理员可以查看平台数据、管理用户并审核商品。

平台的特色能力是自然语言食品筛选。用户可以用日常语言描述商品类别、需要排除的成分、偏好成分、价格范围和营养要求。系统通过 Qwen 大模型与受控规则共同解析需求，再结合 MySQL 商品数据和 Neo4j 食品知识关系生成可解释的筛选结果。

食品成分、营养及风险信息仅用于商品筛选与信息辅助，不构成医学建议。实际信息应以商品包装标签和权威来源为准。

## 系统架构

```text
React + TypeScript + Vite
            ↓ HTTP / JSON / JWT
        FastAPI Backend
            ↓
       MySQL + Neo4j
            ↓
    Qwen + Controlled Rules
```

- **前端：React + TypeScript + Vite**，负责三类角色的页面、路由、用户状态及API交互。
- **后端：FastAPI**，采用 Router → Service → Repository 分层，提供认证、商品、筛选、交易和工作台接口。
- **数据库：MySQL**，存储用户、角色、商品、库存、收藏、购物车、订单、评价和审核等业务数据。
- **知识图谱：Neo4j**，存储食品、成分、添加剂、风险、品牌和分类之间的知识关系。
- **AI：Qwen大模型 + 规则解析**，负责自然语言条件解析；大模型不可用时自动使用规则解析结果继续运行。

## 功能介绍

### 消费者端

- 用户注册、登录与JWT登录状态恢复
- 首页商品浏览
- 商品分类、关键词和条件搜索
- 商品详情查看
- 食品配料、结构化成分、营养和来源信息展示
- 商品知识图谱查看
- AI自然语言智能筛选
- 用户食品偏好管理
- 商品收藏
- 购物车管理
- 收货地址与结算
- 创建订单、模拟支付、取消订单和确认收货
- 订单列表与订单详情
- 已完成订单商品评价
- 个人中心及用户数据隔离

### 商家端

- 商家工作台
- 当前商家商品、订单和销售数据统计
- 当前商家商品列表
- 商品新增与编辑
- 商品上下架
- 查看购买本商家商品的订单
- 订单状态处理：已支付 → 配送中 → 已完成

商家接口通过JWT中的用户身份定位 `merchant.owner_user_id`，只能访问自己的商品和订单。

### 管理员端

- 平台用户、商家、商品和订单数据统计
- 用户列表
- 按用户名或邮箱搜索用户
- 用户详情查看
- 用户启用和禁用
- 待审核商品查看
- 商品审核通过

管理员功能使用 `ADMIN` 权限保护，不提供密码修改、角色修改或用户删除功能。

## AI能力说明

- **自然语言需求解析**：将用户输入转换为结构化筛选条件。
- **Qwen辅助理解**：补充复杂表达、偏好和分类语义。
- **规则可靠性保障**：明确的排除成分、分类和营养硬约束由受控规则优先保留。
- **失败降级**：Qwen超时、接口失败、JSON无效或Schema校验失败时自动回退规则解析。
- **成分与营养匹配**：结合商品成分、可能含有成分、营养值、价格和分类执行筛选。
- **结果解释**：区分 `MATCH`、`RISK`、`NOT_MATCH` 和 `UNKNOWN`，返回命中原因与证据信息。
- **AI辅助软件开发流程**：项目开发过程中使用AI协助需求分析、架构设计、代码生成、问题定位和测试验证。

Qwen只负责“自然语言 → 结构化筛选条件”，不直接修改数据库，也不代替商品匹配规则。

## 技术栈

### Frontend

- React
- TypeScript
- Vite
- React Router
- Cytoscape.js
- Recharts
- Lucide React

### Backend

- FastAPI
- Pydantic v2
- pydantic-settings
- SQLAlchemy 2
- PyMySQL
- JWT / bcrypt
- Neo4j Python Driver
- HTTPX
- pytest

### Database

- MySQL
- Neo4j

### AI

- Qwen大语言模型
- 受控规则解析器

## 项目目录结构

```text
FoodPlatform/
├─ backend/
│  ├─ app/
│  │  ├─ api/               # FastAPI路由与API版本
│  │  ├─ core/              # 配置、日志、响应和异常处理
│  │  ├─ db/                # MySQL与Neo4j连接
│  │  ├─ dependencies/      # JWT认证和角色依赖
│  │  ├─ models/            # 后端数据模型
│  │  ├─ repositories/      # MySQL与Neo4j数据访问
│  │  ├─ schemas/           # Pydantic请求与响应模型
│  │  ├─ services/          # 业务编排与智能解析
│  │  └─ main.py            # FastAPI应用入口
│  ├─ docs/                 # 后端专项文档
│  ├─ tests/                # pytest测试
│  ├─ .env.example          # 环境变量模板
│  ├─ pyproject.toml
│  └─ README.md
├─ database/
│  ├─ mysql/                # Schema、Seed、视图和存储过程
│  ├─ neo4j/                # 约束、初始化、查询和验证脚本
│  ├─ DATABASE_DESIGN.md
│  ├─ data-mapping.md
│  └─ init-database.ps1
├─ src/
│  ├─ components/           # 公共、商品、地址等组件
│  ├─ layouts/              # 消费者端和工作台布局
│  ├─ pages/
│  │  ├─ consumer/          # 消费者页面
│  │  ├─ merchant/          # 商家页面
│  │  ├─ admin/             # 管理员页面
│  │  └─ knowledge/         # 知识管理页面
│  ├─ services/             # 前端API服务层
│  ├─ store/                # 用户与全局业务状态
│  ├─ styles/               # 全局样式
│  ├─ types/                # TypeScript类型
│  ├─ App.tsx               # 前端路由入口
│  └─ main.tsx
├─ package.json
├─ pnpm-lock.yaml
├─ vite.config.ts
└─ README.md
```

## 运行方式

### 1. 环境要求

- Node.js与pnpm
- Python 3.12至3.14
- MySQL
- Neo4j
- Qwen API Key（仅在启用Qwen时需要）

### 2. 初始化数据库

数据库初始化文件位于 `database/`。初始化脚本会清理目标演示数据，执行前应确认连接目标并备份需要保留的数据。

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

详细说明见 [database/README.md](database/README.md) 和 [database/DATABASE_DESIGN.md](database/DATABASE_DESIGN.md)。应用账号建议遵循 [backend/docs/mysql-user.md](backend/docs/mysql-user.md) 中的最小权限方案。

### 3. 配置后端环境变量

复制环境变量模板：

```powershell
Copy-Item backend\.env.example backend\.env
```

在本地 `backend/.env` 中配置以下项目：

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

`backend/.env` 已被Git忽略。不要将真实密码、JWT Secret、Token或API Key写入代码、README或Git历史。

### 4. 启动后端

```powershell
Set-Location D:\CodexProjects\FoodPlatform
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install --upgrade pip
backend\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

后端启动后可访问：

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`
- 健康检查：`http://127.0.0.1:8000/api/v1/health/ready`

### 5. 启动前端

新建PowerShell窗口：

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

### 6. 运行测试

```powershell
Set-Location D:\CodexProjects\FoodPlatform\backend
.\.venv\Scripts\python.exe -m pytest

Set-Location D:\CodexProjects\FoodPlatform
pnpm build
```

当前代码状态的最近一次本地验证结果：

- 后端：`86 passed`
- 前端：TypeScript检查与Vite生产构建通过
- Vite提示单个JavaScript产物超过500 kB；该提示不阻止构建

## AI辅助开发说明

项目开发过程中使用AI辅助完成以下工作：

- 需求梳理与功能边界分析
- 前后端与双数据库架构设计
- React、FastAPI、SQL和Cypher代码生成
- 数据契约和角色权限核对
- Bug定位与联调修复
- 单元测试、构建和发布前安全检查

AI生成或建议的内容需要经过代码审查、自动化测试和真实环境验证。AI辅助不替代业务规则确认、数据库备份、安全审计或人工验收。

## 注意事项

- 运行项目前必须正确配置MySQL、Neo4j和后端环境变量。
- 启用Qwen时必须在本地环境变量中配置API Key；未启用时系统使用规则解析。
- 不要提交 `.env`、数据库密码、Neo4j密码、JWT Secret、Token、API Key、虚拟环境、依赖目录或数据库备份。
- MySQL负责业务和交易事实，Neo4j负责食品知识关系；两者通过业务编码关联，不依赖Neo4j内部节点ID。
- 用户密码仅保存bcrypt哈希。
- 商家和管理员接口均需要正确的JWT角色权限。
- 当前支付功能为项目内模拟支付，不连接真实支付平台。
- 食品筛选与成分分析结果仅供信息参考。