# FoodPlatform 前端

FoodPlatform前端使用React、TypeScript和Vite，实现消费者端、商家端和管理员端页面，并通过统一API服务访问FastAPI后端。

## 技术栈

- React
- TypeScript
- Vite
- React Router
- Cytoscape.js
- Recharts
- Lucide React

## 页面与路由

### 消费者端

主要路由包括：

- `/`：首页
- `/login`：注册与登录
- `/products`：商品列表与数据库筛选
- `/product/{product_code}`：商品详情
- `/smart-filter`：AI智能筛选
- `/graph/{product_code}`：商品知识图谱
- `/compare`：商品对比
- `/cart`：购物车
- `/checkout`：订单结算
- `/orders/{order_id}/result`：订单结果
- `/account`：个人中心
- `/account/preferences`：食品偏好
- `/account/filter-history`：筛选历史

### 商家端

- `/merchant/dashboard`：商家工作台
- `/merchant/products`：商品管理
- `/merchant/orders`：订单管理

商家页面要求当前用户具有 `MERCHANT` 角色。

### 管理员端

- `/admin/dashboard`：平台统计
- `/admin/users`：用户管理
- `/admin/products`：商品审核

管理员页面要求当前用户具有 `ADMIN` 角色。

## 登录流程

```text
登录表单
  ↓ POST /api/v1/auth/login
保存 localStorage.access_token
  ↓
AppStore保存当前用户
  ↓ 页面刷新
GET /api/v1/users/me恢复用户和roles
  ↓
按角色跳转或显示工作台入口
```

- 登录支持用户名或邮箱。
- `ADMIN` 登录后进入 `/admin/dashboard`。
- `MERCHANT` 登录后进入 `/merchant/dashboard`。
- 普通消费者登录后进入首页。
- 商家和管理员返回消费者端时不会退出登录，消费者导航会保留对应工作台入口。
- Token无效或过期时清除当前登录状态并跳转登录页。

## API调用

API服务集中在 `src/services/`：

- `api.ts`：基础地址、统一请求、Bearer注入、商品与智能筛选
- `account.ts`：当前用户
- `commerce.ts`：登录、购物车、地址和订单
- `favorites.ts`：收藏
- `preferences.ts`：食品偏好
- `reviews.ts`：评价
- `workspace.ts`：商家和管理员工作台

`apiRequest()`会合并现有请求头，并在存在Token时添加：

```http
Authorization: Bearer <access_token>
```

代码不会把Authorization请求头输出到控制台。业务页面通过服务层访问后端，不直接拼接数据库数据。

## 目录结构

```text
src/
├─ components/          # 通用、商品、地址等组件
├─ layouts/             # 消费者布局与工作台布局
├─ pages/
│  ├─ consumer/
│  ├─ merchant/
│  ├─ admin/
│  └─ knowledge/
├─ services/            # API服务
├─ store/               # 用户与全局状态
├─ styles/              # 全局样式
├─ types/               # TypeScript类型
├─ App.tsx              # 路由配置
└─ main.tsx             # 应用入口
```

## 环境变量

前端使用：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

未配置时默认请求 `http://127.0.0.1:8000`。不要在前端环境变量中保存数据库密码、JWT Secret或Qwen API Key。

## 本地启动

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

当前代码最近一次TypeScript检查和Vite生产构建均已通过。构建提示单个JavaScript产物超过500 kB，但不阻止构建。

## 安全与数据说明

- Token仅用于前端认证请求，不应输出到日志或提交到Git。
- 用户、购物车、收藏、订单和工作台数据通过真实后端API读取。
- 页面路由保护不能替代后端权限检查；商家和管理员接口同时由FastAPI角色依赖保护。
- 食品成分与筛选结果只用于信息辅助，不构成医学建议。