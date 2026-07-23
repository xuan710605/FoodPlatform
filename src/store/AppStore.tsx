import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { getCurrentUser, type CurrentUser } from '../services/account'
import { addFavorite, deleteFavorite, listFavorites, type ApiFavorite } from '../services/favorites'
import { addCartItem, deleteCartItem, getCart, updateCartItem, type ApiCartItem } from '../services/commerce'
import { getBrowseHistory, getFilterHistory, saveBrowseHistory, saveFilterHistory, writeFilterHistory, type BrowsingHistoryEntry, type FilterHistoryEntry } from '../services/userHistory'
import type { Product } from '../types'

type Toast={id:number;message:string;tone:'success'|'error'|'info'}
interface AppState{cart:ApiCartItem[];favorites:number[];favoriteItems:ApiFavorite[];browsingHistory:BrowsingHistoryEntry[];filterHistory:FilterHistoryEntry[];compare:number[];loggedIn:boolean;currentUser:CurrentUser|null;userLoading:boolean;toasts:Toast[];refreshUser:()=>Promise<void>;refreshCart:()=>Promise<void>;refreshFavorites:()=>Promise<void>;addCart:(id:number,quantity?:number)=>Promise<void>;updateCart:(itemId:number,quantity:number)=>Promise<void>;removeCart:(itemId:number)=>Promise<void>;toggleFavorite:(id:number)=>Promise<void>;trackProductView:(product:Product)=>void;addFilterHistory:(entry:Omit<FilterHistoryEntry,'id'|'time'>)=>void;replaceFilterHistory:(items:FilterHistoryEntry[])=>void;toggleCompare:(id:number)=>void;login:(user:CurrentUser)=>void;logout:()=>void;notify:(message:string,tone?:Toast['tone'])=>void}
const Context=createContext<AppState|null>(null)
const requireLogin=()=>{window.location.assign('/login')}
export function AppProvider({children}:{children:ReactNode}){
 const hasToken=Boolean(localStorage.getItem('access_token'));const [cart,setCart]=useState<ApiCartItem[]>([]);const [favorites,setFavorites]=useState<number[]>([]);const [favoriteItems,setFavoriteItems]=useState<ApiFavorite[]>([]);const [browsingHistory,setBrowsingHistory]=useState<BrowsingHistoryEntry[]>([]);const [filterHistory,setFilterHistory]=useState<FilterHistoryEntry[]>([]);const [compare,setCompare]=useState<number[]>([1,2,16]);const [loggedIn,setLoggedIn]=useState(hasToken);const [currentUser,setCurrentUser]=useState<CurrentUser|null>(null);const [userLoading,setUserLoading]=useState(hasToken);const [toasts,setToasts]=useState<Toast[]>([])
 const notify=(message:string,tone:Toast['tone']='success')=>{const id=Date.now();setToasts(v=>[...v,{id,message,tone}]);window.setTimeout(()=>setToasts(v=>v.filter(x=>x.id!==id)),2300)}
 const refreshCart=async()=>{if(!localStorage.getItem('access_token')){setCart([]);return}setCart((await getCart()).items)}
 const refreshFavorites=async()=>{if(!localStorage.getItem('access_token')){setFavorites([]);setFavoriteItems([]);return}const items=await listFavorites();setFavoriteItems(items);setFavorites(items.map(x=>x.product_id))}
 const clearUserMemory=()=>{setCurrentUser(null);setCart([]);setFavorites([]);setFavoriteItems([]);setBrowsingHistory([]);setFilterHistory([]);setLoggedIn(false)}
 const loadUserLocalData=(userId:number)=>{setBrowsingHistory(getBrowseHistory(userId));setFilterHistory(getFilterHistory(userId))}
 const refreshUser=async()=>{if(!localStorage.getItem('access_token')){clearUserMemory();setUserLoading(false);return}setUserLoading(true);try{const user=await getCurrentUser();setCurrentUser(user);loadUserLocalData(user.id);setLoggedIn(true);localStorage.setItem('current_user',JSON.stringify(user));await Promise.all([refreshCart(),refreshFavorites()])}catch{clearUserMemory();localStorage.removeItem('current_user')}finally{setUserLoading(false)}}
 useEffect(()=>{if(hasToken)void refreshUser()},[])
 useEffect(()=>{const labels=['订单详情','去支付','评价','查看','导出订单','历史版本','选择图片','手动修改','处理记录'];const feedback=(event:MouseEvent)=>{const button=(event.target as HTMLElement).closest('button');if(button&&labels.some(label=>button.textContent?.trim().includes(label)))notify('演示操作已响应','info')};document.addEventListener('click',feedback);return()=>document.removeEventListener('click',feedback)},[])
 const addCart=async(productId:number,quantity=1)=>{if(!currentUser)return requireLogin();try{await addCartItem(`FP${String(productId).padStart(4,'0')}`,quantity);await refreshCart();notify('已加入购物车')}catch(error){notify(error instanceof Error?error.message:'加入购物车失败','error')}}
 const updateCart=async(itemId:number,quantity:number)=>{if(!currentUser)return requireLogin();try{await updateCartItem(itemId,quantity);await refreshCart()}catch(error){notify(error instanceof Error?error.message:'更新购物车失败','error')}}
 const removeCart=async(itemId:number)=>{if(!currentUser)return requireLogin();try{await deleteCartItem(itemId);await refreshCart();notify('商品已移除','info')}catch(error){notify(error instanceof Error?error.message:'删除失败','error')}}
 const toggleFavorite=async(id:number)=>{if(!currentUser)return requireLogin();const code=`FP${String(id).padStart(4,'0')}`;try{if(favorites.includes(id))await deleteFavorite(code);else await addFavorite(code);await refreshFavorites();notify(favorites.includes(id)?'已取消收藏':'已加入收藏','info')}catch(error){notify(error instanceof Error?error.message:'收藏操作失败','error')}}
 const trackProductView=(product:Product)=>{if(currentUser)setBrowsingHistory(saveBrowseHistory(currentUser.id,product))}
 const addFilterHistory=(entry:Omit<FilterHistoryEntry,'id'|'time'>)=>{if(currentUser)setFilterHistory(saveFilterHistory(currentUser.id,entry))}
 const replaceFilterHistory=(items:FilterHistoryEntry[])=>{if(!currentUser)return;writeFilterHistory(currentUser.id,items);setFilterHistory(items)}
 const toggleCompare=(id:number)=>{if(!compare.includes(id)&&compare.length>=4)return notify('最多同时对比 4 件商品','error');setCompare(v=>v.includes(id)?v.filter(x=>x!==id):[...v,id]);notify(compare.includes(id)?'已移出对比':'已加入对比','info')}
 const login=(user:CurrentUser)=>{setCurrentUser(user);loadUserLocalData(user.id);setLoggedIn(true);setUserLoading(false);localStorage.setItem('current_user',JSON.stringify(user));void Promise.all([refreshCart(),refreshFavorites()]);notify('登录成功，欢迎回来')}
 const logout=()=>{localStorage.removeItem('access_token');localStorage.removeItem('current_user');clearUserMemory();setUserLoading(false);notify('已退出登录','info')}
 const value=useMemo(()=>({cart,favorites,favoriteItems,browsingHistory,filterHistory,compare,loggedIn,currentUser,userLoading,toasts,refreshUser,refreshCart,refreshFavorites,addCart,updateCart,removeCart,toggleFavorite,trackProductView,addFilterHistory,replaceFilterHistory,toggleCompare,login,logout,notify}),[cart,favorites,favoriteItems,browsingHistory,filterHistory,compare,loggedIn,currentUser,userLoading,toasts])
 return <Context.Provider value={value}>{children}<div className="toast-stack">{toasts.map(t=><div key={t.id} className={`toast ${t.tone}`}>{t.message}</div>)}</div></Context.Provider>
}
export const useApp=()=>{const value=useContext(Context);if(!value)throw new Error('useApp must be inside AppProvider');return value}
