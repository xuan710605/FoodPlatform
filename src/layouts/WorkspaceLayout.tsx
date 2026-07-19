import { Bell, ChevronLeft, ChevronRight, LogOut, Menu, Search, type LucideIcon } from 'lucide-react'
import { useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'

export interface NavItem { label: string; path: string; icon: LucideIcon }

export function WorkspaceLayout({ role, title, nav, accent = 'sage' }: { role: string; title: string; nav: NavItem[]; accent?: string }) {
  const [collapsed, setCollapsed] = useState(false); const [mobile, setMobile] = useState(false)
  return <div className={`workspace ${collapsed ? 'collapsed' : ''} accent-${accent}`}>
    <aside className={`workspace-side ${mobile ? 'mobile-open' : ''}`}><div className="workspace-logo"><Link to="/" className="logo-mark">知</Link>{!collapsed&&<span><b>{title}</b><small>{role}</small></span>}<button className="side-close" onClick={()=>setMobile(false)}><ChevronLeft/></button></div><nav>{nav.map(({label,path,icon:Icon})=><NavLink key={path} to={path} end={path.split('/').length<=3} onClick={()=>setMobile(false)}><Icon/><span>{label}</span></NavLink>)}</nav><div className="side-bottom"><Link to="/"><LogOut/><span>返回消费者端</span></Link><button onClick={()=>setCollapsed(!collapsed)}>{collapsed?<ChevronRight/>:<ChevronLeft/>}<span>收起导航</span></button></div></aside>
    {mobile&&<div className="side-scrim" onClick={()=>setMobile(false)}/>}<section className="workspace-main"><header className="workspace-top"><button className="mobile-menu" onClick={()=>setMobile(true)}><Menu/></button><div className="workspace-search"><Search/><input placeholder="搜索商品、订单或任务"/></div><div className="workspace-user"><button className="icon-btn"><Bell/><em>3</em></button><div className="avatar">顾</div><span><b>顾岚</b><small>{role}</small></span></div></header><div className="workspace-content"><Outlet/></div></section>
  </div>
}
