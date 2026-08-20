/** 下载中心 API 客户端（前台公开）。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface Download {
  id: number
  title: string
  category: 'catalog' | 'manual' | 'cad' | 'other'
  description: string | null
  file_url: string
  file_size_kb: number | null
  file_format: string | null
  download_count: number
  sort: number
}

export interface ListDownloadsResp {
  items: Download[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export async function listDownloads(params?: {
  category?: string
  page?: number
  page_size?: number
}): Promise<ListDownloadsResp> {
  const env = await http.get<ApiEnvelope<ListDownloadsResp>>('/public/downloads', { params })
  return unwrap(env)
}
