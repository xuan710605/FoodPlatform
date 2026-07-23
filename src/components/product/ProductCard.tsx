import { GitCompareArrows, Heart, ShoppingBag, Star } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useApp } from '../../store/AppStore'
import type { Product } from '../../types'
import { MatchBadge } from '../common/UI'
import { SafeImage } from '../common/SafeImage'
import { productCodeOf } from '../../services/api'
import { addCartItem } from '../../services/commerce'

export function ProductCard({ product, compact = false }: { product: Product; compact?: boolean }) {
  const { addCart, toggleFavorite, toggleCompare, favorites, compare } = useApp()
  const location = useLocation()
  const sourcePath = `${location.pathname}${location.search}`
  const add = async () => { try { await addCartItem(productCodeOf(product)); addCart(product.id) } catch { addCart(product.id) } }
  return <article className={`product-card ${compact ? 'compact' : ''}`}>
    <div className="product-image-wrap">
      <Link to={`/product/${productCodeOf(product)}`} state={{from:sourcePath}}><SafeImage src={product.image} alt={product.name}/></Link>
      <button className={`floating-btn ${favorites.includes(product.id) ? 'active' : ''}`} onClick={() => toggleFavorite(product.id)} aria-label="收藏"><Heart size={18}/></button>
      {product.originalPrice && <span className="discount">限时 -14%</span>}
    </div>
    <div className="product-card-body">
      <div className="brand-line"><span>{product.brand}</span><span><Star size={13} fill="currentColor"/> {product.rating}</span></div>
      <Link to={`/product/${productCodeOf(product)}`} state={{from:sourcePath}} className="product-name">{product.name}</Link>
      <div className="tag-row">{product.ingredients.slice(0,3).map((x) => <span key={x}>{x}</span>)}</div>
      <MatchBadge status={product.status} compact/>
      {!compact && <p className="product-reason">{product.reason}</p>}
      <div className="product-footer"><div className="price"><strong>¥{product.price}</strong>{product.originalPrice && <del>¥{product.originalPrice}</del>}</div><span className="sales">月售 {product.sales}</span></div>
      <div className="card-actions"><button className={`btn ghost icon ${compare.includes(product.id) ? 'selected' : ''}`} onClick={() => toggleCompare(product.id)}><GitCompareArrows size={17}/>对比</button><button className="btn primary grow" onClick={add}><ShoppingBag size={17}/>加入购物车</button></div>
    </div>
  </article>
}
