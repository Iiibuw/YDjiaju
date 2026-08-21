/** 后台分类 API（空间 / 系列 / 品类，kind=space/series/category） */
import { http, unwrap, type ApiEnvelope } from './http'

export interface CategoryItem {
  id: number
  kind: string // 'space' | 'series' | 'category'
  name: string
  name_en?: string | null
  icon?: string | null
  parent_id?: number | null
  sort?: number
  enabled?: number
  is_activate?: number
  status?: number
}

export interface CategoryIn {
  kind: string
  name: string
  name_en?: string | null
  icon?: string | null
  parent_id?: number | null
  sort?: number
  enabled?: number
}

/** 前台只读：全部启用分类（扁平） */
export async function listCategories(kind?: string): Promise<CategoryItem[]> {
  const resp = await http.get<ApiEnvelope<CategoryItem[]>>('/public/categories', { params: { kind } })
  return unwrap(resp)
}

/** 后台分类管理 CRUD */
export const adminCategories = {
  /** 按 kind 列表（含禁用） */
  async list(kind?: string): Promise<CategoryItem[]> {
    const resp = await http.get<ApiEnvelope<CategoryItem[]>>('/admin/categories', { params: { kind } })
    return unwrap(resp)
  },
  async create(payload: CategoryIn): Promise<CategoryItem> {
    const resp = await http.post<ApiEnvelope<CategoryItem>>('/admin/categories', payload)
    return unwrap(resp)
  },
  async update(id: number, payload: Partial<CategoryIn>): Promise<CategoryItem> {
    const resp = await http.put<ApiEnvelope<CategoryItem>>(`/admin/categories/${id}`, payload)
    return unwrap(resp)
  },
  async remove(id: number): Promise<void> {
    const resp = await http.delete<ApiEnvelope<{ id: number }>>(`/admin/categories/${id}`)
    unwrap(resp)
  },
}