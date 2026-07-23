import { apiRequest } from './api'

export type ApiFavorite={id:number;product_id:number;product_code:string;name:string;brand:string;category:string;main_image_url:string|null;sale_price:string|null;sale_status:string;audit_status:string;created_at:string}
export const listFavorites=()=>apiRequest<ApiFavorite[]>('/api/v1/favorites')
export const addFavorite=(productCode:string)=>apiRequest<ApiFavorite>('/api/v1/favorites',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_code:productCode})})
export const deleteFavorite=(productCode:string)=>apiRequest<{product_code:string}>(`/api/v1/favorites/${productCode}`,{method:'DELETE'})
