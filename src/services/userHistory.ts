import type { Product } from '../types'

export interface BrowsingHistoryEntry {
  productId: number
  productCode: string
  name: string
  brand: string
  image: string
  viewedAt: string
}

export interface FilterHistoryEntry {
  id: number
  query: string
  conditions: string[]
  count: number
  time: string
}

const browsingKey = (userId: number) => `browse_history_${userId}`
const filterKey = (userId: number) => `filter_history_${userId}`

function readJson<T>(key: string, fallback: T): T {
  try {
    return JSON.parse(localStorage.getItem(key) || '') as T
  } catch {
    return fallback
  }
}

export const getBrowseHistory = (userId: number) =>
  readJson<BrowsingHistoryEntry[]>(browsingKey(userId), [])

export function saveBrowseHistory(userId: number, product: Product) {
  const entry: BrowsingHistoryEntry = {
    productId: product.id,
    productCode: product.productCode || `FP${String(product.id).padStart(4, '0')}`,
    name: product.name,
    brand: product.brand,
    image: product.image,
    viewedAt: new Date().toISOString(),
  }
  const next = [entry, ...getBrowseHistory(userId).filter(item => item.productCode !== entry.productCode)].slice(0, 30)
  localStorage.setItem(browsingKey(userId), JSON.stringify(next))
  return next
}

export const getFilterHistory = (userId: number) =>
  readJson<FilterHistoryEntry[]>(filterKey(userId), [])

export function saveFilterHistory(
  userId: number,
  entry: Omit<FilterHistoryEntry, 'id' | 'time'>,
) {
  const item: FilterHistoryEntry = {
    ...entry,
    id: Date.now(),
    time: new Date().toISOString(),
  }
  const next = [item, ...getFilterHistory(userId)].slice(0, 30)
  localStorage.setItem(filterKey(userId), JSON.stringify(next))
  return next
}

export function writeFilterHistory(userId: number, items: FilterHistoryEntry[]) {
  localStorage.setItem(filterKey(userId), JSON.stringify(items))
}
