/** 后台会员管理：列表 + 搜索 + 启用/禁用 + 删除。 */
import { useState } from 'react'
import { Button, Card, Input, Popconfirm, Select, Space, Table, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { membersAdmin, type MemberItem } from '../api/members'

const genderLabel = (g: number | null) => (g === 1 ? '男' : g === 2 ? '女' : '-')

export default function Members() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-members', page, pageSize, keyword, statusFilter],
    queryFn: () =>
      membersAdmin.list({
        page,
        page_size: pageSize,
        keyword: keyword || undefined,
        is_activate: statusFilter,
      }),
  })

  const statusMut = useMutation({
    mutationFn: ({ id, is_activate }: { id: number; is_activate: boolean }) =>
      membersAdmin.updateStatus(id, is_activate),
    onSuccess: () => {
      message.success('状态已更新')
      qc.invalidateQueries({ queryKey: ['admin-members'] })
    },
    onError: (e) => message.error(`操作失败：${(e as Error).message}`),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => membersAdmin.delete(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-members'] })
    },
    onError: (e) => message.error(`删除失败：${(e as Error).message}`),
  })

  const columns: ColumnsType<MemberItem> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '手机号', dataIndex: 'phone', width: 140 },
    { title: '昵称', dataIndex: 'nickname', width: 120, render: (n: string | null) => n || '-' },
    { title: '邮箱', dataIndex: 'email', width: 200, ellipsis: true, render: (e: string | null) => e || '-' },
    { title: '性别', dataIndex: 'gender', width: 70, render: (g: number | null) => genderLabel(g) },
    {
      title: '状态',
      dataIndex: 'is_activate',
      width: 90,
      render: (v: number) => (v === 1 ? <Tag color="green">正常</Tag> : <Tag color="red">已禁用</Tag>),
    },
    {
      title: '注册时间',
      dataIndex: 'created_date',
      width: 160,
      render: (d: string | null) => (d ? new Date(d).toLocaleString('zh-CN', { dateStyle: 'short' }) : '-'),
    },
    {
      title: '操作',
      width: 180,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button
            size="small"
            type={r.is_activate === 1 ? 'default' : 'primary'}
            onClick={() => statusMut.mutate({ id: r.id, is_activate: r.is_activate !== 1 })}
          >
            {r.is_activate === 1 ? '禁用' : '启用'}
          </Button>
          <Popconfirm title="确认删除该会员？" onConfirm={() => deleteMut.mutate(r.id)}>
            <Button size="small" type="link" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Card
      title="会员列表"
      extra={
        <Space>
          <Input.Search placeholder="搜索手机号/昵称" allowClear onSearch={setKeyword} style={{ width: 220 }} />
          <Select
            placeholder="状态"
            allowClear
            style={{ width: 110 }}
            value={statusFilter}
            onChange={(v) => setStatusFilter(v)}
            options={[
              { value: true, label: '正常' },
              { value: false, label: '已禁用' },
            ]}
          />
        </Space>
      }
    >
      <Table<MemberItem>
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