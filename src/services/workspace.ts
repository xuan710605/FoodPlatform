import { apiRequest } from './api'

export type MerchantDashboardData={merchant_code:string;merchant_name:string;product_count:number;on_sale_count:number;pending_review_count:number;order_count:number;paid_order_count:number;sales_amount:string}
export type MerchantProduct={product_code:string;name:string;subtitle:string|null;description:string|null;raw_ingredient_text:string;allergen_notice:string|null;brand:string;brand_code:string;category:string;category_code:string;spec_name:string;unit_name:string;image_url:string|null;sale_status:string;review_status:string;sale_price:string|null;stock_quantity:number|null;updated_at:string}
export type ProductWrite={name:string;subtitle:string|null;description:string|null;brand_code:string;category_code:string;raw_ingredient_text:string;allergen_notice:string|null;spec_name:string;unit_name:string;price:string;stock_quantity:number;image_url:string|null}
export type MerchantOrder={id:number;order_no:string;buyer:string;status:'PENDING_PAYMENT'|'PAID'|'SHIPPING'|'COMPLETED'|'CANCELLED'|'REFUND_REQUESTED';payable_amount:string;paid_amount:string;item_count:number;placed_at:string;paid_at:string|null;shipped_at:string|null;completed_at:string|null}
export type AdminDashboardData={user_count:number;merchant_count:number;product_count:number;pending_product_count:number;order_count:number}
export type AdminUser={id:number;user_code:string;username:string;email:string|null;user_type:string;status:string;roles:string[];created_at:string}
export type AdminProduct={product_code:string;name:string;merchant_code:string;merchant_name:string;brand:string;category:string;review_status:string;sale_status:string;submitted_at:string|null;updated_at:string}
export type CatalogOption={category_code?:string;brand_code?:string;name:string}

export const getMerchantDashboard=()=>apiRequest<MerchantDashboardData>('/api/v1/merchant/dashboard')
export const getMerchantProducts=()=>apiRequest<MerchantProduct[]>('/api/v1/merchant/products')
export const createMerchantProduct=(payload:ProductWrite)=>apiRequest<{product_code:string}>('/api/v1/merchant/products',{method:'POST',body:JSON.stringify(payload)})
export const updateMerchantProduct=(code:string,payload:ProductWrite)=>apiRequest<{product_code:string}>(`/api/v1/merchant/products/${code}`,{method:'PUT',body:JSON.stringify(payload)})
export const updateMerchantProductSale=(code:string,sale_status:'ON_SALE'|'OFF_SALE')=>apiRequest<{product_code:string;sale_status:string}>(`/api/v1/merchant/products/${code}/sale-status`,{method:'PUT',body:JSON.stringify({sale_status})})
export const getMerchantOrders=()=>apiRequest<MerchantOrder[]>('/api/v1/merchant/orders')
export const updateMerchantOrderStatus=(id:number,status:'SHIPPING'|'COMPLETED')=>apiRequest<{id:number;status:string}>(`/api/v1/merchant/orders/${id}/status`,{method:'PUT',body:JSON.stringify({status})})
export const getAdminDashboard=()=>apiRequest<AdminDashboardData>('/api/v1/admin/dashboard')
export const getAdminUsers=(keyword='')=>apiRequest<AdminUser[]>(keyword?`/api/v1/admin/users?keyword=${encodeURIComponent(keyword)}`:'/api/v1/admin/users')
export const updateAdminUserStatus=(id:number,status:'ACTIVE'|'DISABLED')=>apiRequest<{id:number;status:string}>(`/api/v1/admin/users/${id}/status`,{method:'PUT',body:JSON.stringify({status})})
export const getAdminProducts=(status='PENDING')=>apiRequest<AdminProduct[]>(`/api/v1/admin/products?review_status=${encodeURIComponent(status)}`)
export const approveAdminProduct=(code:string,opinion:string)=>apiRequest<{product_code:string;review_status:string}>(`/api/v1/admin/products/${code}/approve`,{method:'PUT',body:JSON.stringify({opinion:opinion||null})})
export const getCatalogCategories=()=>apiRequest<CatalogOption[]>('/api/v1/categories')
export const getCatalogBrands=()=>apiRequest<CatalogOption[]>('/api/v1/brands')