/**
 * 后台 HTTP 客户端。
 * - 适配后端 ApiEnvelope<T> 响应格式（与 shared/types/api-types.ts 一致）
 * - 自动注入 Bearer token
 * - 401 自动清除 token + 跳 /login
 * - baseURL = '/api/v1'：与后端 FastAPI 统一前缀对齐；具体端点路径写 '/admin/...'
 *   或 '/auth/...' 等裸路径即可。
 */
import axios, { type AxiosInstance, type AxiosResponse } from 'axios'

const STORAGE_KEY = 'yd_admin_token'

export function getToken(): string | null {
  return localStorage.getItem(STORAGE_KEY)
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(STORAGE_KEY, token)
  else localStorage.removeItem(STORAGE_KEY)
}

export interface ApiEnvelope<T> {
  code: number
  message: string
  data: T
}

export interface PageMeta {
  total: number
  page: number
  page_size: number
  total_pages: number
}

export const http: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE ?? '/api/v1',
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers = config.headers ?? {}
    ;(config.headers as Record<string, string>).Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (resp: AxiosResponse<ApiEnvelope<unknown>>) => {
    const body = resp.data
    if (body && typeof body === 'object' && 'code' in body && body.code !== 0) {
      return Promise.reject(new Error(body.message || 'API error'))
    }
    return resp
  },
  (err) => {
    // 401 未登录 / token 失效：清 token 并跳 /admin/login（保持与浏览器地址栏一致，
    // 配合 vite base='/admin/' 与 react-router basename='/admin'）。
    // 必须用相对路径而非裸 '/login'，否则会被浏览器解析为 http://<host>/login，
    // 落到 vite dev server 而非 React Router basename 内部。
    if (err?.response?.status === 401) {
      setToken(null)
      const path = window.location.pathname
      if (path !== '/admin/login') {
        // 同源跳转避免丢 token/hash 参数
        const target = '/admin/login'
        const here = window.location.pathname + window.location.search + window.location.hash
        if (here !== target) window.location.href = target
      }
    }
    return Promise.reject(err)
  },
)

/** 解包 ApiEnvelope：返回 data。 */
export function unwrap<T>(resp: AxiosResponse<ApiEnvelope<T>>): T {
  return resp.data.data
}
