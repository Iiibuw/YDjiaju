/** 后台招聘管理 API（与后端 /api/v1/admin/jobs 对齐）。 */
import { http, unwrap, type ApiEnvelope, type PageMeta } from './http'

export interface JobItem {
  id: number
  title: string
  category: 'social' | 'campus'
  department: string | null
  location: string | null
  salary_min_cents: number | null
  salary_max_cents: number | null
  headcount: number
  description: string | null
  requirement: string | null
  publish_date: string
  expire_date: string | null
  created_date: string
  updated_date: string
}

export interface JobCreatePayload {
  title: string
  category?: 'social' | 'campus'
  department?: string | null
  location?: string | null
  salary_min_cents?: number | null
  salary_max_cents?: number | null
  headcount?: number
  description?: string | null
  requirement?: string | null
  publish_date?: string | null
  expire_date?: string | null
  is_activate?: boolean
}

export interface ApplicationItem {
  id: number
  job_id: number
  job_title: string | null
  name: string
  phone: string
  email: string | null
  region_code: string | null
  resume_url: string | null
  stage: 'applied' | 'screening' | 'interview' | 'offer' | 'rejected'
  reject_reason: string | null
  applied_date: string
  screening_date: string | null
  interview_date: string | null
  offer_date: string | null
  closed_date: string | null
  admin_note: string | null
  created_date: string
}

export interface JobListResp {
  items: JobItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
  meta: PageMeta
}

export interface ApplicationListResp {
  items: ApplicationItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
  meta: PageMeta
}

export const jobsAdmin = {
  async list(params?: { category?: string; keyword?: string; page?: number; page_size?: number }) {
    const qs = new URLSearchParams()
    if (params?.category) qs.set('category', params.category)
    if (params?.keyword) qs.set('keyword', params.keyword)
    if (params?.page) qs.set('page', String(params.page))
    if (params?.page_size) qs.set('page_size', String(params.page_size))
    const env = await http.get<ApiEnvelope<JobListResp>>(`/api/v1/admin/jobs?${qs.toString()}`)
    return unwrap(env)
  },
  async create(payload: JobCreatePayload) {
    const env = await http.post<ApiEnvelope<JobItem>>('/api/v1/admin/jobs', payload)
    return unwrap(env)
  },
  async update(id: number, payload: Partial<JobCreatePayload>) {
    const env = await http.put<ApiEnvelope<JobItem>>(`/api/v1/admin/jobs/${id}`, payload)
    return unwrap(env)
  },
  async delete(id: number) {
    const env = await http.delete<ApiEnvelope<{ id: number }>>(`/api/v1/admin/jobs/${id}`)
    return unwrap(env)
  },
  async listApplications(params?: { job_id?: number; stage?: string; page?: number; page_size?: number }) {
    const qs = new URLSearchParams()
    if (params?.job_id !== undefined) qs.set('job_id', String(params.job_id))
    if (params?.stage) qs.set('stage', params.stage)
    if (params?.page) qs.set('page', String(params.page))
    if (params?.page_size) qs.set('page_size', String(params.page_size))
    const env = await http.get<ApiEnvelope<ApplicationListResp>>(`/api/v1/admin/jobs/applications?${qs.toString()}`)
    return unwrap(env)
  },
}

export const fmtSalary = (min: number | null, max: number | null) => {
  const yuan = (c: number) => `¥${(c / 100).toFixed(0)}`
  if (min && max) return `${yuan(min)} - ${yuan(max)}`
  if (min) return `${yuan(min)} 起`
  if (max) return `${yuan(max)} 以下`
  return '面议'
}

export const STAGE_LABELS: Record<ApplicationItem['stage'], string> = {
  applied: '已投递',
  screening: '初筛中',
  interview: '面试中',
  offer: '已发 Offer',
  rejected: '已拒绝',
}

export const STAGE_COLORS: Record<ApplicationItem['stage'], string> = {
  applied: 'blue',
  screening: 'cyan',
  interview: 'gold',
  offer: 'green',
  rejected: 'red',
}