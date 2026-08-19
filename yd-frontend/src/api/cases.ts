/** 案例 API 客户端（前台公开读）。后端未启动时回退到 mock。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface CaseListItem {
  id: number
  title: string
  cover_url: string | null
  style: string | null
  area: string | null
  published_date: string | null
  view_count: number
  category_id: number | null
}

export interface CaseDetail extends CaseListItem {
  description: string | null
  category: { id: number; name: string } | null
  images: string[]
  sort: number
}

export interface ListCasesResp {
  items: CaseListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
  meta?: { total: number; page: number; page_size: number; total_pages: number }
}

const mockCases: CaseListItem[] = [
  {
    id: 1,
    title: '胡桃禮·广州海珠湾花园别墅',
    cover_url: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800',
    style: '现代简约',
    area: '280㎡',
    published_date: '2026-07-20T10:00:00',
    view_count: 1280,
    category_id: 1,
  },
  {
    id: 2,
    title: '现代北欧·佛山顺德 120㎡ 三居室',
    cover_url: 'https://images.unsplash.com/photo-1556909114-44e3e9399a2c?w=800',
    style: '现代北欧',
    area: '120㎡',
    published_date: '2026-07-30T10:00:00',
    view_count: 856,
    category_id: 2,
  },
  {
    id: 3,
    title: '新中式·东莞东城复式楼',
    cover_url: 'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=800',
    style: '新中式',
    area: '200㎡',
    published_date: '2026-08-09T10:00:00',
    view_count: 567,
    category_id: 1,
  },
]

const mockDetail = (id: number): CaseDetail => ({
  ...(mockCases.find((c) => c.id === id) ?? mockCases[0]),
  description: '<p>这是 mock 详情，用于开发阶段视觉演示。</p>',
  category: { id: 1, name: '餐厅' },
  images: [],
  sort: 999,
})

export async function listCases(params?: { category_id?: number; is_top?: boolean; keyword?: string; page?: number; page_size?: number }): Promise<ListCasesResp> {
  const qs = new URLSearchParams()
  if (params?.category_id !== undefined) qs.set('category_id', String(params.category_id))
  if (params?.is_top !== undefined) qs.set('is_top', String(params.is_top))
  if (params?.keyword) qs.set('keyword', params.keyword)
  if (params?.page) qs.set('page', String(params.page))
  if (params?.page_size) qs.set('page_size', String(params.page_size))
  try {
    const env = await http.get<ApiEnvelope<ListCasesResp>>(`/public/cases?${qs.toString()}`)
    return unwrap(env)
  } catch {
    return { items: mockCases, total: mockCases.length, page: 1, page_size: 20, total_pages: 1 }
  }
}

export async function getCaseDetail(id: number): Promise<CaseDetail | null> {
  try {
    const env = await http.get<ApiEnvelope<CaseDetail>>(`/public/cases/${id}`)
    return unwrap(env)
  } catch {
    return mockDetail(id)
  }
}