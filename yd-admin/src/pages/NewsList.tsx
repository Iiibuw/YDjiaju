/** 后台资讯管理：列表 + 新建/编辑 + 删除。 */
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
  Tag,
  message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { newsAdmin, type NewsCreatePayload, type NewsItem } from '../api/news'

const CATEGORY_LABELS: Record<string, string> = {
  company: '企业新闻',
  industry: '行业资讯',
}

interface FormValues {
  title: string
  subtitle?: string
  category: 'company' | 'industry'
  cover_url?: string
  summary?: string
  content: string
  author?: string
  source?: string
  is_published: boolean
  is_top: boolean
  is_recommend: boolean
  sort?: number
  published_date?: string
  expire_date?: string
}

const empty: FormValues = {
  title: '',
  subtitle: '',
  category: 'company',
  cover_url: '',
  summary: '',
  content: '',
  author: '',
  source: '',
  is_published: false,
  is_top: false,
  is_recommend: false,
  sort: 0,
}

export default function NewsListPage() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [category, setCategory] = useState<string | undefined>()
  const [isPublished, setIsPublished] = useState<boolean | undefined>()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<NewsItem | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['admin-news', page, pageSize, keyword, category, isPublished],
    queryFn: () =>
      newsAdmin.list({
        page,
        page_size: pageSize,
        keyword: keyword || undefined,
        category,
        is_published: isPublished,
      }),
  })

  const createMut = useMutation({
    mutationFn: (p: FormValues) =>
      newsAdmin.create({
        ...p,
        cover_url: p.cover_url || null,
        summary: p.summary || null,
        subtitle: p.subtitle || null,
        author: p.author || null,
        source: p.source || null,
      } as NewsCreatePayload),
    onSuccess: () => {
      message.success('资讯已创建')
      setModalOpen(false)
      qc.invalidateQueries({ queryKey: ['admin-news'] })
    },
    onError: (e) => message.error(`创建失败：${(e as Error).message}`),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: FormValues }) =>
      newsAdmin.update(id, payload),
    onSuccess: () => {
      message.success('资讯已更新')
      setModalOpen(false)
      setEditing(null)
      qc.invalidateQueries({ queryKey: ['admin-news'] })
    },
    onError: (e) => message.error(`更新失败：${(e as Error).message}`),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => newsAdmin.delete(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-news'] })
    },
    onError: (e) => message.error(`删除失败：${(e as Error).message}`),
  })

  const columns: ColumnsType<NewsItem> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    {
      title: '标题',
      dataIndex: 'title',
      ellipsis: true,
      render: (t: string, r) => (
        <div className="flex items-center gap-2">
          <span className="font-medium">{t}</span>
          {r.is_top && <Tag color="orange">置顶</Tag>}
          {r.is_recommend && <Tag color="gold">推荐</Tag>}
        </div>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      width: 100,
      render: (c: string) => <Tag color={c === 'company' ? 'blue' : 'cyan'}>{CATEGORY_LABELS[c]}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'is_published',
      width: 90,
      render: (v: boolean) => (v ? <Tag color="green">已发布</Tag> : <Tag>草稿</Tag>),
    },
    { title: '浏览', dataIndex: 'view_count', width: 70 },
    {
      title: '发布时间',
      dataIndex: 'published_date',
      width: 170,
      render: (d: string | null) => (d ? new Date(d).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' }) : '-'),
    },
    {
      title: '操作',
      width: 160,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button size="small" type="link" onClick={() => { setEditing(r); setModalOpen(true) }}>编辑</Button>
          <Popconfirm title="确认删除该资讯？" okText="删除" cancelText="取消" onConfirm={() => deleteMut.mutate(r.id)}>
            <Button size="small" type="link" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const formInitial = editing
    ? {
        title: editing.title,
        subtitle: editing.subtitle ?? '',
        category: editing.category,
        cover_url: editing.cover_url ?? '',
        summary: editing.summary ?? '',
        content: editing.content,
        author: editing.author ?? '',
        source: editing.source ?? '',
        is_published: editing.is_published,
        is_top: editing.is_top,
        is_recommend: editing.is_recommend,
        sort: editing.sort,
      }
    : empty

  return (
    <Card
      title="资讯管理"
      extra={
        <Space>
          <Input.Search
            placeholder="搜索标题"
            allowClear
            onSearch={setKeyword}
            style={{ width: 220 }}
          />
          <Select
            placeholder="分类"
            allowClear
            style={{ width: 140 }}
            value={category}
            onChange={setCategory}
            options={[
              { value: 'company', label: '企业新闻' },
              { value: 'industry', label: '行业资讯' },
            ]}
          />
          <Select
            placeholder="状态"
            allowClear
            style={{ width: 120 }}
            value={isPublished}
            onChange={setIsPublished}
            options={[
              { value: true, label: '已发布' },
              { value: false, label: '草稿' },
            ]}
          />
          <Button type="primary" onClick={() => { setEditing(null); setModalOpen(true) }}>新建资讯</Button>
        </Space>
      }
    >
      <Table<NewsItem>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items ?? []}
        columns={columns}
        scroll={{ x: 900 }}
        pagination={{
          current: page,
          pageSize,
          total: data?.total,
          onChange: (p, ps) => { setPage(p); setPageSize(ps) },
        }}
      />

      <Modal
        open={modalOpen}
        title={editing ? '编辑资讯' : '新建资讯'}
        width={760}
        onCancel={() => { setModalOpen(false); setEditing(null) }}
        onOk={() => {
          // 通过 form ref submit（见下）
          ;(document.getElementById('news-form-submit') as HTMLButtonElement | null)?.click()
        }}
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
          key={editing?.id ?? 'new'}
        >
          <Form.Item name="title" label="标题" rules={[{ required: true, min: 2, max: 128 }]}>
            <Input placeholder="请输入标题（2-128 字）" />
          </Form.Item>
          <Form.Item name="subtitle" label="副标题">
            <Input placeholder="可选" maxLength={255} />
          </Form.Item>
          <div className="grid grid-cols-2 gap-4">
            <Form.Item name="category" label="分类" rules={[{ required: true }]}>
              <Select
                options={[
                  { value: 'company', label: '企业新闻' },
                  { value: 'industry', label: '行业资讯' },
                ]}
              />
            </Form.Item>
            <Form.Item name="cover_url" label="封面 URL">
              <Input placeholder="https://..." maxLength={255} />
            </Form.Item>
          </div>
          <Form.Item name="summary" label="摘要">
            <Input.TextArea rows={2} maxLength={500} showCount />
          </Form.Item>
          <Form.Item name="content" label="正文（HTML）" rules={[{ required: true, min: 1 }]}>
            <Input.TextArea rows={8} placeholder="<p>正文内容</p>" />
          </Form.Item>
          <div className="grid grid-cols-2 gap-4">
            <Form.Item name="author" label="作者"><Input /></Form.Item>
            <Form.Item name="source" label="来源"><Input /></Form.Item>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <Form.Item name="is_published" label="发布" valuePropName="checked"><Switch /></Form.Item>
            <Form.Item name="is_top" label="置顶" valuePropName="checked"><Switch /></Form.Item>
            <Form.Item name="is_recommend" label="推荐" valuePropName="checked"><Switch /></Form.Item>
          </div>
          <Form.Item name="sort" label="排序（数值大者优先）">
            <InputNumber min={0} max={9999} />
          </Form.Item>
          <button id="news-form-submit" type="submit" style={{ display: 'none' }} />
        </Form>
      </Modal>
    </Card>
  )
}