/** 与后端 auth.py 对齐（M1 dev 期间返回 mock 登录，后端就绪后切真实）。 */
import { http, tokenStore, unwrap, type ApiEnvelope } from './http'

export interface CaptchaOut {
  captcha_id: string
  captcha_image: string // data URI
  expires_in: number
}

export interface LoginIn {
  username: string
  password: string
  captcha_id: string
  captcha_code: string
}

export interface TokenOut {
  access_token: string
  token_type: string
  expires_in: number
  admin_id: number
  real_name: string | null
  role: string | null
  avatar_url: string | null
}

const USE_MOCK = true

export async function getCaptcha(): Promise<CaptchaOut> {
  if (USE_MOCK) {
    // mock：一个固定 id + 占位 SVG
    return {
      captcha_id: 'mock-' + Date.now(),
      captcha_image:
        'data:image/svg+xml;utf8,' +
        encodeURIComponent(
          `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40" viewBox="0 0 120 40">
             <rect width="120" height="40" fill="#f5f5f4"/>
             <text x="60" y="26" text-anchor="middle" font-family="monospace" font-size="22" fill="#57534e">A7K9</text>
             <line x1="0" y1="20" x2="120" y2="20" stroke="#d6d3d1"/>
           </svg>`,
        ),
      expires_in: 300,
    }
  }
  const resp = await http.get<ApiEnvelope<CaptchaOut>>('/auth/captcha')
  return unwrap(resp)
}

export async function login(payload: LoginIn): Promise<TokenOut> {
  if (USE_MOCK) {
    if (payload.username === 'admin' && payload.password === 'admin123') {
      const token = 'mock-jwt-token-' + Date.now()
      tokenStore.set(token)
      return {
        access_token: token,
        token_type: 'Bearer',
        expires_in: 7200,
        admin_id: 1,
        real_name: '管理员',
        role: 'admin',
        avatar_url: null,
      }
    }
    throw new Error('账号或密码错误（演示账号：admin / admin123）')
  }
  const resp = await http.post<ApiEnvelope<TokenOut>>('/auth/login', payload)
  const data = unwrap(resp)
  tokenStore.set(data.access_token)
  return data
}

export async function logout() {
  tokenStore.clear()
}
