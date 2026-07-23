import { apiRequest } from './api'
import type { Product } from '../types'

export interface ProductQuery {keyword?:string;category?:string;brand?:string;excludedIngredients:string[];sugarMax?:number;fatMax?:number;proteinMin?:number;sodiumMax?:number;priceMin?:number;priceMax?:number;page:number;pageSize:number;sortBy:'created_at'|'price'|'name'|'stock';sortOrder:'asc'|'desc'}
interface ApiProduct {id:number;product_code:string;name:string;subtitle:string|null;brand:string;category:string;merchant:string;main_image_url:string|null;sale_price:string|null;market_price:string|null;stock_quantity:number|null;audit_status:string;updated_at:string}
export interface CategoryCount {category_code:string;category_name:string;product_count:number}
export interface BrandOption {brand_code:string;name:string}
export interface ProductResult {total:number;page:number;page_size:number;items:Product[]}

const toParams=(query:ProductQuery)=>{const p=new URLSearchParams({page:String(query.page),page_size:String(query.pageSize),sort_by:query.sortBy,sort_order:query.sortOrder});if(query.keyword)p.set('keyword',query.keyword);if(query.category)p.set('category',query.category);if(query.brand)p.set('brand',query.brand);query.excludedIngredients.forEach(value=>p.append('exclude',value));([['sugar_max',query.sugarMax],['fat_max',query.fatMax],['protein_min',query.proteinMin],['sodium_max',query.sodiumMax],['price_min',query.priceMin],['price_max',query.priceMax]] as const).forEach(([key,value])=>value!==undefined&&p.set(key,String(value)));return p}
const mapProduct=(item:ApiProduct):Product=>({id:item.id,productCode:item.product_code,name:item.name,brand:item.brand,category:item.category,price:item.sale_price===null?0:Number(item.sale_price),originalPrice:item.market_price===null?undefined:Number(item.market_price),image:item.main_image_url||'',rating:0,sales:0,stock:item.stock_quantity??0,spec:'',ingredients:[],additives:[],mayContain:[],unknown:[],nutrition:{energy:null,protein:null,fat:null,sugar:null,sodium:null},status:'信息不足',reason:item.subtitle||'商品数据来自平台数据库',evidence:'请进入详情查看配料证据',source:'MySQL',reviewStatus:item.audit_status==='APPROVED'?'已通过':'待审核',merchant:item.merchant,updatedAt:item.updated_at})
export async function queryProducts(query:ProductQuery):Promise<ProductResult>{const data=await apiRequest<{total:number;page:number;page_size:number;items:ApiProduct[]}>(`/api/v1/products?${toParams(query)}`);return{...data,items:data.items.map(mapProduct)}}
export const getProductCategoryCounts=()=>apiRequest<CategoryCount[]>('/api/v1/products/categories')
export const getProductBrands=()=>apiRequest<BrandOption[]>('/api/v1/brands')
