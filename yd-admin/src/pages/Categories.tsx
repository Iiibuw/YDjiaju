/** 后台分类管理：空间 / 系列 / 品类 三个 Tab，各自 新增/编辑/删除/启用禁用。 */
import { useState } from 'react'
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Space,
  Switch,
  Table,
  Tag,
  message,
} from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { adminCategories, type CategoryItem } from '../api/categories'

const KINDS = [
  { key: 'space', label: '空间', tip: '如：客厅 / 餐厅 / 卧室' },
  { key: 'series', label: '系列', tip: '如：胡桃禮系列 / 云杉系列' },
  { key: 'category', label: '品类', tip: '如：餐桌 / 沙发 / 床' },
]

interface FormValues {
  name: string
  sort?: number
  enabled?: boolean
}

export default function Categories() {
  const qc = useQueryClient()
  const [activeKind, setActiveKind] = useState('space')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<CategoryItem | null>(null)
  const [form] = Form.useForm<FormValues>()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-categories', activeKind],
    queryFn: () => adminCategories.list(activeKind),
  })
  const rows = data ?? []

  const createMut = useMutation({
    mutationFn: (p: FormValues) =>
      adminCategories.create({
        kind: activeKind,
        name: p.name,
        sort: p.sort ?? 0,
        enabled: p.enabled === false ? 0 : 1,
      }),
    onSuccess: () => {
      message.success('分类已创建')
      setModalOpen(false)
      form.resetFields()
      qc.invalidateQueries({ queryKey: ['admin-categories'] })
      qc.invalidateQueries({ queryKey: ['categories', 'all'] })
    },
    onError: (e: any) => message.error(e?.response?.data?.detail || '创建失败'),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: { name: string; sort?: number; enabled?: number } }) =>
      adminCategories.update(id, payload),
    onSuccess: () => {
      message.success('分类已更新')
      setModalOpen(false)
      form.resetFields()
      qc.invalidateQueries({ queryKey: ['admin-categories'] })
      qc.invalidateQueries({ queryKey: ['categories', 'all'] })
    },
    onError: (e: any) => message.error(e?.response?.data?.detail || '更新失败'),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => adminCategories.remove(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-categories'] })
      qc.invalidateQueries({ queryKey: ['categories', 'all'] })
    },
    onError: (e: any) =>
      message.error(e?.response?.data?.detail || e?.response?.data?.message || '删除失败(可能有产品引用)'),
  })

  const columns: ColumnsType<CategoryItem> = [
    { title: 'ID', dataIndex: 'id', width: 70 },
    {
      title: '名称',
      dataIndex: 'name',
      render: (name: string, r) => (
        <div className="font-medium">
          {name}
          {r.name_en && <span className="ml-2 text-xs text-gray-400">{r.name_en}</span>}
        </div>
      ),
    },
    { title: '排序', dataIndex: 'sort', width: 80, align: 'center' },
    {
      title: '状态',
      dataIndex: 'enabled',
      width: 90,
      render: (v: number) => (v === 1 || v === undefined ? <Tag color="green">启用</Tag> : <Tag>禁用</Tag>),
    },
    {
      title: '操作',
      width: 180,
      render: (_, r) => (
        <Space size="small">
          <Button
            size="small"
            type="link"
            onClick={() => {
              setEditing(r)
              form.setFieldsValue({
                name: r.name,
                sort: r.sort ?? 0,
                enabled: r.enabled !== 0,
              })
              setModalOpen(true)
            }}
          >
            编辑
          </Button>
          <Button
            size="small"
            type="link"
            danger
            onClick={() =>
              Modal.confirm({
                title: `确认删除分类「${r.name}」？`,
                content: '删除后该分类从筛选栏消失；若被产品引用将删除失败',
                okText: '删除',
                cancelText: '取消',
                okButtonProps: { danger: true },
                onOk: () => deleteMut.mutate(r.id),
              })
            }
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <Card
      title="分类管理"
      tabList={KINDS.map((k) => ({ key: k.key, tab: k.label }))}
      activeTabKey={activeKind}
      onTabChange={(k) => setActiveKind(k)}
      tabBarExtraContent={
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setModalOpen(true) }}>
          新增{KINDS.find((k) => k.key === activeKind)?.label}
        </Button>
      }
    >
      <p className="mb-4 text-sm text-gray-500">
        {KINDS.find((k) => k.key === activeKind)?.tip}——新增后前台「产品中心」左侧筛选栏自动同步显示。
      </p>
      <Table<CategoryItem>
        rowKey="id"
        loading={isLoading}
        dataSource={rows}
        columns={columns}
        pagination={false}
      />

      <Modal
        open={modalOpen}
        title={editing ? `编辑${KINDS.find((k) => k.key === activeKind)?.label}` : `新增${KINDS.find((k) => k.key === activeKind)?.label}`}
        onCancel={() => { setModalOpen(false); form.resetFields() }}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending || updateMut.isPending}
        destroyOnHidden
      >
        <Form<FormValues> form={form} layout="vertical" onFinish={(vals) => {
          if (editing) {
            updateMut.mutate({
              id: editing.id,
              payload: { name: vals.name, sort: vals.sort ?? 0, enabled: vals.enabled === false ? 0 : 1 },
            })
          } else {
            createMut.mutate(vals)
          }
        }}>
          <Form.Item name="name" label="名称" rules={[{ required: true, min: 1, max: 64 }]}>
            <Input placeholder={KINDS.find((k) => k.key === activeKind)?.tip} />
          </Form.Item>
          <Form.Item name="sort" label="排序号" tooltip="数值越大越靠前">
            <InputNumber min={0} max={9999} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="enabled" label="启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}