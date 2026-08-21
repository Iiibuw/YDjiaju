/** 后台产品管理 API */
import { http, unwrap, type ApiEnvelope } from './http'

export type ProductStatus = 'draft' | 'on_sale' | 'off_sale'

export interface ProductItem {
  id: number
  title: string
  subtitle?: string | null
  series?: string | null
  space?: string | null
  category_id?: number | null
  style?: string | null
  cover_url?: string | null
  gallery?: string[] | null
  description?: string | null
  min_price_cents?: number | null
  max_price_cents?: number | null
  is_top?: boolean
  is_recommend?: boolean
  is_activate?: boolean
  sort?: number
  status?: ProductStatus
  view_count?: number
  created_date?: string | null
  updated_date?: string | null
}

export interface ProductCreatePayload {
  title: string
  subtitle?: string | null
  series?: string | null
  space?: string | null
  style?: string | null
  cover_url?: string | null
  description?: string | null
  min_price_cents?: number | null
  max_price_cents?: number | null
  status?: ProductStatus
  is_activate?: boolean
  sort?: number
}

export interface ProductPageData {
  items: ProductItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const productsAdmin = {
  async list(params: {
    page?: number
    page_size?: number
    keyword?: string
    status?: ProductStatus
    space?: string
  } = {}): Promise<ProductPageData> {
    const resp = await http.get<ApiEnvelope<ProductPageData>>('/admin/products', { params })
    return unwrap(resp)
  },

  async get(id: number): Promise<ProductItem> {
    const resp = await http.get<ApiEnvelope<ProductItem>>(`/admin/products/${id}`)
    return unwrap(resp)
  },

  async create(payload: ProductCreatePayload): Promise<ProductItem> {
    const resp = await http.post<ApiEnvelope<ProductItem>>('/admin/products', payload)
    return unwrap(resp)
  },

  async update(id: number, payload: Partial<ProductCreatePayload>): Promise<ProductItem> {
    const resp = await http.put<ApiEnvelope<ProductItem>>(`/admin/products/${id}`, payload)
    return unwrap(resp)
  },

  async remove(id: number): Promise<void> {
    const resp = await http.delete<ApiEnvelope<{ id: number }>>(`/admin/products/${id}`)
    unwrap(resp)
  },
}