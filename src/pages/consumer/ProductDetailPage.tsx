import { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, ChevronRight, GitFork, Heart, Minus, Plus, RefreshCw, ShieldCheck, ShoppingBag, Star, Store } from 'lucide-react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { InlineNotice, MatchBadge, Modal } from '../../components/common/UI'
import { SafeImage } from '../../components/common/SafeImage'
import { useApp } from '../../store/AppStore'
import { getProductDetail, resolveProductCode, type ApiProductDetail, type ApiProductIngredient } from '../../services/api'
import type { MatchStatus } from '../../types'
import { listProductReviews, type ApiReview } from '../../services/consumer'

const statusMap: Record<string, MatchStatus> = {
  FULL_MATCH: '完全匹配',
  RISK: '存在风险',
  NOT_MATCH: '不匹配',
  INFORMATION_INSUFFICIENT: '信息不足',
}
const auditLabels: Record<string, string> = { APPROVED: '已通过', PENDING: '待审核', REJECTED: '已驳回', NEED_MORE_INFO: '需补充' }
const basisLabels: Record<string, string> = { PER_100G: '每100g', PER_100ML: '每100mL', PER_SERVING: '每份' }
const valueOrEmpty = (value: string | null, suffix = '') => value === null ? '暂无数据' : `${value}${suffix}`

