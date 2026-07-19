# 知味集 · 食品成分智能筛选电商平台

基于 React、TypeScript 与 Vite 的完整前端 UI 原型。当前版本只使用本地 Mock 数据，不连接 Qwen、Neo4j、MySQL、支付渠道或任何业务后端。

## 启动

```bash
pnpm install
pnpm dev
```

生产构建：

```bash
pnpm build
pnpm preview
```

## 主要路由

### 消费者端

- `/login` 登录与注册
- `/` 首页
- `/products` 商品列表
- `/smart-filter` 智能筛选
- `/product/1` 商品详情
- `/graph/1` 知识图谱追溯
- `/compare` 商品对比
- `/cart` 购物车
- `/checkout` 确认订单
- `/order-result` 订单结果
- `/account` 个人中心
- `/account/preferences` 成分偏好
- `/account/filter-history` 智能筛选历史

### 商家端

- `/merchant` 商家工作台
- `/merchant/products` 商品管理
- `/merchant/products/new` 商品发布与编辑
- `/merchant/orders` 商家订单
- `/merchant/inventory` 库存管理

### 平台管理端

- `/admin` 管理驾驶舱
- `/admin/reviews` 商品审核
- `/admin/users` 用户与商家管理
- `/admin/anomalies` 异常数据中心
- `/admin/orders` 订单监管
- `/admin/audit` 审计日志

### 知识管理员端

- `/knowledge` 知识图谱管理
- `/knowledge/relations` 关系管理
- `/knowledge/pending` 待确认词条
- `/knowledge/versions` 图谱版本与影响分析

## 数据与组件

- Mock 数据：`src/mock/data.ts`
- 商品图片：公开图片 URL，统一通过 `SafeImage` 加载，失败时显示本地 SVG 占位图
- 知识图谱：Cytoscape.js
- 图表：Recharts
- 图标：Lucide React

## 业务判定规则

- 明确含有排除成分：不匹配
- 标签提示“可能含有”：存在风险
- 成分缺失、未知或冲突：信息不足
- 硬约束优先于价格、销量和推荐度
- AI 只用于受控解析与解释，不修改商品事实

## 数据库脚本与验证

数据库文件位于 `database/`，正确本地路径为 `D:\CodexProjects\FoodPlatform`。当前脚本以 MySQL 9.7.1 和 Neo4j 2026.06.0 为兼容目标；MySQL 初始化及过程最小业务测试已在 9.7.1 完成，Neo4j 脚本需在具备目标库凭据的环境中运行 `database/neo4j/verify.cypher` 后，方可认定实际导入通过。完整说明见 [database/README.md](database/README.md)。

关系语义严格区分明确含有、可能含有和信息不足；“未查到关系”不代表绝对安全。跨库只使用 `product_code`、`ingredient_code`、`brand_code` 等业务编码，不依赖 Neo4j 内部节点 ID。商品原始配料文本与结构化成分分别保存。