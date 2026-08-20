/** 后台订单管理：列表 + 状态流转（pending→paid→shipped→completed/closed）。 */
import { useState } from 'react'
import { Button, Card, Input, Select, Space, Table, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { ordersAdmin, ORDER_STATUS_LABELS, fmtCents, type OrderItem } from '../api/orders'

const STATUS_COLORS: Record<string, string> = {
  pending: 'orange',
  paid: 'blue',
  shipped: 'cyan',
  completed: 'green',
  closed: 'default',
}

const NEXT_ACTIONS: Record<string, { label: string; status: string }[]> = {
  pending: [{ label: '标记已付款', status: 'paid' }, { label: '关闭订单', status: 'closed' }],
  paid: [{ label: '标记已发货', status: 'shipped' }, { label: '关闭订单', status: 'closed' }],
  shipped: [{ label: '标记已完成', status: 'completed' }],
  completed: [],
  closed: [],
}

export default function Orders() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [statusFilter, setStatusFilter] = useState<string | undefined>()
  const [keyword, setKeyword] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['admin-orders', page, pageSize, statusFilter, keyword],
    queryFn: () => ordersAdmin.list({ page, page_size: pageSize, status: statusFilter, keyword: keyword || undefined }),
  })

  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => ordersAdmin.updateStatus(id, status),
    onSuccess: () => {
      message.success('订单状态已更新')
      qc.invalidateQueries({ queryKey: ['admin-orders'] })
    },
    onError: (e) => message.error(`操作失败：${(e as Error).message}`),
  })

  const columns: ColumnsType<OrderItem> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '订单号', dataIndex: 'order_no', width: 190 },
    {
      title: '商品',
      width: 240,
      render: (_, r) => (
        <div className="flex flex-col gap-1.5">
          {r.items.map((it) => (
            <div key={it.id} className="flex items-center gap-2 text-sm">
              {it.cover_url ? (
                <img
                  src={it.cover_url}
                  className="h-8 w-8 flex-shrink-0 rounded object-cover"
                  loading="lazy"
                  onError={(e) => {
                    ;(e.currentTarget as HTMLImageElement).style.opacity = '0.3'
                  }}
                />
              ) : (
                <div className="h-8 w-8 flex-shrink-0 rounded bg-gray-100" />
              )}
              <span className="truncate">{it.product_name} × {it.quantity}</span>
            </div>
          ))}
        </div>
      ),
    },
    {
      title: '收货人',
      width: 200,
      render: (_, r) => (
        <div className="text-sm">
          <div>{r.receiver_name} {r.receiver_phone}</div>
          <div className="truncate text-xs text-gray-400">{r.receiver_address}</div>
        </div>
      ),
    },
    {
      title: '金额',
      dataIndex: 'final_cents',
      width: 100,
      render: (c: number) => <span className="font-medium text-walnut">{fmtCents(c)}</span>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (s: string) => <Tag color={STATUS_COLORS[s]}>{ORDER_STATUS_LABELS[s] ?? s}</Tag>,
    },
    {
      title: '下单时间',
      dataIndex: 'created_date',
      width: 160,
      render: (d: string | null) => (d ? new Date(d).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' }) : '-'),
    },
    {
      title: '操作',
      width: 200,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          {(NEXT_ACTIONS[r.status] ?? []).map((act) => (
            <Button
              key={act.status}
              size="small"
              type={act.status === 'closed' ? 'default' : 'primary'}
              onClick={() => statusMut.mutate({ id: r.id, status: act.status })}
            >
              {act.label}
            </Button>
          ))}
          {!NEXT_ACTIONS[r.status]?.length && <span className="text-xs text-gray-400">终态</span>}
        </Space>
      ),
    },
  ]

  return (
    <Card
      title="订单列表"
      extra={
        <Space>
          <Input.Search placeholder="订单号/收货人/手机" allowClear onSearch={setKeyword} style={{ width: 220 }} />
          <Select
            placeholder="状态"
            allowClear
            style={{ width: 120 }}
            value={statusFilter}
            onChange={setStatusFilter}
            options={Object.entries(ORDER_STATUS_LABELS).map(([v, l]) => ({ value: v, label: l }))}
          />
        </Space>
      }
    >
      <Table<OrderItem>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items ?? []}
        columns={columns}
        scroll={{ x: 1300 }}
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