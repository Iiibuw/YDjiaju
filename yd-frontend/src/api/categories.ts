/** 分类 API 客户端（前台公开：产品中心筛选）。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface Category {
  id: number
  kind: 'series' | 'space' | 'category'
  name: string
  name_en: string | null
  parent_id: number | null
  sort: number
}

export async function listCategories(kind?: string): Promise<Category[]> {
  const env = await http.get<ApiEnvelope<Category[]>>('/public/categories', { params: { kind } })
  return unwrap(env)
}
