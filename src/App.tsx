import { AlertTriangle, Boxes, ClipboardCheck, ClipboardList, FileClock, FileText, GitCompareArrows, GitFork, History, LayoutDashboard, ListTree, Package, PackagePlus, ScrollText, ShieldCheck, ShoppingBag, Store, Users } from 'lucide-react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { ConsumerLayout } from './layouts/ConsumerLayout'
import { WorkspaceLayout, type NavItem } from './layouts/WorkspaceLayout'
import { AccountPage, FilterHistoryPage, PreferencesPage } from './pages/consumer/AccountPages'
import { CartPage, CheckoutPage, OrderResultPage } from './pages/consumer/CommercePages'
import { ComparePage } from './pages/consumer/ComparePage'
import { GraphPage } from './pages/consumer/GraphPage'
import { HomePage } from './pages/consumer/HomePage'
import { LoginPage } from './pages/consumer/LoginPage'
import { ProductDetailPage } from './pages/consumer/ProductDetailPage'
import { ProductsPage } from './pages/consumer/ProductsPage'
import { SmartFilterPage } from './pages/consumer/SmartFilterPage'
import { AdminDashboard, AnomalyCenter, AuditLog, OrderSupervision, ProductReview, UserManagement } from './pages/admin/AdminPages'
import { InventoryPage, MerchantDashboard, MerchantOrders, MerchantProducts, ProductPublish } from './pages/merchant/MerchantPages'
import { GraphVersions, KnowledgeGraphManagement, PendingTerms, RelationManagement } from './pages/knowledge/KnowledgePages'

const merchantNav:NavItem[]=[{label:'商家工作台',path:'/merchant',icon:LayoutDashboard},{label:'商品管理',path:'/merchant/products',icon:Package},{label:'发布商品',path:'/merchant/products/new',icon:PackagePlus},{label:'商家订单',path:'/merchant/orders',icon:ShoppingBag},{label:'库存管理',path:'/merchant/inventory',icon:Boxes}]
const adminNav:NavItem[]=[{label:'管理驾驶舱',path:'/admin',icon:LayoutDashboard},{label:'商品审核',path:'/admin/reviews',icon:ClipboardCheck},{label:'用户与商家',path:'/admin/users',icon:Users},{label:'异常数据中心',path:'/admin/anomalies',icon:AlertTriangle},{label:'订单监管',path:'/admin/orders',icon:ShoppingBag},{label:'审计日志',path:'/admin/audit',icon:ScrollText}]
const knowledgeNav:NavItem[]=[{label:'图谱管理',path:'/knowledge',icon:GitFork},{label:'关系管理',path:'/knowledge/relations',icon:ListTree},{label:'待确认词条',path:'/knowledge/pending',icon:FileClock},{label:'版本与影响',path:'/knowledge/versions',icon:GitCompareArrows},{label:'审核协同',path:'/admin/reviews',icon:ShieldCheck}]

function NotFound(){return <div className="page"><div className="container"><div className="card empty-state"><div className="empty-illustration">404</div><h1>页面走丢了</h1><p>这个 Mock 路由不存在，返回首页继续浏览。</p><a className="btn primary" href="/">返回首页</a></div></div></div>}

export default function App(){return <Routes>
  <Route path="/login" element={<LoginPage/>}/>
  <Route element={<ConsumerLayout/>}>
    <Route index element={<HomePage/>}/><Route path="products" element={<ProductsPage/>}/><Route path="smart-filter" element={<SmartFilterPage/>}/><Route path="product/:id" element={<ProductDetailPage/>}/><Route path="graph/:id" element={<GraphPage/>}/><Route path="compare" element={<ComparePage/>}/><Route path="cart" element={<CartPage/>}/><Route path="checkout" element={<CheckoutPage/>}/><Route path="order-result" element={<OrderResultPage/>}/><Route path="account" element={<AccountPage/>}/><Route path="account/preferences" element={<PreferencesPage/>}/><Route path="account/filter-history" element={<FilterHistoryPage/>}/>
  </Route>
  <Route path="/merchant" element={<WorkspaceLayout role="商家" title="知味商家中心" nav={merchantNav}/> }><Route index element={<MerchantDashboard/>}/><Route path="products" element={<MerchantProducts/>}/><Route path="products/new" element={<ProductPublish/>}/><Route path="orders" element={<MerchantOrders/>}/><Route path="inventory" element={<InventoryPage/>}/></Route>
  <Route path="/admin" element={<WorkspaceLayout role="平台管理员" title="知味运营中心" nav={adminNav} accent="olive"/> }><Route index element={<AdminDashboard/>}/><Route path="reviews" element={<ProductReview/>}/><Route path="users" element={<UserManagement/>}/><Route path="anomalies" element={<AnomalyCenter/>}/><Route path="orders" element={<OrderSupervision/>}/><Route path="audit" element={<AuditLog/>}/></Route>
  <Route path="/knowledge" element={<WorkspaceLayout role="知识管理员" title="知味知识中心" nav={knowledgeNav} accent="sand"/> }><Route index element={<KnowledgeGraphManagement/>}/><Route path="relations" element={<RelationManagement/>}/><Route path="pending" element={<PendingTerms/>}/><Route path="versions" element={<GraphVersions/>}/></Route>
  <Route path="/home" element={<Navigate to="/" replace/>}/><Route path="*" element={<NotFound/>}/>
 </Routes>}
