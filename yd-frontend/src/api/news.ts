/** 资讯 API 客户端（前台）。后端未启动时回退到 mock。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface NewsListItem {
  id: number
  title: string
  subtitle: string | null
  category: 'company' | 'industry'
  cover_url: string | null
  summary: string | null
  author: string | null
  view_count: number
  published_date: string | null
  is_top: boolean
  is_recommend: boolean
}

export interface NewsDetail extends NewsListItem {
  content: string
  source: string | null
  expire_date: string | null
  is_published: boolean
  sort: number
  created_date: string
  updated_date: string
}

export interface PageMeta {
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ListNewsResp {
  items: NewsListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
  meta: PageMeta
}

// ===== Mock 兜底（仅开发演示） =====
const mockNews: NewsListItem[] = [
  {
    id: 1,
    title: 'YD 家居荣获 2026 中国家具创新品牌奖',
    subtitle: '品牌动态',
    category: 'company',
    cover_url: 'https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800',
    summary: '8 月 15 日，YD 家居凭借胡桃禮系列在 2026 中国家具创新品牌评选中脱颖而出，荣获年度创新品牌奖。',
    author: 'YD 编辑部',
    view_count: 1280,
    published_date: '2026-08-18T10:00:00',
    is_top: true,
    is_recommend: true,
  },
  {
    id: 2,
    title: '关于我司参加 2026 广州国际家具博览会的通知',
    subtitle: '展会信息',
    category: 'company',
    cover_url: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
    summary: '我司将于 9 月 10 日至 13 日参加广州国际家具博览会，展位号 5B12。',
    author: '市场部',
    view_count: 856,
    published_date: '2026-08-16T10:00:00',
    is_top: false,
    is_recommend: true,
  },
  {
    id: 3,
    title: '2026 年家居行业消费趋势报告',
    subtitle: '行业洞察',
    category: 'industry',
    cover_url: 'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=800',
    summary: '报告显示，2026 年中国家装行业整体规模超 5 万亿元，新中式风格持续走热。',
    author: '行业研究部',
    view_count: 2340,
    published_date: '2026-08-14T10:00:00',
    is_top: true,
    is_recommend: false,
  },
]

const mockDetail = (id: number): NewsDetail => ({
  ...(mockNews.find((n) => n.id === id) ?? mockNews[0]),
  content: '<p>这是 mock 正文，用于开发阶段视觉演示。</p><p>接入真实后端后此内容来自数据库。</p>',
  source: null,
  expire_date: null,
  is_published: true,
  sort: 0,
  created_date: '2026-08-01T10:00:00',
  updated_date: '2026-08-18T10:00:00',
})

// ===== API =====
export async function listNews(params?: { category?: string; is_top?: boolean; page?: number; page_size?: number }): Promise<ListNewsResp> {
  const qs = new URLSearchParams()
  if (params?.category) qs.set('category', params.category)
  if (params?.is_top !== undefined) qs.set('is_top', String(params.is_top))
  if (params?.page) qs.set('page', String(params.page))
  if (params?.page_size) qs.set('page_size', String(params.page_size))
  try {
    const env = await http.get<ApiEnvelope<ListNewsResp>>(`/api/v1/public/news?${qs.toString()}`)
    return unwrap(env)
  } catch {
    return { items: mockNews, total: mockNews.length, page: 1, page_size: 20, total_pages: 1, meta: { total: mockNews.length, page: 1, page_size: 20, total_pages: 1 } }
  }
}

export async function getNewsDetail(id: number): Promise<NewsDetail | null> {
  try {
    const env = await http.get<ApiEnvelope<NewsDetail>>(`/api/v1/public/news/${id}`)
    return unwrap(env)
  } catch {
    return mockDetail(id)
  }
}