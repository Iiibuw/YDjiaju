/** 后台留言管理：列表 + 状态筛选 + 回复 Modal + 删除。 */
import { useState } from 'react'
import { Button, Card, Input, Modal, Popconfirm, Select, Space, Table, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { messagesAdmin, type MessageItem } from '../api/messages'

const STATUS_LABELS: Record<MessageItem['status'], { label: string; color: string }> = {
  pending: { label: '待回复', color: 'orange' },
  replied: { label: '已回复', color: 'green' },
  archived: { label: '已归档', color: 'default' },
}

export default function Messages() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [statusFilter, setStatusFilter] = useState<string | undefined>()
  const [replyTarget, setReplyTarget] = useState<MessageItem | null>(null)
  const [replyText, setReplyText] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['admin-messages', page, pageSize, statusFilter],
    queryFn: () => messagesAdmin.list({ page, page_size: pageSize, status: statusFilter }),
  })

  const replyMut = useMutation({
    mutationFn: ({ id, content }: { id: number; content: string }) => messagesAdmin.reply(id, content),
    onSuccess: () => {
      message.success('回复成功')
      setReplyTarget(null)
      setReplyText('')
      qc.invalidateQueries({ queryKey: ['admin-messages'] })
    },
    onError: (e) => message.error(`回复失败：${(e as Error).message}`),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => messagesAdmin.delete(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-messages'] })
    },
    onError: (e) => message.error(`删除失败：${(e as Error).message}`),
  })

  const columns: ColumnsType<MessageItem> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '称呼', dataIndex: 'name', width: 100 },
    { title: '电话', dataIndex: 'phone', width: 130, render: (p: string | null) => p || '-' },
    {
      title: '留言内容',
      dataIndex: 'content',
      width: 320,
      ellipsis: true,
      render: (c: string, r) => (
        <div>
          <div className="line-clamp-2">{c}</div>
          {r.reply_content && (
            <div className="mt-1 rounded bg-green-50 px-2 py-1 text-xs text-green-700">
              回复：{r.reply_content}
            </div>
          )}
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (s: MessageItem['status']) => {
        const m = STATUS_LABELS[s] ?? STATUS_LABELS.pending
        return <Tag color={m.color}>{m.label}</Tag>
      },
    },
    {
      title: '提交时间',
      dataIndex: 'created_date',
      width: 160,
      render: (d: string | null) => (d ? new Date(d).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' }) : '-'),
    },
    {
      title: '操作',
      width: 160,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button
            size="small"
            type="link"
            onClick={() => {
              setReplyTarget(r)
              setReplyText(r.reply_content ?? '')
            }}
          >
            {r.status === 'replied' ? '修改回复' : '回复'}
          </Button>
          <Popconfirm title="确认删除该留言？" onConfirm={() => deleteMut.mutate(r.id)}>
            <Button size="small" type="link" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Card
      title="留言列表"
      extra={
        <Select
          placeholder="状态筛选"
          allowClear
          style={{ width: 120 }}
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { value: 'pending', label: '待回复' },
            { value: 'replied', label: '已回复' },
            { value: 'archived', label: '已归档' },
          ]}
        />
      }
    >
      <Table<MessageItem>
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

      <Modal
        open={!!replyTarget}
        title={`回复留言（${replyTarget?.name ?? ''}）`}
        onCancel={() => {
          setReplyTarget(null)
          setReplyText('')
        }}
        onOk={() => {
          if (replyTarget && replyText.trim()) {
            replyMut.mutate({ id: replyTarget.id, content: replyText.trim() })
          } else {
            message.warning('请输入回复内容')
          }
        }}
        confirmLoading={replyMut.isPending}
      >
        <div className="mb-4 rounded-lg bg-gray-50 p-3 text-sm text-gray-700">
          {replyTarget?.content}
        </div>
        <Input.TextArea
          rows={4}
          value={replyText}
          onChange={(e) => setReplyText(e.target.value)}
          placeholder="输入回复内容..."
        />
      </Modal>
    </Card>
  )
}