/** 后台订单 + 预约管理 API。 */
import { http, unwrap, type ApiEnvelope, type PageMeta } from './http'

export interface OrderItemOut {
  id: number
  product_id: number
  product_name: string
  cover_url: string | null
  price_cents: number
  quantity: number
  subtotal_cents: number
}

export interface OrderItem {
  id: number
  order_no: string
  status: 'pending' | 'paid' | 'shipped' | 'completed' | 'closed'
  total_cents: number
  final_cents: number
  receiver_name: string | null
  receiver_phone: string | null
  receiver_address: string | null
  remark: string | null
  created_date: string | null
  paid_date: string | null
  shipped_date: string | null
  items: OrderItemOut[]
}

export interface AppointmentItem {
  id: number
  type: 'visit' | 'consult' | 'custom' | 'other'
  name: string
  phone: string
  preferred_date: string | null
  message: string | null
  status: 'pending' | 'following' | 'converted' | 'invalid'
  follow_note: string | null
  created_date: string | null
}

export const ORDER_STATUS_LABELS: Record<string, string> = {
  pending: '待付款',
  paid: '已付款',
  shipped: '已发货',
  completed: '已完成',
  closed: '已关闭',
}

export const APPT_STATUS_LABELS: Record<string, string> = {
  pending: '待跟进',
  following: '跟进中',
  converted: '已转化',
  invalid: '无效',
}

export const fmtCents = (c: number) => `¥${(c / 100).toFixed(2)}`

export const ordersAdmin = {
  async list(params?: { status?: string; keyword?: string; page?: number; page_size?: number }) {
    const qs = new URLSearchParams()
    if (params?.status) qs.set('status', params.status)
    if (params?.keyword) qs.set('keyword', params.keyword)
    if (params?.page) qs.set('page', String(params.page))
    if (params?.page_size) qs.set('page_size', String(params.page_size))
    const env = await http.get<ApiEnvelope<{ items: OrderItem[]; total: number; page: number; page_size: number; total_pages: number; meta: PageMeta }>>(`/admin/orders?${qs.toString()}`)
    return unwrap(env)
  },
  async updateStatus(id: number, status: string) {
    const env = await http.put<ApiEnvelope<OrderItem>>(`/admin/orders/${id}/status`, { status })
    return unwrap(env)
  },
}

export const appointmentsAdmin = {
  async list(params?: { status?: string; keyword?: string; page?: number; page_size?: number }) {
    const qs = new URLSearchParams()
    if (params?.status) qs.set('status', params.status)
    if (params?.keyword) qs.set('keyword', params.keyword)
    if (params?.page) qs.set('page', String(params.page))
    if (params?.page_size) qs.set('page_size', String(params.page_size))
    const env = await http.get<ApiEnvelope<{ items: AppointmentItem[]; total: number; page: number; page_size: number; total_pages: number; meta: PageMeta }>>(`/admin/appointments?${qs.toString()}`)
    return unwrap(env)
  },
  async updateStatus(id: number, status: string, follow_note?: string) {
    const env = await http.put<ApiEnvelope<AppointmentItem>>(`/admin/appointments/${id}/status`, { status, follow_note })
    return unwrap(env)
  },
  async delete(id: number) {
    const env = await http.delete<ApiEnvelope<{ id: number }>>(`/admin/appointments/${id}`)
    return unwrap(env)
  },
}