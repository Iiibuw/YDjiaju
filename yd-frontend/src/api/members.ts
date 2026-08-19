/** 前台会员 + 留言 API。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface MemberOut {
  id: number
  phone: string
  nickname: string | null
  avatar_url: string | null
  email: string | null
  gender: number | null
  created_date: string | null
  last_login_date: string | null
}

export interface MemberLoginResp {
  access_token: string
  token_type: string
  expires_in: number
  member: MemberOut
}

export interface MessageOut {
  id: number
  name: string
  phone: string | null
  email: string | null
  content: string
  status: string
  created_date: string | null
}

export async function submitMessage(payload: { name: string; phone?: string; email?: string; content: string }): Promise<MessageOut> {
  const env = await http.post<ApiEnvelope<MessageOut>>('/members/messages', payload)
  return unwrap(env)
}

export async function memberLogin(payload: { phone: string; password: string }): Promise<MemberLoginResp> {
  const env = await http.post<ApiEnvelope<MemberLoginResp>>('/members/login', payload)
  return unwrap(env)
}