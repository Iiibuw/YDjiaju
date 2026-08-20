/** 后台仪表盘 API。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface DashboardCounts {
  members: number
  products: number
  orders: number
  messages: number
  appointments: number
  news: number
}

export interface LatestMember {
  id: number
  nickname: string | null
  phone: string | null
  created_date: string | null
}

export interface DashboardStats {
  counts: DashboardCounts
  days: string[]
  orders: number[] // 近7日订单
  visits: number[] // 近7日访问
  appointments: number[] // 近7日预约
  news_trend: number[] // 近7日资讯发布
  order_status_dist: { status: string; count: number }[]
  todos: {
    draft_news: number
    pending_appointments: number
    pending_messages: number
    latest_members: LatestMember[]
  }
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const resp = await http.get<ApiEnvelope<DashboardStats>>('/admin/dashboard/stats')
  return unwrap(resp)
}