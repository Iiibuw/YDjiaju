/** 后台案例管理（AntD Table + Form + Modal）。 */
import { useState } from 'react'
import {
  Button,
  Card,
  Form,
  Image,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { casesAdmin, type CaseCreatePayload, type CaseItem } from '../api/cases'
import RichTextEditor from '../components/RichTextEditor'

interface FormValues {
  title: string
  cover_url: string
  style?: string
  area?: string
  description?: string
  sort?: number
}

const empty: FormValues = {
  title: '',
  cover_url: '',
  style: '',
  area: '',
  description: '',
  sort: 0,
}

const STYLE_OPTIONS = [
  { value: '现代简约', label: '现代简约' },
  { value: '现代北欧', label: '现代北欧' },
  { value: '新中式', label: '新中式' },
  { value: '轻奢风', label: '轻奢风' },
  { value: '极简', label: '极简' },
  { value: '工业风', label: '工业风' },
]

export default function Cases() {
  const qc = useQueryClient()
  const nav = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<CaseItem | null>(null)
  const [form] = Form.useForm<FormValues>()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-cases', page, pageSize, keyword],
    queryFn: () => casesAdmin.list({ page, page_size: pageSize, keyword: keyword || undefined }),
  })

  const createMut = useMutation({
    mutationFn: (p: FormValues) => casesAdmin.create(p as CaseCreatePayload),
    onSuccess: () => {
      message.success('案例已创建')
      setModalOpen(false)
      qc.invalidateQueries({ queryKey: ['admin-cases'] })
    },
    onError: (e) => message.error(`创建失败：${(e as Error).message}`),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<FormValues> }) =>
      casesAdmin.update(id, payload),
    onSuccess: () => {
      message.success('案例已更新')
      setModalOpen(false)
      setEditing(null)
      qc.invalidateQueries({ queryKey: ['admin-cases'] })
    },
    onError: (e) => message.error(`更新失败：${(e as Error).message}`),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => casesAdmin.delete(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-cases'] })
    },
    onError: (e) => message.error(`删除失败：${(e as Error).message}`),
  })

  const columns: ColumnsType<CaseItem> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    {
      title: '案例',
      width: 360,
      render: (_, r) => (
        <div className="flex items-center gap-3">
          <Image src={r.cover_url} width={60} height={48} className="!rounded-md object-cover" />
          <div>
            <div className="font-medium">{r.title}</div>
            <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
              {r.style && <Tag color="blue">{r.style}</Tag>}
              {r.area && <span>{r.area}</span>}
              {r.is_deleted === 1 && <Tag color="red">已删除</Tag>}
            </div>
          </div>
        </div>
      ),
    },
    { title: '风格', dataIndex: 'style', width: 100, render: (s: string | null) => s || '-' },
    { title: '面积', dataIndex: 'area', width: 90, render: (a: string | null) => a || '-' },
    { title: '浏览', dataIndex: 'view_count', width: 70 },
    {
      title: '发布时间',
      dataIndex: 'published_date',
      width: 110,
      render: (d: string) => new Date(d).toLocaleDateString('zh-CN'),
    },
    {
      title: '操作',
      width: 160,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button size="small" type="link" onClick={() => { setEditing(r); setModalOpen(true) }}>编辑</Button>
          <Popconfirm title="确认删除该案例？" onConfirm={() => deleteMut.mutate(r.id)}>
            <Button size="small" type="link" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const formInitial: FormValues = editing
    ? {
        title: editing.title,
        cover_url: editing.cover_url,
        style: editing.style ?? '',
        area: editing.area ?? '',
        description: editing.description ?? '',
        sort: editing.sort,
      }
    : empty

  return (
    <Card
      title="案例列表"
      extra={
        <Space>
          <Input.Search placeholder="搜索标题" allowClear onSearch={setKeyword} style={{ width: 220 }} />
          <Button type="primary" onClick={() => nav('/cases/new')}>新建案例</Button>
        </Space>
      }
    >
      <Table<CaseItem>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items ?? []}
        columns={columns}
        scroll={{ x: 1100 }}
        pagination={{ current: page, pageSize, total: data?.total, onChange: (p, ps) => { setPage(p); setPageSize(ps) } }}
      />

      <Modal
        open={modalOpen}
        title={editing ? '编辑案例' : '新建案例'}
        width={760}
        onCancel={() => {
          setModalOpen(false)
          setEditing(null)
          form.resetFields()
        }}
        onOk={() => form.submit()}
        confirmLoading={createMut.isPending || updateMut.isPending}
        destroyOnClose
      >
        <Form<FormValues>
          form={form}
          layout="vertical"
          initialValues={formInitial}
          onFinish={(vals) => {
            if (editing) updateMut.mutate({ id: editing.id, payload: vals })
            else createMut.mutate(vals)
          }}
          key={editing?.id ?? 'new'}
        >
          <Form.Item name="title" label="案例标题" rules={[{ required: true, min: 2 }]}>
            <Input placeholder="如：胡桃禮·广州海珠湾花园别墅" />
          </Form.Item>
          <Form.Item name="cover_url" label="封面图 URL" rules={[{ required: true, type: 'url' }]}>
            <Input placeholder="https://..." />
          </Form.Item>
          <Form.Item name="style" label="风格">
            <Select allowClear placeholder="选择风格" options={STYLE_OPTIONS} />
          </Form.Item>
          <Form.Item name="area" label="面积（如 120㎡）">
            <Input />
          </Form.Item>
          <Form.Item name="sort" label="排序（越大越靠前，999=置顶）">
            <InputNumber min={0} max={999} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="description" label="项目详情（HTML）">
            <RichField name="description" placeholder="项目详情，支持加粗、颜色、对齐、图片..." minHeight={300} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}

/** RichTextEditor wrapper for Form.Item in this file */
function RichField({ name, placeholder, minHeight }: { name: string; placeholder?: string; minHeight?: number }) {
  const f = Form.useFormInstance<FormValues>()
  const v = (f.getFieldValue(name as never) as string | undefined) ?? ''
  return (
    <RichTextEditor
      value={v}
      onChange={(html) => f.setFieldValue(name as never, html as never)}
      placeholder={placeholder}
      minHeight={minHeight}
    />
  )
}