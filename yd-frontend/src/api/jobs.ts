/** 招聘 API 客户端（前台）。后端未启动时回退到 mock。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface JobListItem {
  id: number
  title: string
  category: 'social' | 'campus'
  department: string | null
  location: string | null
  salary_min_cents: number | null
  salary_max_cents: number | null
  headcount: number
  publish_date: string | null
  expire_date: string | null
}

export interface JobDetail extends JobListItem {
  description: string | null
  requirement: string | null
  created_date: string
  updated_date: string
}

export interface ListJobsResp {
  items: JobListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

const mockJobs: JobListItem[] = [
  {
    id: 1,
    title: '高级家具设计师',
    category: 'social',
    department: '设计中心',
    location: '佛山',
    salary_min_cents: 1500000,
    salary_max_cents: 2500000,
    headcount: 2,
    publish_date: '2026-08-17T10:00:00',
    expire_date: '2026-10-18T10:00:00',
  },
  {
    id: 2,
    title: '电商运营专员',
    category: 'social',
    department: '电商部',
    location: '佛山',
    salary_min_cents: 800000,
    salary_max_cents: 1200000,
    headcount: 1,
    publish_date: '2026-08-14T10:00:00',
    expire_date: '2026-09-18T10:00:00',
  },
  {
    id: 3,
    title: '2027 届校园招聘 - 产品设计培训生',
    category: 'campus',
    department: '管培生项目',
    location: '佛山',
    salary_min_cents: 800000,
    salary_max_cents: 1200000,
    headcount: 10,
    publish_date: '2026-08-09T10:00:00',
    expire_date: '2026-11-17T10:00:00',
  },
]

const mockDetail = (id: number): JobDetail => ({
  ...(mockJobs.find((j) => j.id === id) ?? mockJobs[0]),
  description: '<p>负责实木家具的产品设计与研发。</p>',
  requirement: '<ul><li>5 年以上实木家具设计经验</li><li>熟练使用 SolidWorks/Rhino</li></ul>',
  created_date: '2026-08-01T10:00:00',
  updated_date: '2026-08-17T10:00:00',
})

export const fmtSalary = (min: number | null, max: number | null) => {
  const yuan = (c: number) => `¥${(c / 100).toFixed(0)}`
  if (min && max) return `${yuan(min)} - ${yuan(max)}`
  if (min) return `${yuan(min)} 起`
  if (max) return `${yuan(max)} 以下`
  return '面议'
}

export async function listJobs(params?: { category?: string; keyword?: string; page?: number; page_size?: number }): Promise<ListJobsResp> {
  const qs = new URLSearchParams()
  if (params?.category) qs.set('category', params.category)
  if (params?.keyword) qs.set('keyword', params.keyword)
  if (params?.page) qs.set('page', String(params.page))
  if (params?.page_size) qs.set('page_size', String(params.page_size))
  try {
    const env = await http.get<ApiEnvelope<ListJobsResp>>(`/public/jobs?${qs.toString()}`)
    return unwrap(env)
  } catch {
    return { items: mockJobs, total: mockJobs.length, page: 1, page_size: 20, total_pages: 1 }
  }
}

export async function getJobDetail(id: number): Promise<JobDetail | null> {
  try {
    const env = await http.get<ApiEnvelope<JobDetail>>(`/public/jobs/${id}`)
    return unwrap(env)
  } catch {
    return mockDetail(id)
  }
}

export interface ApplyPayload {
  job_id: number
  name: string
  phone: string
  email?: string | null
}

export async function applyJob(payload: ApplyPayload): Promise<{ id: number; stage: string }> {
  const env = await http.post<ApiEnvelope<{ id: number; stage: string }>>('/public/jobs/apply', payload)
  return unwrap(env)
}

export interface MyApplication {
  id: number
  job_id: number
  job_title: string | null
  name: string
  phone: string
  stage: string
  applied_date: string | null
}

export interface ListMyAppsResp {
  items: MyApplication[]
  total: number
}

export async function listMyApplications(): Promise<ListMyAppsResp> {
  const env = await http.get<ApiEnvelope<ListMyAppsResp>>('/public/jobs/applications/me')
  return unwrap(env)
}