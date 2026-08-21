/** 后台产品管理 API（字段对齐后端 admin_products，价格单位=分） */
import { http, unwrap, type ApiEnvelope } from './http'

export type ProductStatus = 'draft' | 'on_sale' | 'off_sale'

export interface ProductItem {
  id: number
  product_code?: string | null
  /** 产品标题（后端字段为 name） */
  name: string
  subtitle?: string | null
  category_id?: number | null
  space_id?: number | null
  series_id?: number | null
  category_name?: string | null
  space_name?: string | null
  series_name?: string | null
  cover_url?: string | null
  description?: string | null
  min_price_cents?: number | null
  max_price_cents?: number | null
  is_top?: boolean | number
  is_activate?: boolean | number
  support_order?: number
  sort?: number
  status?: ProductStatus
  view_count?: number
  created_date?: string | null
  updated_date?: string | null
}

export interface ProductCreatePayload {
  name: string
  subtitle?: string | null
  series_id?: number | null
  space_id?: number | null
  category_id?: number | null
  cover_url?: string | null
  description?: string | null
  min_price_cents?: number | null
  max_price_cents?: number | null
  status?: ProductStatus
  is_top?: number
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
  /** 后台列表：keyword / status_filter / category_id / space_id / series_id */
  async list(params: {
    page?: number
    page_size?: number
    keyword?: string
    status_filter?: ProductStatus
    category_id?: number
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