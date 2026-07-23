export type MatchStatus = '完全匹配' | '存在风险' | '不匹配' | '信息不足'
export type ReviewStatus = '草稿' | '待审核' | '已通过' | '已驳回' | '需补充'

export interface Nutrition {
  energy: number | null
  protein: number | null
  fat: number | null
  sugar: number | null
  sodium: number | null
}

export interface Product {
  id: number
  productCode?: string
  name: string
  brand: string
  category: string
  price: number
  originalPrice?: number
  image: string
  gallery?: string[]
  rating: number
  sales: number
  stock: number
  spec: string
  ingredients: string[]
  additives: string[]
  mayContain: string[]
  unknown: string[]
  nutrition: Nutrition
  status: MatchStatus
  reason: string
  evidence: string
  source: string
  reviewStatus: ReviewStatus
  merchant: string
  updatedAt: string
}

export interface CatalogProduct {
  id: number
  productCode?: string
  name: string
  brand: string
  category: string
  price: number | null
  originalPrice?: number
  image: string
  rating: number | null
  reviewCount?: number
  sales: number | null
  ingredients: string[]
  additives?: string[]
  mayContain?: string[]
  unknown?: string[]
}
export interface SmartFilterProduct extends Product {}

export interface Order {
  id: string
  date: string
  status: '待付款' | '待发货' | '待收货' | '已完成' | '已取消' | '退款申请'
  amount: number
  productIds: number[]
  buyer: string
}

export interface GraphNode {
  data: { id: string; label: string; type: string; detail?: string }
}

export interface GraphEdge {
  data: { id: string; source: string; target: string; label: string }
}