export function ProductDetailPage() {
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const code = resolveProductCode(id)
  const [product, setProduct] = useState<ApiProductDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [qty, setQty] = useState(1)
  const [tab, setTab] = useState('ingredients')
  const [ingredient, setIngredient] = useState<ApiProductIngredient | null>(null)
  const [main, setMain] = useState('')
  const [reviews, setReviews] = useState<ApiReview[]>([])
  const { addCart, toggleFavorite, toggleCompare, trackProductView, favorites, loggedIn, currentUser } = useApp()

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    setProduct(null)
    getProductDetail(code)
      .then(next => {
        if (!active) return
        setProduct(next)
        setMain(next.images.find(image => image.image_type === 'MAIN')?.image_url || next.images[0]?.image_url || '')
      })
      .catch(reason => {
        if (!active) return
        setError(reason instanceof Error ? reason.message : '商品详情加载失败')
      })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [code, reloadKey])

  useEffect(() => { let active=true; listProductReviews(code).then(data=>{if(active)setReviews(data.items)}).catch(()=>{if(active)setReviews([])}); return()=>{active=false} }, [code, reloadKey])

  useEffect(() => {
    if (!currentUser || !product) return
    trackProductView({
      id: product.id,
      productCode: product.product_code,
      name: product.name,
      brand: product.brand,
      image: product.images.find(image => image.image_type === 'MAIN')?.image_url || product.images[0]?.image_url || '',
    })
  }, [currentUser?.id, product?.product_code])

  const defaultSpec = useMemo(() => product?.specs.find(spec => spec.is_default) || product?.specs[0], [product])
  const gallery = product?.images.map(image => image.image_url).filter(Boolean) || []
  const ingredients = product?.contains.filter(item => item.entity_type !== 'ADDITIVE') || []
  const additives = product?.contains.filter(item => item.entity_type === 'ADDITIVE') || []
  const routeState = location.state as { from?: unknown } | null
  const sourcePath = typeof routeState?.from === 'string' && !routeState.from.startsWith('/graph/') ? routeState.from : '/products'
  const goBack = () => navigate(sourcePath, { replace: true })

  if (loading) return <div className="page"><div className="container"><div className="card empty-state"><h3>正在加载商品详情</h3><p>正在读取数据库中的商品、成分和营养信息。</p></div></div></div>
  if (error || !product) return <div className="page"><div className="container"><button className="btn ghost" onClick={goBack}><ArrowLeft size={17}/>返回商品列表</button><div className="card empty-state"><h3>商品详情加载失败</h3><p>{error || '未获取到商品数据'}</p><button className="btn primary" onClick={() => setReloadKey(value => value + 1)}><RefreshCw size={16}/>重新加载</button></div></div></div>

  const matchStatus = statusMap[product.match_status] || '信息不足'
  const addToCart = async () => { await addCart(product.id, qty) }
  return <div className="page"><div className="container">
    <button className="btn ghost" style={{ marginBottom: 12 }} onClick={goBack}><ArrowLeft size={17}/>{sourcePath === '/products' ? '返回商品列表' : '返回来源页'}</button>
    <div className="breadcrumbs"><Link to="/">首页</Link><span>/</span><Link to="/products">{product.category}</Link><span>/</span><span>{product.name}</span></div>
    <div className="detail-grid">
      <section className="gallery">
        <div className="gallery-thumbs">{gallery.map((image, index) => <button key={`${image}-${index}`} className={main === image ? 'active' : ''} onClick={() => setMain(image)}><SafeImage src={image} alt={`${product.name}图片${index + 1}`}/></button>)}</div>
        <div className="gallery-main"><SafeImage src={main} alt={product.name}/></div>
      </section>
      <section className="detail-info">
        <div className="detail-meta"><span>{product.brand}</span><span>{product.category}</span><span><Star size={13} fill="currentColor"/> {product.average_rating === null ? '暂无评分' : product.average_rating}</span></div>
        <h1>{product.name}</h1>
        <p>{product.subtitle || product.description || '暂无商品介绍'}</p>
        <div className="detail-price"><strong>{defaultSpec?.sale_price === null || !defaultSpec ? '暂无价格' : `¥${defaultSpec.sale_price}`}</strong>{defaultSpec?.market_price && <del>¥{defaultSpec.market_price}</del>}<small>已售 {product.sales_count} 件</small></div>
        <div className="match-summary soft-card"><MatchBadge status={matchStatus}/><p><ShieldCheck size={15}/>{product.match_reason || '暂无匹配说明'}{product.evidence_text ? `。${product.evidence_text}` : ''}</p></div>
        <div className="spec-row"><span>规格</span><button className="spec-button">{defaultSpec?.spec_name || '暂无规格'}</button></div>
        <div className="spec-row"><span>库存</span><span className="muted">{defaultSpec?.stock_quantity === null || !defaultSpec ? '暂无数据' : `现货 ${defaultSpec.stock_quantity} 件`}</span></div>
        <div className="spec-row"><span>数量</span><div className="quantity"><button onClick={() => setQty(Math.max(1, qty - 1))}><Minus size={14}/></button><input value={qty} readOnly/><button onClick={() => setQty(qty + 1)}><Plus size={14}/></button></div></div>
        <div className="buy-actions"><button className="btn secondary large" onClick={async () => { if (!loggedIn) { navigate('/login'); return } await addToCart(); navigate('/cart') }}>立即购买</button><button className="btn primary large" onClick={addToCart}><ShoppingBag/>加入购物车</button><button className={`btn ghost large ${favorites.includes(product.id) ? 'selected' : ''}`} onClick={() => toggleFavorite(product.id)}><Heart/></button><button className="btn ghost large" onClick={() => toggleCompare(product.id)}>加入对比</button></div>
        <div className="seller-card card"><span><b><Store size={16}/> {product.merchant.name}</b><small>商家编码：{product.merchant.merchant_code}</small></span></div>
      </section>
    </div>
    <div className="detail-tabs">{[['ingredients', '成分与配料'], ['nutrition', '营养成分'], ['source', '信息来源'], ['reviews', '用户评价']].map(([key, label]) => <button key={key} className={tab === key ? 'active' : ''} onClick={() => setTab(key)}>{label}</button>)}</div>
    <div className="detail-content">
      {tab === 'ingredients' && <><section className="detail-section card"><h3>商品匹配摘要</h3><InlineNotice tone={matchStatus === '完全匹配' ? 'success' : matchStatus === '不匹配' ? 'danger' : 'warning'} title={matchStatus}>{product.match_reason || '暂无匹配说明'}</InlineNotice></section><section className="detail-section card"><h3>原始配料表</h3><p className="raw-label">{product.raw_ingredient_text || '暂无数据'}</p>{product.allergen_notice && <p className="muted">过敏原提示：{product.allergen_notice}</p>}<div className="ingredient-zones"><IngredientZone title="主要配料" items={ingredients} onSelect={setIngredient}/><IngredientZone title="食品添加剂" items={additives} onSelect={setIngredient}/><IngredientZone title="可能含有" items={product.may_contain} onSelect={setIngredient}/><IngredientZone title="未识别成分" items={product.unknown} onSelect={setIngredient}/></div></section></>}
      {tab === 'nutrition' && <section className="detail-section card"><h3>营养成分表</h3>{product.nutrition.length === 0 ? <p className="muted">暂无数据</p> : <table className="nutrition-table"><thead><tr><th>营养项目</th><th>数值</th><th>计量基准</th></tr></thead><tbody>{product.nutrition.map(item => <tr key={`${item.nutrient_code}-${item.basis}`}><td>{item.nutrient_name}</td><td>{valueOrEmpty(item.value, item.unit)}</td><td>{basisLabels[item.basis] || item.basis}{item.basis_quantity ? `（${item.basis_quantity}${item.unit}）` : ''}</td></tr>)}</tbody></table>}</section>}
      {tab === 'source' && <section className="detail-section card"><h3>信息来源与审核状态</h3><div className="form-grid"><div><span className="muted">来源</span><p>{product.info_source || '暂无数据'}</p></div><div><span className="muted">审核状态</span><p><span className="status-pill success">{auditLabels[product.audit_status] || product.audit_status}</span></p></div><div><span className="muted">最近更新时间</span><p>{new Date(product.updated_at).toLocaleString('zh-CN')}</p></div><div><span className="muted">成分版本</span><p>{product.ingredient_version === null ? '暂无数据' : `v${product.ingredient_version}`}</p></div></div><Link className="btn primary" to={`/graph/${product.product_code}`}><GitFork/>查看完整图谱追溯</Link></section>}
      {tab === 'reviews' && <section className="detail-section card"><h3>用户评价 · {product.review_count}</h3><p>平均评分：{product.average_rating === null ? '暂无数据' : `${product.average_rating} / 5`}</p>{reviews.length?reviews.map(review=><article className="order-head" style={{padding:'14px 0'}} key={review.review_code}><div><b>{review.username} · {'★'.repeat(review.rating)}</b><p>{review.review_text||'用户未填写文字评价'}</p><small className="muted">{new Date(review.reviewed_at).toLocaleString('zh-CN')}</small></div></article>):<p className="muted">暂无已发布评价</p>}</section>}
    </div>
    <Modal open={!!ingredient} title={`${ingredient?.name || ''} · 成分信息`} onClose={() => setIngredient(null)} footer={<><button className="btn ghost" onClick={() => setIngredient(null)}>关闭</button><Link className="btn primary" to={`/graph/${product.product_code}`}>在图谱中查看 <ChevronRight size={15}/></Link></>}><div className="node-detail"><small>标准名称</small><h3>{ingredient?.name}</h3><p>业务编码：{ingredient?.entity_code || '暂无数据'}</p><div className="tag-row"><span>{ingredient?.audit_status || '暂无审核状态'}</span><span>来源：{ingredient?.source_code || '暂无数据'}</span><span>置信度：{ingredient?.confidence ?? '暂无数据'}</span></div></div></Modal>
  </div></div>
}

function IngredientZone({ title, items, onSelect }: { title: string; items: ApiProductIngredient[]; onSelect: (item: ApiProductIngredient) => void }) {
  return <div className="ingredient-zone"><h4>{title}</h4>{items.length ? items.map(item => <button onClick={() => onSelect(item)} key={`${item.relation_type}-${item.entity_code}`}>{item.name}</button>) : <span className="muted">暂无数据</span>}</div>
}