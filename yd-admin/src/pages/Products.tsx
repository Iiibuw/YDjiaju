/** 后台产品管理：列表 + 搜索 + 上架/下架/置顶 + 删除；新增/编辑跳独立页。 */
import { useState } from 'react'
import {
  Button,
  Card,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  message,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  StopOutlined,
  CheckCircleOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { productsAdmin, type ProductItem, type ProductStatus } from '../api/products'

const STATUS_OPTIONS: { value: ProductStatus; label: string; color: string }[] = [
  { value: 'draft', label: '草稿', color: 'default' },
  { value: 'on_sale', label: '在售', color: 'green' },
  { value: 'off_sale', label: '下架', color: 'orange' },
]
const STATUS_COLOR: Record<string, string> = Object.fromEntries(
  STATUS_OPTIONS.map((o) => [o.value, o.color]),
)

const fmtPrice = (cents?: number | null) =>
  cents ? `¥${(cents / 100).toLocaleString()}` : '-'

export default function Products() {
  const qc = useQueryClient()
  const nav = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [statusFilter, setStatusFilter] = useState<ProductStatus | undefined>()
  const [spaceFilter, setSpaceFilter] = useState<string | undefined>()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-products', page, pageSize, keyword, statusFilter, spaceFilter],
    queryFn: () =>
      productsAdmin.list({
        page,
        page_size: pageSize,
        keyword: keyword || undefined,
        status: statusFilter,
        space: spaceFilter,
      }),
  })

  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: ProductStatus }) =>
      productsAdmin.update(id, { status }),
    onSuccess: (_, vars) => {
      message.success(vars.status === 'on_sale' ? '已上架' : '已下架')
      qc.invalidateQueries({ queryKey: ['admin-products'] })
    },
    onError: (e: any) => message.error(e?.response?.data?.message || '操作失败'),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => productsAdmin.remove(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-products'] })
    },
    onError: (e: any) => message.error(e?.response?.data?.message || '删除失败'),
  })

  const columns: ColumnsType<ProductItem> = [
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
      title: '产品',
      dataIndex: 'title',
      ellipsis: true,
      render: (t: string, r) => (
        <div>
          <div className="font-medium">{t}</div>
          <div className="text-xs text-gray-500">
            {[r.series, r.space, r.style].filter(Boolean).join(' · ') || '-'}
          </div>
        </div>
      ),
    },
    {
      title: '价格',
      width: 140,
      render: (_, r) => (
        <span>
          {fmtPrice(r.min_price_cents)} ~ {fmtPrice(r.max_price_cents)}
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (s: string) => (
        <Tag color={STATUS_COLOR[s] || 'default'}>
          {STATUS_OPTIONS.find((o) => o.value === s)?.label ?? s}
        </Tag>
      ),
    },
    {
      title: '上架时间',
      dataIndex: 'updated_date',
      width: 170,
      render: (d: string | null) =>
        d ? new Date(d).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' }) : '-',
    },
    {
      title: '操作',
      width: 200,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button size="small" type="link" icon={<EditOutlined />} onClick={() => nav(`/products/edit/${r.id}`)}>
            编辑
          </Button>
          {r.status === 'on_sale' ? (
            <Button
              size="small"
              type="link"
              icon={<StopOutlined />}
              style={{ color: '#fa8c16' }}
              onClick={() =>
                Modal.confirm({
                  title: '确认下架该产品？',
                  content: '下架后前台不再展示',
                  okText: '下架',
                  cancelText: '取消',
                  okButtonProps: { style: { backgroundColor: '#fa8c16', borderColor: '#fa8c16' } },
                  onOk: () => statusMut.mutate({ id: r.id, status: 'off_sale' }),
                })
              }
            >
              下架
            </Button>
          ) : (
            <Button
              size="small"
              type="link"
              icon={<CheckCircleOutlined />}
              style={{ color: '#52c41a' }}
              onClick={() =>
                Modal.confirm({
                  title: '确认上架该产品？',
                  okText: '上架',
                  cancelText: '取消',
                  onOk: () => statusMut.mutate({ id: r.id, status: 'on_sale' }),
                })
              }
            >
              上架
            </Button>
          )}
          <Button
            size="small"
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() =>
              Modal.confirm({
                title: '确认删除该产品？',
                content: '删除后数据无法恢复',
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
      title="产品管理"
      extra={
        <Space>
          <Input.Search
            placeholder="搜索标题"
            allowClear
            onSearch={setKeyword}
            style={{ width: 220 }}
          />
          <Select
            placeholder="空间"
            allowClear
            style={{ width: 120 }}
            value={spaceFilter}
            onChange={setSpaceFilter}
            options={[
              { value: '客厅', label: '客厅' },
              { value: '餐厅', label: '餐厅' },
              { value: '卧室', label: '卧室' },
              { value: '书房', label: '书房' },
              { value: '茶室', label: '茶室' },
              { value: '办公', label: '办公' },
            ]}
          />
          <Select
            placeholder="状态"
            allowClear
            style={{ width: 120 }}
            value={statusFilter}
            onChange={setStatusFilter}
            options={STATUS_OPTIONS.map((o) => ({ value: o.value, label: o.label }))}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => nav('/products/new')}>
            新建产品
          </Button>
        </Space>
      }
    >
      <Table<ProductItem>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items ?? []}
        columns={columns}
        scroll={{ x: 1100 }}
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