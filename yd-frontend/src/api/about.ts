/** 关于我们 API 客户端（前台公开：区块 + 图集）。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface AboutImage {
  id: number
  url: string
  caption: string | null
  sort: number
}

export interface AboutSection {
  id: number
  code: string
  title: string
  subtitle: string | null
  body: string | null
  sort: number
  images: AboutImage[]
}

export async function listAboutSections(): Promise<AboutSection[]> {
  const env = await http.get<ApiEnvelope<AboutSection[]>>('/public/about-sections')
  return unwrap(env)
}
