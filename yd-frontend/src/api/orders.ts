/** 订单 + 预约 API（前台）。 */
import { http, unwrap, type ApiEnvelope } from './http'

interface PageMeta {
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface OrderItemOut {
  id: number
  product_id: number
  product_name: string
  cover_url: string | null
  price_cents: number
  quantity: number
  subtotal_cents: number
}

export interface OrderOut {
  id: number
  order_no: string
  status: 'pending' | 'paid' | 'shipped' | 'completed' | 'closed'
  total_cents: number
  shipping_cents: number
  discount_cents: number
  final_cents: number
  receiver_name: string | null
  receiver_phone: string | null
  receiver_address: string | null
  remark: string | null
  created_date: string | null
  paid_date: string | null
  items: OrderItemOut[]
}

export interface AppointmentOut {
  id: number
  type: 'visit' | 'consult' | 'custom' | 'other'
  name: string
  phone: string
  preferred_date: string | null
  message: string | null
  source_page: string | null
  status: 'pending' | 'following' | 'converted' | 'invalid'
  follow_note: string | null
  created_date: string | null
}

export const fmtCents = (c: number) => `¥${(c / 100).toFixed(2)}`

export const ORDER_STATUS: Record<OrderOut['status'], { label: string; color: string }> = {
  pending: { label: '待付款', color: 'orange' },
  paid: { label: '已付款', color: 'blue' },
  shipped: { label: '已发货', color: 'cyan' },
  completed: { label: '已完成', color: 'green' },
  closed: { label: '已关闭', color: 'default' },
}

export const APPT_STATUS: Record<AppointmentOut['status'], { label: string; color: string }> = {
  pending: { label: '待跟进', color: 'orange' },
  following: { label: '跟进中', color: 'blue' },
  converted: { label: '已转化', color: 'green' },
  invalid: { label: '无效', color: 'default' },
}

export interface OrderCreatePayload {
  items: { product_id: number; quantity: number }[]
  receiver_name: string
  receiver_phone: string
  receiver_address: string
  remark?: string | null
}

export async function createOrder(payload: OrderCreatePayload): Promise<OrderOut> {
  const env = await http.post<ApiEnvelope<OrderOut>>('/orders', payload)
  return unwrap(env)
}

export async function listMyOrders(): Promise<{ items: OrderOut[]; total: number }> {
  const env = await http.get<ApiEnvelope<{ items: OrderOut[]; total: number; meta: PageMeta }>>('/orders/me')
  return unwrap(env)
}

export interface AppointmentCreatePayload {
  type: string
  name: string
  phone: string
  preferred_date?: string | null
  message?: string | null
  source_page?: string | null
}

export async function createAppointment(payload: AppointmentCreatePayload): Promise<AppointmentOut> {
  const env = await http.post<ApiEnvelope<AppointmentOut>>('/appointments', payload)
  return unwrap(env)
}

export async function listMyAppointments(): Promise<{ items: AppointmentOut[]; total: number }> {
  const env = await http.get<ApiEnvelope<{ items: AppointmentOut[]; total: number; meta: PageMeta }>>('/appointments/me')
  return unwrap(env)
}