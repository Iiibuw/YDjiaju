/** 后台资讯管理：列表 + 搜索 + 删除（新增/编辑均跳独立页）。 */
import { useState } from 'react'
import {
  Button,
  Card,
  Input,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  message,
} from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { newsAdmin, type NewsItem } from '../api/news'

const CATEGORY_LABELS: Record<string, string> = {
  company: '企业新闻',
  industry: '行业资讯',
}

export default function NewsListPage() {
  const qc = useQueryClient()
  const nav = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [category, setCategory] = useState<string | undefined>()
  const [isPublished, setIsPublished] = useState<boolean | undefined>()

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
      title: '封面',
      dataIndex: 'cover_url',
      width: 56,
      render: (url: string | null) =>
        url ? (
          <img
            src={url}
            alt=""
            loading="lazy"
            style={{
              width: 36,
              height: 36,
              objectFit: 'cover',
              flexShrink: 0,
              borderRadius: 4,
              display: 'block',
            }}
            onError={(e) => {
              ;(e.currentTarget as HTMLImageElement).style.opacity = '0.3'
            }}
          />
        ) : (
          <span className="text-xs text-gray-400">无</span>
        ),
    },
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
      render: (d: string | null) =>
        d ? new Date(d).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' }) : '-',
    },
    {
      title: '操作',
      width: 160,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          {/* 编辑 → 独立编辑页（非弹窗） */}
          <Button size="small" type="link" onClick={() => nav(`/news/edit/${r.id}`)}>
            编辑
          </Button>
          <Popconfirm
            title="确认删除该资讯？"
            okText="删除"
            cancelText="取消"
            onConfirm={() => deleteMut.mutate(r.id)}
          >
            <Button size="small" type="link" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

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
          <Button type="primary" icon={<PlusOutlined />} onClick={() => nav('/news/new')}>
            新建资讯
          </Button>
        </Space>
      }
    >
      <Table<NewsItem>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items ?? []}
        columns={columns}
        scroll={{ x: 1000 }}
        pagination={{
          current: page,
          pageSize,
          total: data?.total,
          onChange: (p, ps) => {
            setPage(p)
            setPageSize(ps)
          },
        }}
      />
    </Card>
  )
}