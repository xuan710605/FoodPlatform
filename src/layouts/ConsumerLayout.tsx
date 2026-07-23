import { Heart, Menu, Search, ShoppingBag, UserRound, X } from 'lucide-react'
import { useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useApp } from '../store/AppStore'

export function ConsumerLayout() {
  const { cart, favorites, loggedIn } = useApp(); const location = useLocation(); const filterScrollMode = location.pathname === '/products' || location.pathname === '/smart-filter'; const [mobile, setMobile] = useState(false); const [query, setQuery] = useState(''); const navigate = useNavigate()
  const submit = (e: React.FormEvent) => { e.preventDefault(); navigate(`/products?q=${encodeURIComponent(query)}`); setMobile(false) }
  return <div className={`site-shell ${filterScrollMode ? 'filter-scroll-mode' : ''}`}>
    <header className="site-header"><div className="header-inner">
      <Link to="/" className="logo"><span className="logo-mark">知</span><span><b>知味集</b><small>FoodGraph Market</small></span></Link>
      <nav className={`main-nav ${mobile ? 'open' : ''}`}>
        <NavLink to="/" onClick={() => setMobile(false)}>首页</NavLink><NavLink to="/products" onClick={() => setMobile(false)}>商品分类</NavLink><NavLink to="/smart-filter" onClick={() => setMobile(false)}>智能筛选</NavLink><NavLink to="/compare" onClick={() => setMobile(false)}>商品对比</NavLink>
        <form className="nav-search mobile-only" onSubmit={submit}><Search/><input value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="搜索商品、品牌或成分"/></form>
      </nav>
      <form className="nav-search desktop-search" onSubmit={submit}><Search/><input value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="搜索商品、品牌或成分"/></form>
      <div className="nav-tools"><Link to="/account?tab=favorites" className="nav-icon"><Heart/><span>收藏</span>{favorites.length>0&&<em>{favorites.length}</em>}</Link><Link to="/cart" className="nav-icon"><ShoppingBag/><span>购物车</span><em>{cart.reduce((s,x)=>s+x.quantity,0)}</em></Link><Link to={loggedIn?'/account':'/login'} className="nav-icon"><UserRound/><span>{loggedIn?'个人中心':'登录'}</span></Link><button className="mobile-menu" onClick={()=>setMobile(!mobile)}>{mobile?<X/>:<Menu/>}</button></div>
    </div></header>
    <main><Outlet/></main>
    <footer className="site-footer"><div className="footer-main"><div className="footer-brand"><div className="logo"><span className="logo-mark">知</span><span><b>知味集</b><small>让每一次选择都有依据</small></span></div><p>基于可信商品标签与知识图谱，为你提供可追溯的食品成分筛选与购物体验。</p></div><div><h4>平台服务</h4><a>食品信息免责声明</a><a>数据来源说明</a><a>成分纠错</a></div><div><h4>关于我们</h4><a>用户协议</a><a>隐私政策</a><a>商家入驻</a></div><div><h4>联系我们</h4><a>service@zhiweiji.mock</a><a>400-800-0718</a><a>工作日 9:00–18:00</a></div></div><div className="footer-bottom"><span>© 2026 知味集 · 前端演示原型</span><span>食品信息仅供筛选参考，不构成医学建议或食品安全认证。</span></div></footer>
  </div>
}
