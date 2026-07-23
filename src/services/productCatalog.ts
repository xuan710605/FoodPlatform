import { apiRequest } from './api'
import type { MatchStatus, ProductCardData } from '../types'

export interface ProductQuery {keyword?:string;category?:string;brand?:string;excludedIngredients:string[];sugarMax?:number;fatMax?:number;proteinMin?:number;sodiumMax?:number;priceMin?:number;priceMax?:number;page:number;pageSize:number;sortBy:'created_at'|'price'|'name'|'stock';sortOrder:'asc'|'desc'}
interface ApiIngredientSummary {entity_code:string;name:string;entity_type:string;relation_type:'CONTAINS'|'MAY_CONTAIN'|'UNKNOWN';confidence:string|null;source_code:string;audit_status:string}
interface ApiProduct {id:number;product_code:string;name:string;subtitle:string|null;brand:string;category:string;merchant:string;main_image_url:string|null;sale_price:string|null;market_price:string|null;stock_quantity:number|null;audit_status:string;updated_at:string;average_rating:string|null;review_count:number;sales_count?:number|null;match_status:string;match_reason:string|null;evidence_text:string|null;info_source:string|null;contains:ApiIngredientSummary[];may_contain:ApiIngredientSummary[];unknown:ApiIngredientSummary[]}
export interface CategoryCount {category_code:string;category_name:string;product_count:number}
export interface BrandOption {brand_code:string;name:string}
export interface ProductResult {total:number;page:number;page_size:number;items:ProductCardData[]}

const matchStatuses:Record<string,MatchStatus>={FULL_MATCH:'完全匹配',RISK:'存在风险',NOT_MATCH:'不匹配',INFORMATION_INSUFFICIENT:'信息不足'}
const toParams=(query:ProductQuery)=>{const p=new URLSearchParams({page:String(query.page),page_size:String(query.pageSize),sort_by:query.sortBy,sort_order:query.sortOrder});if(query.keyword)p.set('keyword',query.keyword);if(query.category)p.set('category',query.category);if(query.brand)p.set('brand',query.brand);query.excludedIngredients.forEach(value=>p.append('exclude',value));([['sugar_max',query.sugarMax],['fat_max',query.fatMax],['protein_min',query.proteinMin],['sodium_max',query.sodiumMax],['price_min',query.priceMin],['price_max',query.priceMax]] as const).forEach(([key,value])=>value!==undefined&&p.set(key,String(value)));return p}
const mapProduct=(item:ApiProduct):ProductCardData=>({
  id:item.id,
  productCode:item.product_code,
  name:item.name,
  brand:item.brand,
  category:item.category,
  price:item.sale_price===null?null:Number(item.sale_price),
  originalPrice:item.market_price===null?undefined:Number(item.market_price),
  image:item.main_image_url||'',
  rating:item.average_rating===null?null:Number(item.average_rating),
  reviewCount:item.review_count,
  sales:item.sales_count??null,
  ingredients:item.contains.filter(value=>value.entity_type!=='ADDITIVE').map(value=>value.name),
  additives:item.contains.filter(value=>value.entity_type==='ADDITIVE').map(value=>value.name),
  mayContain:item.may_contain.map(value=>value.name),
  unknown:item.unknown.map(value=>value.name),
  status:matchStatuses[item.match_status]||'信息不足',
  reason:item.match_reason,
  evidence:item.evidence_text,
  source:item.info_source,
})
export async function queryProducts(query:ProductQuery):Promise<ProductResult>{const data=await apiRequest<{total:number;page:number;page_size:number;items:ApiProduct[]}>(`/api/v1/products?${toParams(query)}`);return{...data,items:data.items.map(mapProduct)}}
export const getProductCategoryCounts=()=>apiRequest<CategoryCount[]>('/api/v1/products/categories')
export const getProductBrands=()=>apiRequest<BrandOption[]>('/api/v1/brands')