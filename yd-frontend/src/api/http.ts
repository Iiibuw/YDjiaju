/** Axios 客户端封装（技术文档 §5）。
 * - 拦截器：注入 Bearer token；401 自动跳转登录
 * - 自动解包 ApiResponse.data
 * - 错误统一处理
 */
import axios, { AxiosError, type AxiosInstance, type AxiosResponse } from 'axios'

// dev 走 vite proxy（vite.config.ts 将 /api → :8000），prod 同源 /api/v1；
// 部署到独立后端时用 VITE_API_BASE_URL 覆盖。
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1'

export const http: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10_000,
  withCredentials: false, // JWT 不放 cookie
})

// ===== token 持久化：按当前路径分流——后台(/admin)用 admin token,前台用 member token =====
const TOKEN_KEY = 'yd_admin_token'
const MEMBER_TOKEN_KEY = 'yd_member_token'

const isAdminPath = () =>
  typeof location !== 'undefined' && location.pathname.startsWith('/admin')

export const tokenStore = {
  get: (): string | null => {
    if (isAdminPath()) return localStorage.getItem(TOKEN_KEY)
    return localStorage.getItem(MEMBER_TOKEN_KEY) || localStorage.getItem(TOKEN_KEY)
  },
  set: (t: string) => {
    if (isAdminPath()) localStorage.setItem(TOKEN_KEY, t)
    else localStorage.setItem(MEMBER_TOKEN_KEY, t)
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(MEMBER_TOKEN_KEY)
  },
}

// ===== 拦截器：注入 token =====
http.interceptors.request.use((config) => {
  const t = tokenStore.get()
  if (t) config.headers.Authorization = `Bearer ${t}`
  return config
})

// ===== 统一响应结构 =====

export interface ApiEnvelope<T> {
  code: number
  message: string
  data: T
  trace_id?: string | null
}

export class ApiError extends Error {
  code: number
  status: number
  constructor(message: string, code: number, status: number) {
    super(message)
    this.code = code
    this.status = status
  }
}

// ===== 拦截器：解包 + 错误归一化 =====
http.interceptors.response.use(
  (resp: AxiosResponse<ApiEnvelope<unknown>>) => {
    const body = resp.data
    // 后端用 ApiResponse 包装：code=0 成功
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) return resp  // 解包 data 由各 wrapper 处理
      throw new ApiError(body.message || '业务错误', body.code, resp.status)
    }
    // 非包装响应（如 /docs、/openapi.json）
    return resp
  },
  (err: AxiosError<ApiEnvelope<unknown>>) => {
    const status = err.response?.status ?? 0
    const body = err.response?.data
    if (status === 401) {
      tokenStore.clear()
      // 简单跳转（M2 改为 router push）
      if (location.pathname.startsWith('/admin')) location.href = '/login'
    }
    throw new ApiError(
      body?.message || err.message || '网络错误',
      body?.code ?? -1,
      status,
    )
  },
)

/** 解包 ApiResponse.data（业务接口 helper） */
export function unwrap<T>(resp: AxiosResponse<ApiEnvelope<T>>): T {
  return (resp.data as ApiEnvelope<T>).data
}
