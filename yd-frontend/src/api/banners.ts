/** 轮播图 API 客户端（前台公开）。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface Banner {
  id: number
  title: string
  image_url: string
  link_type: 'product' | 'news' | 'case' | 'url'
  link_target: string
  sort: number
}

export async function listBanners(): Promise<Banner[]> {
  const env = await http.get<ApiEnvelope<Banner[]>>('/public/banners')
  return unwrap(env)
}
