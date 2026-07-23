import { GitCompareArrows, Heart, ShoppingBag, Star } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useApp } from '../../store/AppStore'
import type { ProductCardData } from '../../types'
import { MatchBadge } from '../common/UI'
import { SafeImage } from '../common/SafeImage'
import { productCodeOf } from '../../services/api'

export function ProductCard({ product, compact = false }: { product: ProductCardData; compact?: boolean }) {
  const { addCart, toggleFavorite, toggleCompare, favorites, compare } = useApp()
  const location = useLocation()
  const sourcePath = `${location.pathname}${location.search}`
  const add = () => { void addCart(product.id) }
  return <article className={`product-card ${compact ? 'compact' : ''}`}>
    <div className="product-image-wrap">
      <Link to={`/product/${productCodeOf(product)}`} state={{from:sourcePath}}><SafeImage src={product.image} alt={product.name}/></Link>
      <button className={`floating-btn ${favorites.includes(product.id) ? 'active' : ''}`} onClick={() => toggleFavorite(product.id)} aria-label="收藏"><Heart size={18}/></button>
      {product.originalPrice && <span className="discount">限时 -14%</span>}
    </div>
    <div className="product-card-body">
      <div className="brand-line"><span>{product.brand}</span><span><Star size={13} fill="currentColor"/> {product.rating === null ? '暂无评分' : product.rating}</span></div>
      <Link to={`/product/${productCodeOf(product)}`} state={{from:sourcePath}} className="product-name">{product.name}</Link>
      <div className="tag-row">{product.ingredients.slice(0,3).map((name) => <span key={name}>{name}</span>)}</div>
      <MatchBadge status={product.status} compact/>
      {!compact && <p className="product-reason">{product.reason || '暂无匹配说明'}</p>}
      <div className="product-footer"><div className="price"><strong>{product.price === null ? '暂无价格' : `¥${product.price}`}</strong>{product.originalPrice && <del>¥{product.originalPrice}</del>}</div><span className="sales">{product.sales === null ? '暂无销量' : `月售 ${product.sales}`}</span></div>
      <div className="card-actions"><button className={`btn ghost icon ${compare.includes(product.id) ? 'selected' : ''}`} onClick={() => toggleCompare(product.id)}><GitCompareArrows size={17}/>对比</button><button className="btn primary grow" onClick={add}><ShoppingBag size={17}/>加入购物车</button></div>
    </div>
  </article>
}