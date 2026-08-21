/** 后台产品管理：完整表格列（名称/副标题/系列/空间/品类/价格/排序/状态/封面/时间/操作）+ 搜索 + 上下架 + 删除。 */
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
import { listCategories } from '../api/categories'

const STATUS_OPTIONS: { value: ProductStatus; label: string; color: string }[] = [
  { value: 'draft', label: '草稿', color: 'default' },
  { value: 'on_sale', label: '在售', color: 'green' },
  { value: 'off_sale', label: '下架', color: 'orange' },
]
const STATUS_COLOR: Record<string, string> = Object.fromEntries(
  STATUS_OPTIONS.map((o) => [o.value, o.color]),
)

/** 分 → 元 */
const fmtYuan = (cents?: number | null) =>
  cents != null ? `¥${(cents / 100).toLocaleString('zh-CN', { minimumFractionDigits: 0 })}` : '-'

export default function Products() {
  const qc = useQueryClient()
  const nav = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [statusFilter, setStatusFilter] = useState<ProductStatus | undefined>()
  const [spaceId, setSpaceId] = useState<number | undefined>()

  // 分类(空间/系列/品类)
  const { data: cats } = useQuery({
    queryKey: ['categories', 'all'],
    queryFn: () => listCategories(),
    staleTime: 60_000,
  })
  const spaceOptions = (cats ?? []).filter((c) => c.kind === 'space').map((c) => ({ value: c.id, label: c.name }))

  const { data, isLoading } = useQuery({
    queryKey: ['admin-products', page, pageSize, keyword, statusFilter, spaceId],
    queryFn: () =>
      productsAdmin.list({
        page,
        page_size: pageSize,
        keyword: keyword || undefined,
        status_filter: statusFilter,
        category_id: spaceId,
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
      title: '产品标题',
      dataIndex: 'name',
      ellipsis: true,
      render: (name: string, r) => (
        <div>
          <div className="font-medium">{name}</div>
          {r.subtitle && <div className="text-xs text-gray-500">{r.subtitle}</div>}
        </div>
      ),
    },
    {
      title: '系列',
      dataIndex: 'series_name',
      width: 110,
      render: (v: string | null) => v || <span className="text-gray-400">-</span>,
    },
    {
      title: '空间',
      dataIndex: 'space_name',
      width: 90,
      render: (v: string | null) => v || <span className="text-gray-400">-</span>,
    },
    {
      title: '品类',
      dataIndex: 'category_name',
      width: 110,
      render: (v: string | null) => v || <span className="text-gray-400">-</span>,
    },
    {
      title: '最低价',
      width: 110,
      render: (_, r) => fmtYuan(r.min_price_cents),
    },
    {
      title: '最高价',
      width: 110,
      render: (_, r) => fmtYuan(r.max_price_cents),
    },
    { title: '排序', dataIndex: 'sort', width: 70, align: 'center' },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (s: string) => (
        <Tag color={STATUS_COLOR[s] || 'default'}>
          {STATUS_OPTIONS.find((o) => o.value === s)?.label ?? s}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_date',
      width: 150,
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
                  content: '下架后前台产品中心不再展示',
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
              disabled={r.status === 'draft' && r.is_top ? true : false}
              onClick={() =>
                Modal.confirm({
                  title: '确认上架该产品？',
                  content: '上架后前台产品中心将展示该产品',
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
            placeholder="搜索产品标题"
            allowClear
            onSearch={(v) => {
              setKeyword(v)
              setPage(1)
            }}
            style={{ width: 200 }}
          />
          <Select
            placeholder="空间"
            allowClear
            style={{ width: 110 }}
            value={spaceId}
            onChange={(v) => {
              setSpaceId(v)
              setPage(1)
            }}
            options={spaceOptions}
          />
          <Select
            placeholder="状态"
            allowClear
            style={{ width: 100 }}
            value={statusFilter}
            onChange={(v) => {
              setStatusFilter(v)
              setPage(1)
            }}
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
        scroll={{ x: 1400 }}
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