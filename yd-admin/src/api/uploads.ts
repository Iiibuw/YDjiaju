/** 后台上传 API（对接后端 /api/v1/upload/*）。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface UploadResult {
  url: string // 公网可访问的完整 URL（如 http://127.0.0.1:8000/static/uploads/images/xxx.png）
  filename: string
  size: number
  content_type: string
}

/**
 * 上传图片（png/jpg/jpeg/webp/gif，≤5MB）。
 * @returns 公网 URL，前端拿到后直接填入 URL 输入框即可。
 */
export async function uploadImage(file: File): Promise<UploadResult> {
  const fd = new FormData()
  fd.append('file', file)
  const resp = await http.post<ApiEnvelope<UploadResult>>('/upload/image', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30_000, // 上传给 30s
  })
  return unwrap(resp)
}

/** 上传通用文件（pdf/doc/docx/xls/xlsx/txt/zip，≤10MB）。 */
export async function uploadFile(file: File): Promise<UploadResult> {
  const fd = new FormData()
  fd.append('file', file)
  const resp = await http.post<ApiEnvelope<UploadResult>>('/upload/file', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30_000,
  })
  return unwrap(resp)
}

/**
 * 校验图片 URL：
 * - 空：允许（封面图可选）
 * - 本地路径（C:\ / D:\ / ./ / /Users/）：拒绝（用户误填）
 * - 非 http/https 开头：拒绝
 * - http/https：放行
 *
 * @returns null 表示通过；string 表示校验失败提示文案。
 */
export function validateImageUrl(url: string | undefined | null): string | null {
  if (!url) return null
  const v = url.trim()
  if (!v) return null
  // 本地路径检测（Windows 反斜杠或盘符 / Mac/Linux 绝对路径 / 相对路径）
  if (/^[a-zA-Z]:[\\/]/.test(v) || /^[\\/]{1,2}(Users|home|tmp|var|opt)/.test(v) || /^\.{1,2}[\\/]/.test(v)) {
    return '请填写 https 开头的网络图片链接，或使用上传按钮上传图片'
  }
  // 必须是 http/https 开头
  if (!/^https?:\/\//i.test(v)) {
    return '请填写 https 开头的网络图片链接，或使用上传按钮上传图片'
  }
  return null
}