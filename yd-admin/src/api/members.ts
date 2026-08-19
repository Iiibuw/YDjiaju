/** 后台会员管理 API。 */
import { http, unwrap, type ApiEnvelope, type PageMeta } from './http'

export interface MemberItem {
  id: number
  phone: string
  nickname: string | null
  avatar_url: string | null
  email: string | null
  gender: number | null
  is_activate: number
  created_date: string | null
  last_login_date: string | null
}

export interface MemberListResp {
  items: MemberItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
  meta: PageMeta
}

export const membersAdmin = {
  async list(params?: { keyword?: string; is_activate?: boolean; page?: number; page_size?: number }) {
    const qs = new URLSearchParams()
    if (params?.keyword) qs.set('keyword', params.keyword)
    if (params?.is_activate !== undefined) qs.set('is_activate', String(params.is_activate))
    if (params?.page) qs.set('page', String(params.page))
    if (params?.page_size) qs.set('page_size', String(params.page_size))
    const env = await http.get<ApiEnvelope<MemberListResp>>(`/admin/members?${qs.toString()}`)
    return unwrap(env)
  },
  async updateStatus(id: number, is_activate: boolean) {
    const env = await http.put<ApiEnvelope<MemberItem>>(`/admin/members/${id}/status`, { is_activate })
    return unwrap(env)
  },
  async delete(id: number) {
    const env = await http.delete<ApiEnvelope<{ id: number }>>(`/admin/members/${id}`)
    return unwrap(env)
  },
}