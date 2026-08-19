/** 后台部门管理 API。 */
import { http, unwrap, type ApiEnvelope } from './http'

export interface DeptNode {
  id: number
  name: string
  code: string | null
  parent_id: number | null
  sort: number
  leader_id: number | null
  is_activate: number
  created_date?: string | null
  updated_date?: string | null
}

export interface DeptTreeNode extends DeptNode {
  children: DeptTreeNode[]
}

export interface DeptCreatePayload {
  name: string
  code?: string | null
  parent_id?: number | null
  sort?: number
  leader_id?: number | null
  is_activate?: boolean
}

export const deptsAdmin = {
  async listTree(): Promise<DeptTreeNode[]> {
    const env = await http.get<ApiEnvelope<DeptTreeNode[]>>('/admin/depts')
    return unwrap(env)
  },
  async listFlat(): Promise<DeptNode[]> {
    const env = await http.get<ApiEnvelope<DeptNode[]>>('/admin/depts/flat')
    return unwrap(env)
  },
  async create(payload: DeptCreatePayload) {
    const env = await http.post<ApiEnvelope<DeptNode>>('/admin/depts', payload)
    return unwrap(env)
  },
  async update(id: number, payload: Partial<DeptCreatePayload>) {
    const env = await http.put<ApiEnvelope<DeptNode>>(`/admin/depts/${id}`, payload)
    return unwrap(env)
  },
  async delete(id: number) {
    const env = await http.delete<ApiEnvelope<{ id: number }>>(`/admin/depts/${id}`)
    return unwrap(env)
  },
}