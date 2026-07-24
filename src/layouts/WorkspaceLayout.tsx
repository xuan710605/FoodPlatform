import { Bell, ChevronLeft, ChevronRight, LogOut, Menu, Search, type LucideIcon } from 'lucide-react'
import { useState } from 'react'
import { Link, Navigate, NavLink, Outlet, useLocation } from 'react-router-dom'
import { useApp } from '../store/AppStore'

export interface NavItem { label: string; path: string; icon: LucideIcon }

export function WorkspaceLayout({ role, title, nav, accent = 'sage', allowedRoles = [] }: { role: string; title: string; nav: NavItem[]; accent?: string; allowedRoles?: string[] }) {
  const [collapsed,setCollapsed]=useState(false);const [mobile,setMobile]=useState(false);const {currentUser,userLoading}=useApp();const location=useLocation()
  if(userLoading)return <div className="loading-block">正在验证登录状态…</div>
  if(!currentUser)return <Navigate to="/login" state={{from:location.pathname}} replace/>
  if(allowedRoles.length&&!allowedRoles.some(item=>currentUser.roles.includes(item as never)))return <Navigate to="/" replace/>
  const displayName=currentUser.username;const initial=displayName.slice(0,1).toUpperCase()
  return <div className={`workspace ${collapsed?'collapsed':''} accent-${accent}`}>
    <aside className={`workspace-side ${mobile?'mobile-open':''}`}><div className="workspace-logo"><Link to="/" className="logo-mark">知</Link>{!collapsed&&<span><b>{title}</b><small>{role}</small></span>}<button className="side-close" onClick={()=>setMobile(false)}><ChevronLeft/></button></div><nav>{nav.map(({label,path,icon:Icon})=><NavLink key={path} to={path} end onClick={()=>setMobile(false)}><Icon/><span>{label}</span></NavLink>)}</nav><div className="side-bottom"><Link to="/"><LogOut/><span>返回消费者端</span></Link><button onClick={()=>setCollapsed(!collapsed)}>{collapsed?<ChevronRight/>:<ChevronLeft/>}<span>收起导航</span></button></div></aside>
    {mobile&&<div className="side-scrim" onClick={()=>setMobile(false)}/>}<section className="workspace-main"><header className="workspace-top"><button className="mobile-menu" onClick={()=>setMobile(true)}><Menu/></button><div className="workspace-search"><Search/><input placeholder="搜索当前工作台数据"/></div><div className="workspace-user"><button className="icon-btn"><Bell/></button><div className="avatar">{initial}</div><span><b>{displayName}</b><small>{role}</small></span></div></header><div className="workspace-content"><Outlet/></div></section>
  </div>
}