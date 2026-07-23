import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { getCurrentUser, type CurrentUser } from '../services/account'

type CartLine={productId:number;quantity:number;selected:boolean}
type Toast={id:number;message:string;tone:'success'|'error'|'info'}
interface AppState{cart:CartLine[];favorites:number[];compare:number[];loggedIn:boolean;currentUser:CurrentUser|null;userLoading:boolean;toasts:Toast[];refreshUser:()=>Promise<void>;addCart:(id:number,quantity?:number)=>void;updateCart:(id:number,patch:Partial<CartLine>)=>void;removeCart:(id:number)=>void;toggleFavorite:(id:number)=>void;toggleCompare:(id:number)=>void;login:()=>void;logout:()=>void;notify:(message:string,tone?:Toast['tone'])=>void}
const Context=createContext<AppState|null>(null)
const readFavorites=()=>{try{return JSON.parse(localStorage.getItem('foodplatform_favorites')||'[]') as number[]}catch{return []}}
export function AppProvider({children}:{children:ReactNode}){
 const [cart,setCart]=useState<CartLine[]>([{productId:1,quantity:1,selected:true},{productId:13,quantity:2,selected:true},{productId:15,quantity:1,selected:false}])
 const [favorites,setFavorites]=useState<number[]>(readFavorites);const [compare,setCompare]=useState<number[]>([1,2,16]);const [loggedIn,setLoggedIn]=useState(()=>Boolean(localStorage.getItem('access_token')));const [currentUser,setCurrentUser]=useState<CurrentUser|null>(null);const [userLoading,setUserLoading]=useState(false);const [toasts,setToasts]=useState<Toast[]>([])
 const notify=(message:string,tone:Toast['tone']='success')=>{const id=Date.now();setToasts(v=>[...v,{id,message,tone}]);window.setTimeout(()=>setToasts(v=>v.filter(x=>x.id!==id)),2300)}
 const refreshUser=async()=>{if(!localStorage.getItem('access_token')){setCurrentUser(null);setLoggedIn(false);return}setUserLoading(true);try{setCurrentUser(await getCurrentUser());setLoggedIn(true)}catch{setCurrentUser(null);setLoggedIn(false)}finally{setUserLoading(false)}}
 useEffect(()=>{if(loggedIn)void refreshUser()},[loggedIn])
 useEffect(()=>{localStorage.setItem('foodplatform_favorites',JSON.stringify(favorites))},[favorites])
 useEffect(()=>{const labels=['订单详情','去支付','评价','查看','导出订单','历史版本','选择图片','手动修改','处理记录'];const feedback=(event:MouseEvent)=>{const button=(event.target as HTMLElement).closest('button');if(button&&labels.some(label=>button.textContent?.trim().includes(label)))notify('演示操作已响应','info')};document.addEventListener('click',feedback);return()=>document.removeEventListener('click',feedback)},[])
 const addCart=(productId:number,quantity=1)=>{setCart(lines=>{const old=lines.find(x=>x.productId===productId);return old?lines.map(x=>x.productId===productId?{...x,quantity:x.quantity+quantity}:x):[...lines,{productId,quantity,selected:true}]});notify('已加入购物车')}
 const updateCart=(id:number,patch:Partial<CartLine>)=>setCart(v=>v.map(x=>x.productId===id?{...x,...patch}:x));const removeCart=(id:number)=>{setCart(v=>v.filter(x=>x.productId!==id));notify('商品已移除','info')};const toggleFavorite=(id:number)=>{setFavorites(v=>v.includes(id)?v.filter(x=>x!==id):[...v,id]);notify(favorites.includes(id)?'已取消收藏':'已加入收藏','info')};const toggleCompare=(id:number)=>{if(!compare.includes(id)&&compare.length>=4)return notify('最多同时对比 4 件商品','error');setCompare(v=>v.includes(id)?v.filter(x=>x!==id):[...v,id]);notify(compare.includes(id)?'已移出对比':'已加入对比','info')}
 const login=()=>{setLoggedIn(true);notify('登录成功，欢迎回来')};const logout=()=>{localStorage.removeItem('access_token');setCurrentUser(null);setLoggedIn(false);notify('已退出登录','info')}
 const value=useMemo(()=>({cart,favorites,compare,loggedIn,currentUser,userLoading,toasts,refreshUser,addCart,updateCart,removeCart,toggleFavorite,toggleCompare,login,logout,notify}),[cart,favorites,compare,loggedIn,currentUser,userLoading,toasts])
 return <Context.Provider value={value}>{children}<div className="toast-stack">{toasts.map(t=><div key={t.id} className={`toast ${t.tone}`}>{t.message}</div>)}</div></Context.Provider>
}
export const useApp=()=>{const value=useContext(Context);if(!value)throw new Error('useApp must be inside AppProvider');return value}