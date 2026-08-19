/** 后台预约管理：列表 + 状态跟进 + 删除。 */
import { useState } from 'react'
import { Button, Card, Input, Modal, Popconfirm, Select, Space, Table, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { appointmentsAdmin, APPT_STATUS_LABELS, type AppointmentItem } from '../api/orders'

const STATUS_COLORS: Record<string, string> = {
  pending: 'orange',
  following: 'blue',
  converted: 'green',
  invalid: 'default',
}

const TYPE_LABELS: Record<string, string> = {
  visit: '到店参观',
  consult: '方案咨询',
  custom: '定制服务',
  other: '其他',
}

export default function Appointments() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [statusFilter, setStatusFilter] = useState<string | undefined>()
  const [keyword, setKeyword] = useState('')
  const [followTarget, setFollowTarget] = useState<AppointmentItem | null>(null)
  const [followStatus, setFollowStatus] = useState('following')
  const [followNote, setFollowNote] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['admin-appointments', page, pageSize, statusFilter, keyword],
    queryFn: () => appointmentsAdmin.list({ page, page_size: pageSize, status: statusFilter, keyword: keyword || undefined }),
  })

  const followMut = useMutation({
    mutationFn: ({ id, status, note }: { id: number; status: string; note?: string }) =>
      appointmentsAdmin.updateStatus(id, status, note),
    onSuccess: () => {
      message.success('预约状态已更新')
      setFollowTarget(null)
      setFollowNote('')
      qc.invalidateQueries({ queryKey: ['admin-appointments'] })
    },
    onError: (e) => message.error(`操作失败：${(e as Error).message}`),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => appointmentsAdmin.delete(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-appointments'] })
    },
    onError: (e) => message.error(`删除失败：${(e as Error).message}`),
  })

  const columns: ColumnsType<AppointmentItem> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '类型', dataIndex: 'type', width: 90, render: (t: string) => TYPE_LABELS[t] ?? t },
    { title: '姓名', dataIndex: 'name', width: 90 },
    { title: '手机', dataIndex: 'phone', width: 130 },
    {
      title: '期望时间',
      dataIndex: 'preferred_date',
      width: 170,
      render: (d: string | null) => (d ? new Date(d).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' }) : '待确认'),
    },
    {
      title: '需求',
      dataIndex: 'message',
      width: 250,
      ellipsis: true,
      render: (m: string | null) => (
        <div>
          <div className="line-clamp-2">{m || '-'}</div>
          {followTarget?.id && (
            <div className="mt-1 text-xs text-green-600">跟进：{followTarget.follow_note}</div>
          )}
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (s: string) => <Tag color={STATUS_COLORS[s]}>{APPT_STATUS_LABELS[s] ?? s}</Tag>,
    },
    {
      title: '提交时间',
      dataIndex: 'created_date',
      width: 160,
      render: (d: string | null) => (d ? new Date(d).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' }) : '-'),
    },
    {
      title: '操作',
      width: 170,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button size="small" type="link" onClick={() => { setFollowTarget(r); setFollowStatus(r.status); setFollowNote(r.follow_note ?? '') }}>
            跟进
          </Button>
          <Popconfirm title="确认删除该预约？" onConfirm={() => deleteMut.mutate(r.id)}>
            <Button size="small" type="link" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Card
      title="预约列表"
      extra={
        <Space>
          <Input.Search placeholder="姓名/手机" allowClear onSearch={setKeyword} style={{ width: 200 }} />
          <Select
            placeholder="状态"
            allowClear
            style={{ width: 120 }}
            value={statusFilter}
            onChange={setStatusFilter}
            options={Object.entries(APPT_STATUS_LABELS).map(([v, l]) => ({ value: v, label: l }))}
          />
        </Space>
      }
    >
      <Table<AppointmentItem>
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

      <Modal
        open={!!followTarget}
        title={`跟进预约（${followTarget?.name ?? ''}）`}
        onCancel={() => setFollowTarget(null)}
        onOk={() => {
          if (followTarget) followMut.mutate({ id: followTarget.id, status: followStatus, note: followNote || undefined })
        }}
        confirmLoading={followMut.isPending}
      >
        <div className="mb-4 rounded-lg bg-gray-50 p-3 text-sm text-gray-700">
          {followTarget?.message || '（无需求描述）'}
        </div>
        <Select
          value={followStatus}
          onChange={setFollowStatus}
          style={{ width: '100%' }}
          options={Object.entries(APPT_STATUS_LABELS).map(([v, l]) => ({ value: v, label: l }))}
        />
        <Input.TextArea
          className="mt-3"
          rows={3}
          value={followNote}
          onChange={(e) => setFollowNote(e.target.value)}
          placeholder="跟进记录（选填）..."
        />
      </Modal>
    </Card>
  )
}