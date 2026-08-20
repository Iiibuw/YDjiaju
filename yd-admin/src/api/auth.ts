/** 后台登录鉴权 API（对接真实后端 /api/v1/auth/*）。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface CaptchaOut {
  captcha_id: string
  captcha_image: string // data:image/png;base64,...
  expires_in: number
}

export interface LoginIn {
  username: string
  password: string
  captcha_id: string
  captcha_code: string
}

/** 对齐后端 app/schemas/auth.py TokenOut（登录响应无 profile 字段）。 */
export interface TokenOut {
  access_token: string
  token_type: 'Bearer'
  expires_in: number
  admin_id: number
  real_name: string | null
  role: string | null
  avatar_url: string | null
}

/** 对齐后端 AdminProfileOut（GET /auth/me）。 */
export interface AdminProfile {
  id: number
  username: string
  real_name: string | null
  nickname: string | null
  avatar_url: string | null
  email: string | null
  role: string | null
  dept_name: string | null
  data_scope: string
}

export async function getCaptcha(): Promise<CaptchaOut> {
  const resp = await http.get<ApiEnvelope<CaptchaOut>>('/auth/captcha')
  return unwrap(resp)
}

export async function login(payload: LoginIn): Promise<TokenOut> {
  const resp = await http.post<ApiEnvelope<TokenOut>>('/auth/login', payload)
  return unwrap(resp)
}

export async function fetchProfile(): Promise<AdminProfile> {
  const resp = await http.get<ApiEnvelope<AdminProfile>>('/auth/me')
  return unwrap(resp)
}

export async function logout(): Promise<void> {
  await http.post('/auth/logout')
}

/** 改自己密码。 */
export interface ChangePasswordIn {
  old_password: string
  new_password: string
}

export async function changePassword(payload: ChangePasswordIn): Promise<void> {
  await http.post<ApiEnvelope<null>>('/auth/change-password', payload)
}
