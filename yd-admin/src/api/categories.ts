/** 后台分类 API（空间/系列/品类，来自 /public/categories） */
import { http, unwrap, type ApiEnvelope } from './http'

export interface CategoryItem {
  id: number
  name: string
  kind: string // 'space' | 'series' | 'category'
  parent_id?: number | null
  sort?: number
}

export async function listCategories(): Promise<CategoryItem[]> {
  const resp = await http.get<ApiEnvelope<CategoryItem[]>>('/public/categories')
  return unwrap(resp)
}