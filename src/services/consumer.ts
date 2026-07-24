import { apiRequest } from './api'
export type ApiReview={id:number;review_code:string;order_item_id:number|null;product_code:string;product_name:string;username:string;rating:number;review_text:string|null;reviewed_at:string}
export type ApiRecommendation={product_code:string;name:string;brand:string;image_url:string|null;sale_price:string|null;score:string;reasons:string[]}
export type ApiNotification={id:string;type:string;title:string;message:string;created_at:string;target_path:string|null}
export const listProductReviews=(code:string)=>apiRequest<{total:number;page:number;page_size:number;items:ApiReview[]}>(`/api/v1/products/${code}/reviews`)
export const listMyReviews=()=>apiRequest<{total:number;page:number;page_size:number;items:ApiReview[]}>('/api/v1/reviews/me')
export const createReview=(orderItemId:number,rating:number,reviewText:string)=>apiRequest<ApiReview>('/api/v1/reviews',{method:'POST',body:JSON.stringify({order_item_id:orderItemId,rating,review_text:reviewText||null})})
export const getRecommendations=()=>apiRequest<ApiRecommendation[]>('/api/v1/recommendations')
export const getNotifications=()=>apiRequest<ApiNotification[]>('/api/v1/notifications')