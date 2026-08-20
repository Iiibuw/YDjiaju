/** 独立「新增部门」页：名称/编码/上级/排序/启用。 */
import { Button, Card, Form, Input, InputNumber, Select, Space, Switch, message } from 'antd'
import { ArrowLeftOutlined, PlusOutlined } from '@ant-design/icons'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { deptsAdmin, type DeptTreeNode } from '../api/depts'

interface FormValues {
  name: string
  code?: string
  parent_id?: number | null
  sort?: number
  is_activate?: boolean
}

export default function DeptNewPage() {
  const nav = useNavigate()
  const [searchParams] = useSearchParams()
  const parentId = searchParams.get('parent') ? Number(searchParams.get('parent')) : undefined
  const qc = useQueryClient()
  const [form] = Form.useForm<FormValues>()

  // 上级部门选项（树）
  const { data: tree } = useQuery({
    queryKey: ['admin-depts-tree'],
    queryFn: () => deptsAdmin.listTree(),
    staleTime: 30_000,
  })

  // 拍平树
  const flatten = (nodes: DeptTreeNode[]): DeptTreeNode[] =>
    nodes.flatMap((n) => [n, ...flatten(n.children ?? [])])
  const flat = flatten(tree ?? [])

  const createMut = useMutation({
    mutationFn: (p: FormValues) =>
      deptsAdmin.create({
        name: p.name,
        code: p.code || null,
        parent_id: p.parent_id ?? null,
        sort: p.sort ?? 0,
        is_activate: p.is_activate,
      }),
    onSuccess: () => {
      message.success('部门已创建')
      qc.invalidateQueries({ queryKey: ['admin-depts-tree'] })
      qc.invalidateQueries({ queryKey: ['admin-depts-flat'] })
      nav('/depts')
    },
    onError: (e: any) => {
      message.error(`创建失败：${e?.response?.data?.message || (e as Error).message}`)
    },
  })

  return (
    <Card
      title={
        <Space>
          <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => nav('/depts')}>
            返回列表
          </Button>
          新增部门
        </Space>
      }
      extra={
        <Space>
          <Button onClick={() => nav('/depts')}>取消</Button>
          <Button type="primary" icon={<PlusOutlined />} loading={createMut.isPending} onClick={() => form.submit()}>
            保存
          </Button>
        </Space>
      }
    >
      <div className="mx-auto max-w-lg">
        <Form<FormValues>
          form={form}
          layout="vertical"
          onFinish={(vals) => createMut.mutate(vals)}
          initialValues={{ name: '', code: '', parent_id: parentId, sort: 0, is_activate: true }}
        >
          <Form.Item name="name" label="部门名称" rules={[{ required: true, min: 1 }]}>
            <Input placeholder="如：设计中心" />
          </Form.Item>
          <Form.Item name="code" label="部门编码" extra="可空，唯一">
            <Input placeholder="如：DESIGN_CTR" />
          </Form.Item>
          <Form.Item name="parent_id" label="上级部门">
            <Select
              allowClear
              placeholder="不选则为顶层部门"
              options={flat.map((n) => ({ value: n.id, label: n.name }))}
            />
          </Form.Item>
          <div className="grid grid-cols-2 gap-4">
            <Form.Item name="sort" label="排序">
              <InputNumber min={0} max={9999} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="is_activate" label="启用" valuePropName="checked">
              <Switch />
            </Form.Item>
          </div>
        </Form>
      </div>
    </Card>
  )
}