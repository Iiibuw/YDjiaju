/** 后台留言管理 API。 */
import { http, unwrap, type ApiEnvelope, type PageMeta } from './http'

export interface MessageItem {
  id: number
  name: string
  phone: string | null
  email: string | null
  content: string
  status: 'pending' | 'replied' | 'archived'
  reply_content: string | null
  reply_date: string | null
  created_date: string | null
}

export interface MessageListResp {
  items: MessageItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
  meta: PageMeta
}

export const messagesAdmin = {
  async list(params?: { status?: string; keyword?: string; page?: number; page_size?: number }) {
    const qs = new URLSearchParams()
    if (params?.status) qs.set('status', params.status)
    if (params?.keyword) qs.set('keyword', params.keyword)
    if (params?.page) qs.set('page', String(params.page))
    if (params?.page_size) qs.set('page_size', String(params.page_size))
    const env = await http.get<ApiEnvelope<MessageListResp>>(`/admin/messages?${qs.toString()}`)
    return unwrap(env)
  },
  async reply(id: number, reply_content: string) {
    const env = await http.post<ApiEnvelope<MessageItem>>(`/admin/messages/${id}/reply`, { reply_content })
    return unwrap(env)
  },
  async delete(id: number) {
    const env = await http.delete<ApiEnvelope<{ id: number }>>(`/admin/messages/${id}`)
    return unwrap(env)
  },
}