/**
 * 后台 HTTP 客户端。
 * - 适配后端 ApiEnvelope<T> 响应格式（与 shared/types/api-types.ts 一致）
 * - 自动注入 Bearer token
 * - 401 自动跳转 /login（M1 mock 阶段不处理）
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
  baseURL: import.meta.env.VITE_API_BASE ?? '/api',
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
    // 401 未登录：清除 token 等待上层路由跳转
    if (err?.response?.status === 401) {
      setToken(null)
    }
    return Promise.reject(err)
  },
)

/** 解包 ApiEnvelope：返回 data。 */
export function unwrap<T>(resp: AxiosResponse<ApiEnvelope<T>>): T {
  return resp.data.data
}
