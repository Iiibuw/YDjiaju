/** 后台案例管理 API。 */
import { http, unwrap, type ApiEnvelope, type PageMeta } from './http'

export interface CaseItem {
  id: number
  title: string
  cover_url: string
  style: string | null
  area: string | null
  description: string | null
  published_date: string
  view_count: number
  category_id: number | null
  category: { id: number; name: string } | null
  images: string[]
  sort: number
  is_deleted: number
  created_date: string | null
  updated_date: string | null
}

export interface CaseCreatePayload {
  title: string
  cover_url: string
  category_id?: number | null
  style?: string | null
  area?: string | null
  description?: string | null
  published_date?: string | null
  sort?: number
}

export interface CaseListResp {
  items: CaseItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
  meta: PageMeta
}

export const casesAdmin = {
  async list(params?: { keyword?: string; category_id?: number; page?: number; page_size?: number }) {
    const qs = new URLSearchParams()
    if (params?.keyword) qs.set('keyword', params.keyword)
    if (params?.category_id !== undefined) qs.set('category_id', String(params.category_id))
    if (params?.page) qs.set('page', String(params.page))
    if (params?.page_size) qs.set('page_size', String(params.page_size))
    const env = await http.get<ApiEnvelope<CaseListResp>>(`/admin/cases?${qs.toString()}`)
    return unwrap(env)
  },
  async get(id: number) {
    const env = await http.get<ApiEnvelope<CaseItem>>(`/admin/cases/${id}`)
    return unwrap(env)
  },
  async create(payload: CaseCreatePayload) {
    const env = await http.post<ApiEnvelope<CaseItem>>('/admin/cases', payload)
    return unwrap(env)
  },
  async update(id: number, payload: Partial<CaseCreatePayload>) {
    const env = await http.put<ApiEnvelope<CaseItem>>(`/admin/cases/${id}`, payload)
    return unwrap(env)
  },
  async delete(id: number) {
    const env = await http.delete<ApiEnvelope<{ id: number }>>(`/admin/cases/${id}`)
    return unwrap(env)
  },
}