/** 后台资讯管理 API（与后端 /api/v1/admin/news 对齐）。 */
import { http, unwrap, type ApiEnvelope, type PageMeta } from './http'

export interface NewsItem {
  id: number
  title: string
  subtitle: string | null
  category: 'company' | 'industry'
  cover_url: string | null
  summary: string | null
  content: string
  author: string | null
  source: string | null
  view_count: number
  published_date: string | null
  expire_date: string | null
  is_published: boolean
  is_top: boolean
  is_recommend: boolean
  sort: number
  created_date: string
  updated_date: string
}

export interface NewsCreatePayload {
  title: string
  subtitle?: string | null
  category?: 'company' | 'industry'
  cover_url?: string | null
  summary?: string | null
  content: string
  author?: string | null
  source?: string | null
  is_published?: boolean
  is_top?: boolean
  is_recommend?: boolean
  sort?: number
  published_date?: string | null
  expire_date?: string | null
}

export interface NewsListResp {
  items: NewsItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
  meta: PageMeta
}

export const newsAdmin = {
  async list(params?: { category?: string; is_published?: boolean; keyword?: string; page?: number; page_size?: number }) {
    const qs = new URLSearchParams()
    if (params?.category) qs.set('category', params.category)
    if (params?.is_published !== undefined) qs.set('is_published', String(params.is_published))
    if (params?.keyword) qs.set('keyword', params.keyword)
    if (params?.page) qs.set('page', String(params.page))
    if (params?.page_size) qs.set('page_size', String(params.page_size))
    const env = await http.get<ApiEnvelope<NewsListResp>>(`/api/v1/admin/news?${qs.toString()}`)
    return unwrap(env)
  },
  async get(id: number) {
    const env = await http.get<ApiEnvelope<NewsItem>>(`/api/v1/admin/news/${id}`)
    return unwrap(env)
  },
  async create(payload: NewsCreatePayload) {
    const env = await http.post<ApiEnvelope<NewsItem>>('/api/v1/admin/news', payload)
    return unwrap(env)
  },
  async update(id: number, payload: Partial<NewsCreatePayload>) {
    const env = await http.put<ApiEnvelope<NewsItem>>(`/api/v1/admin/news/${id}`, payload)
    return unwrap(env)
  },
  async delete(id: number) {
    const env = await http.delete<ApiEnvelope<{ id: number }>>(`/api/v1/admin/news/${id}`)
    return unwrap(env)
  },
}