/** 后台登录鉴权 API（与后端 /api/v1/auth/* 对齐）。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface CaptchaOut {
  captcha_id: string
  captcha_image: string // data:image/png;base64,...
}

export interface LoginIn {
  username: string
  password: string
  captcha_id: string
  captcha_code: string
}

export interface AdminProfile {
  id: number
  username: string
  real_name: string
  email: string | null
  avatar_url: string | null
  dept_id: number | null
  dept_name: string | null
  roles: string[]
  permissions: string[]
}

export interface TokenOut {
  access_token: string
  token_type: 'Bearer'
  expires_in: number
  profile: AdminProfile
}

// ===== Mock 实现（M1 dev 期；后端就绪后接真实接口） =====
const USE_MOCK = true
const MOCK_DELAY = 200

function delay<T>(value: T, ms = MOCK_DELAY): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

const MOCK_CAPTCHA_PNG =
  'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40"><rect width="120" height="40" fill="%23f0f0f0"/><text x="60" y="26" text-anchor="middle" font-size="20" font-family="monospace" fill="%231677ff">A4B9</text></svg>'

export async function getCaptcha(): Promise<CaptchaOut> {
  if (USE_MOCK) {
    return delay({
      captcha_id: `mock-${Date.now()}`,
      captcha_image: MOCK_CAPTCHA_PNG,
    })
  }
  const resp = await http.get<ApiEnvelope<CaptchaOut>>('/auth/captcha')
  return unwrap(resp)
}

export async function login(payload: LoginIn): Promise<TokenOut> {
  if (USE_MOCK) {
    // 演示模式：任何用户名密码都通过（除 admin/admin123 必须）
    if (payload.username === 'admin' && payload.password === 'admin123') {
      return delay({
        access_token: 'mock-jwt-token-' + Date.now(),
        token_type: 'Bearer' as const,
        expires_in: 7200,
        profile: {
          id: 1,
          username: 'admin',
          real_name: '超级管理员',
          email: 'admin@yd.com',
          avatar_url: null,
          dept_id: 1,
          dept_name: '总经办',
          roles: ['admin'],
          permissions: ['*'],
        },
      })
    }
    throw new Error('用户名或密码错误（演示账户：admin / admin123）')
  }
  const resp = await http.post<ApiEnvelope<TokenOut>>('/auth/login', payload)
  return unwrap(resp)
}

export async function fetchProfile(): Promise<AdminProfile> {
  if (USE_MOCK) {
    return delay({
      id: 1,
      username: 'admin',
      real_name: '超级管理员',
      email: 'admin@yd.com',
      avatar_url: null,
      dept_id: 1,
      dept_name: '总经办',
      roles: ['admin'],
      permissions: ['*'],
    })
  }
  const resp = await http.get<ApiEnvelope<AdminProfile>>('/auth/profile')
  return unwrap(resp)
}

export async function logout(): Promise<void> {
  if (USE_MOCK) return
  await http.post('/auth/logout')
}
