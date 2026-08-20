/** 后台部门管理（树形展示 + 新增/编辑/删除）。 */
import { useState } from 'react'
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tree,
  message,
} from 'antd'
import type { DataNode } from 'antd/es/tree'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { deptsAdmin, type DeptCreatePayload, type DeptNode, type DeptTreeNode } from '../api/depts'

interface FormValues {
  name: string
  code?: string
  parent_id?: number | null
  sort?: number
  is_activate?: boolean
}

const buildTreeData = (nodes: DeptTreeNode[]): DataNode[] =>
  nodes.map((n) => ({
    key: n.id,
    title: (
      <span>
        <span className="font-medium">{n.name}</span>
        {n.code && <span className="ml-2 text-xs text-gray-400">({n.code})</span>}
        {n.is_activate === 0 && <span className="ml-2 text-xs text-red-500">[禁用]</span>}
      </span>
    ),
    children: n.children?.length ? buildTreeData(n.children) : [],
  }))

const flatten = (nodes: DeptTreeNode[], depth = 0, out: DeptNode[] = []): DeptNode[] => {
  for (const n of nodes) {
    out.push({ id: n.id, name: n.name, code: n.code, parent_id: n.parent_id, sort: n.sort, leader_id: n.leader_id, is_activate: n.is_activate })
    if (n.children?.length) flatten(n.children, depth + 1, out)
  }
  return out
}

const empty: FormValues = { name: '', code: '', parent_id: undefined, is_activate: true }

export default function Departments() {
  const qc = useQueryClient()
  const nav = useNavigate()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<DeptNode | null>(null)
  const [parentHint, setParentHint] = useState<DeptNode | null>(null)

  const { data: tree = [], isLoading: treeLoading } = useQuery({
    queryKey: ['admin-depts-tree'],
    queryFn: () => deptsAdmin.listTree(),
  })

  const { data: flat = [] } = useQuery({
    queryKey: ['admin-depts-flat'],
    queryFn: () => deptsAdmin.listFlat(),
  })
  void flat  // 暂未直接用（M2-3 详情页/选择器会用到）

  const createMut = useMutation({
    mutationFn: (p: FormValues) => deptsAdmin.create(p as DeptCreatePayload),
    onSuccess: () => {
      message.success('部门已创建')
      setModalOpen(false)
      setEditing(null)
      setParentHint(null)
      qc.invalidateQueries({ queryKey: ['admin-depts-tree'] })
      qc.invalidateQueries({ queryKey: ['admin-depts-flat'] })
    },
    onError: (e) => message.error(`创建失败：${(e as Error).message}`),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<FormValues> }) =>
      deptsAdmin.update(id, payload),
    onSuccess: () => {
      message.success('部门已更新')
      setModalOpen(false)
      setEditing(null)
      qc.invalidateQueries({ queryKey: ['admin-depts-tree'] })
      qc.invalidateQueries({ queryKey: ['admin-depts-flat'] })
    },
    onError: (e) => message.error(`更新失败：${(e as Error).message}`),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => deptsAdmin.delete(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-depts-tree'] })
      qc.invalidateQueries({ queryKey: ['admin-depts-flat'] })
    },
    onError: (e) => message.error(`删除失败：${(e as Error).message}`),
  })

  // 平铺表格
  const flatRows = flatten(tree)
  const columns: ColumnsType<DeptNode> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    {
      title: '部门名称',
      dataIndex: 'name',
      render: (name: string, r) => (
        <div>
          <div className="font-medium">{name}</div>
          {r.code && <div className="text-xs text-gray-500">{r.code}</div>}
        </div>
      ),
    },
    {
      title: '上级',
      dataIndex: 'parent_id',
      width: 160,
      render: (pid: number | null) => {
        if (!pid) return <span className="text-gray-400">— 顶层 —</span>
        const p = flatRows.find((n) => n.id === pid)
        return <span>{p?.name ?? `#${pid}`}</span>
      },
    },
    { title: '排序', dataIndex: 'sort', width: 80 },
    {
      title: '状态',
      dataIndex: 'is_activate',
      width: 80,
      render: (v: number) => (v === 1 ? <span className="text-green-600">启用</span> : <span className="text-red-500">禁用</span>),
    },
    {
      title: '操作',
      width: 240,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button
            size="small"
            type="link"
            onClick={() => nav(`/depts/new?parent=${r.id}`)}
          >
            + 子部门
          </Button>
          <Button size="small" type="link" onClick={() => { setEditing(r); setParentHint(null); setModalOpen(true) }}>编辑</Button>
          <Popconfirm title="确认删除该部门？" onConfirm={() => deleteMut.mutate(r.id)}>
            <Button size="small" type="link" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const formInitial: FormValues = editing
    ? {
        name: editing.name,
        code: editing.code ?? '',
        parent_id: editing.parent_id,
        sort: editing.sort,
        is_activate: editing.is_activate === 1,
      }
    : {
        ...empty,
        parent_id: parentHint?.id ?? undefined,
      }

  const parentOptions = flatRows.map((n) => ({
    value: n.id,
    label: n.name,
  }))

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <Card
        title="部门树"
        extra={
          <Button type="primary" onClick={() => nav('/depts/new')}>
            新建顶层部门
          </Button>
        }
      >
        {treeLoading ? (
          <div className="py-8 text-center text-gray-400">加载中...</div>
        ) : (
          <Tree treeData={buildTreeData(tree)} defaultExpandAll />
        )}
      </Card>

      <Card title="部门列表（平铺）">
        <Table<DeptNode>
          rowKey="id"
          loading={treeLoading}
          dataSource={flatRows}
          columns={columns}
          pagination={false}
          size="small"
        />
      </Card>

      <Modal
        open={modalOpen}
        title={editing ? '编辑部门' : (parentHint ? `新建子部门（父：${parentHint.name}）` : '新建顶层部门')}
        width={520}
        onCancel={() => { setModalOpen(false); setEditing(null); setParentHint(null) }}
        onOk={() => (document.getElementById('dept-form-submit') as HTMLButtonElement | null)?.click()}
        confirmLoading={createMut.isPending || updateMut.isPending}
        destroyOnClose
      >
        <Form<FormValues>
          layout="vertical"
          initialValues={formInitial}
          onFinish={(vals) => {
            if (editing) updateMut.mutate({ id: editing.id, payload: vals })
            else createMut.mutate(vals)
          }}
          key={editing?.id ?? `new-${parentHint?.id ?? 'top'}`}
        >
          <Form.Item name="name" label="部门名称" rules={[{ required: true, min: 1 }]}>
            <Input />
          </Form.Item>
          <Form.Item name="code" label="部门编码（可空，唯一）">
            <Input />
          </Form.Item>
          <Form.Item name="parent_id" label="上级部门">
            <Select
              allowClear
              placeholder="顶层部门"
              options={parentOptions.filter((o) => o.value !== editing?.id)}
              disabled={!!editing}
            />
          </Form.Item>
          <Form.Item name="sort" label="排序"><InputNumber style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="is_activate" label="启用" valuePropName="checked"><Switch /></Form.Item>
          <button id="dept-form-submit" type="submit" style={{ display: 'none' }} />
        </Form>
      </Modal>
    </div>
  )
}