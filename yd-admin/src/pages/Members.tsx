/** 后台会员管理：列表 + 统计卡片 + 搜索 + 启用/禁用 + 编辑/查看/添加/删除。 */
import { useState } from 'react'
import {
  Avatar,
  Button,
  Card,
  Col,
  Descriptions,
  Form,
  Input,
  Modal,
  Popconfirm,
  Radio,
  Row,
  Select,
  Space,
  Statistic,
  Table,
  Tag,
  message,
} from 'antd'
import {
  EditOutlined,
  EyeOutlined,
  StopOutlined,
  CheckCircleOutlined,
  DeleteOutlined,
  PlusOutlined,
  UserOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { membersAdmin, type MemberItem } from '../api/members'

const genderLabel = (g: number | null) => (g === 1 ? '男' : g === 2 ? '女' : '未知')
const STATUS_ACTIVE = 1
const STATUS_DISABLED = 0

export default function Members() {
  const qc = useQueryClient()
  const nav = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>()

  const [editing, setEditing] = useState<MemberItem | null>(null)
  const [editOpen, setEditOpen] = useState(false)
  const [viewing, setViewing] = useState<MemberItem | null>(null)
  const [viewOpen, setViewOpen] = useState(false)
  const [addingOpen, setAddingOpen] = useState(false)
  const [editForm] = Form.useForm<{ nickname?: string; email?: string; gender?: number }>()
  const [addForm] = Form.useForm<{ phone: string; password: string; nickname?: string; email?: string }>()

  // ===== 数据查询 =====
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

  const { data: stats } = useQuery({
    queryKey: ['admin-members-stats'],
    queryFn: () => membersAdmin.stats(),
    staleTime: 30_000,
  })

  // ===== 变更操作 =====
  const statusMut = useMutation({
    mutationFn: ({ id, is_activate }: { id: number; is_activate: boolean }) =>
      membersAdmin.updateStatus(id, is_activate),
    onSuccess: () => {
      message.success('状态已更新')
      qc.invalidateQueries({ queryKey: ['admin-members'] })
      qc.invalidateQueries({ queryKey: ['admin-members-stats'] })
    },
    onError: (e) => message.error(`操作失败：${(e as Error).message}`),
  })

  const editMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: { nickname?: string | null; email?: string | null; gender?: number | null } }) =>
      membersAdmin.update(id, payload),
    onSuccess: () => {
      message.success('会员信息已更新')
      setEditOpen(false)
      setEditing(null)
      qc.invalidateQueries({ queryKey: ['admin-members'] })
    },
    onError: (e) => message.error(`更新失败：${(e as Error).message}`),
  })

  const addMut = useMutation({
    mutationFn: (p: { phone: string; password: string; nickname?: string | null; email?: string | null }) =>
      membersAdmin.create(p),
    onSuccess: () => {
      message.success('会员已创建')
      setAddingOpen(false)
      addForm.resetFields()
      qc.invalidateQueries({ queryKey: ['admin-members'] })
      qc.invalidateQueries({ queryKey: ['admin-members-stats'] })
    },
    onError: (e: any) => {
      const msg = e?.response?.data?.message || '创建失败'
      message.error(msg)
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => membersAdmin.delete(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-members'] })
      qc.invalidateQueries({ queryKey: ['admin-members-stats'] })
    },
    onError: (e) => message.error(`删除失败：${(e as Error).message}`),
  })

  // ===== 操作 handler =====
  const openEdit = (r: MemberItem) => {
    setEditing(r)
    editForm.setFieldsValue({
      nickname: r.nickname ?? '',
      email: r.email ?? '',
      gender: r.gender ?? 0,
    })
    setEditOpen(true)
  }

  const handleEdit = (vals: { nickname?: string; email?: string; gender?: number }) => {
    if (!editing) return
    editMut.mutate({
      id: editing.id,
      payload: {
        nickname: vals.nickname ?? null,
        email: vals.email ?? null,
        gender: vals.gender ?? 0,
      },
    })
  }

  const handleAdd = (vals: { phone: string; password: string; nickname?: string; email?: string }) => {
    addMut.mutate({
      phone: vals.phone,
      password: vals.password,
      nickname: vals.nickname ?? null,
      email: vals.email ?? null,
    })
  }

  const openView = (r: MemberItem) => {
    setViewing(r)
    setViewOpen(true)
  }

  // ===== 列表列 =====
  const columns: ColumnsType<MemberItem> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    {
      title: '头像/昵称',
      width: 180,
      render: (_, r) => (
        <div className="flex items-center gap-2">
          <Avatar
            size={32}
            icon={<UserOutlined />}
            src={r.avatar_url || undefined}
            style={{ backgroundColor: '#1677ff', flexShrink: 0 }}
          >
            {(r.nickname || r.phone).slice(0, 1)}
          </Avatar>
          <div className="leading-tight">
            <div className="text-sm font-medium">{r.nickname || <span className="text-gray-400">未设置</span>}</div>
            <div className="text-xs text-gray-400">#{r.id}</div>
          </div>
        </div>
      ),
    },
    { title: '手机号', dataIndex: 'phone', width: 130 },
    { title: '邮箱', dataIndex: 'email', width: 200, ellipsis: true, render: (e: string | null) => e || '-' },
    {
      title: '性别',
      dataIndex: 'gender',
      width: 70,
      render: (g: number | null) => genderLabel(g),
    },
    {
      title: '状态',
      dataIndex: 'is_activate',
      width: 90,
      render: (v: number) =>
        v === STATUS_ACTIVE ? <Tag color="success">正常</Tag> : <Tag>已禁用</Tag>,
    },
    {
      title: '注册时间',
      dataIndex: 'created_date',
      width: 160,
      render: (d: string | null) => (d ? new Date(d).toLocaleString('zh-CN', { dateStyle: 'short' }) : '-'),
    },
    {
      title: '操作',
      width: 340,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button size="small" type="link" icon={<EyeOutlined />} onClick={() => openView(r)}>
            查看
          </Button>
          <Button size="small" type="link" icon={<EditOutlined />} onClick={() => openEdit(r)} style={{ color: '#1677ff' }}>
            编辑
          </Button>
          {r.is_activate === STATUS_ACTIVE ? (
            <Popconfirm
              title="确认禁用该会员？"
              description="禁用后该会员将无法登录前台"
              okText="禁用"
              cancelText="取消"
              okButtonProps={{ danger: false, style: { background: '#fa8c16', borderColor: '#fa8c16' } }}
              onConfirm={() => statusMut.mutate({ id: r.id, is_activate: false })}
            >
              <Button size="small" type="link" icon={<StopOutlined />} style={{ color: '#fa8c16' }}>
                禁用
              </Button>
            </Popconfirm>
          ) : (
            <Popconfirm
              title="确认启用该会员？"
              okText="启用"
              cancelText="取消"
              onConfirm={() => statusMut.mutate({ id: r.id, is_activate: true })}
            >
              <Button size="small" type="link" icon={<CheckCircleOutlined />} style={{ color: '#52c41a' }}>
                启用
              </Button>
            </Popconfirm>
          )}
          <Popconfirm
            title="确认删除该会员？"
            description="删除后数据无法恢复"
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
            onConfirm={() => deleteMut.mutate(r.id)}
          >
            <Button size="small" type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="flex flex-col gap-4">
      {/* ===== 统计卡片 ===== */}
      <Row gutter={16}>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="会员总数"
              value={stats?.total ?? 0}
              prefix={<UserOutlined style={{ color: '#1677ff' }} />}
              valueStyle={{ color: '#1677ff', fontWeight: 600 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="今日新增"
              value={stats?.today_new ?? 0}
              prefix={<PlusOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a', fontWeight: 600 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card>
            <Statistic
              title="正常会员"
              value={data?.items?.filter((m) => m.is_activate === STATUS_ACTIVE).length ?? 0}
              prefix={<CheckCircleOutlined style={{ color: '#13c2c2' }} />}
              valueStyle={{ color: '#13c2c2', fontWeight: 600 }}
              suffix={<span className="text-xs text-gray-400 ml-1">/ 当前页</span>}
            />
          </Card>
        </Col>
      </Row>

      {/* ===== 列表 ===== */}
      <Card
        title="会员列表"
        extra={
          <Space wrap>
            <Input.Search
              placeholder="搜索手机号 / 昵称 / 邮箱"
              allowClear
              onSearch={setKeyword}
              style={{ width: 240 }}
            />
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
            <Button type="primary" icon={<PlusOutlined />} onClick={() => nav('/members/new')}>
              添加会员
            </Button>
          </Space>
        }
      >
        <Table<MemberItem>
          rowKey="id"
          loading={isLoading}
          dataSource={data?.items ?? []}
          columns={columns}
          scroll={{ x: 1200 }}
          rowClassName={(record, index) => {
            const base = record.is_activate === STATUS_DISABLED ? 'opacity-60' : ''
            // 斑马纹：奇数行浅灰
            const stripe = index % 2 === 0 ? 'member-row-stripe' : ''
            return [base, stripe].filter(Boolean).join(' ')
          }}
          pagination={{
            current: page,
            pageSize,
            total: data?.total,
            showSizeChanger: true,
            showQuickJumper: true,
            pageSizeOptions: ['10', '20', '50'],
            showTotal: (t) => `共 ${t} 条`,
            onChange: (p, ps) => {
              setPage(p)
              setPageSize(ps)
            },
          }}
        />
      </Card>

      {/* ===== 编辑会员 Modal ===== */}
      <Modal
        open={editOpen}
        title={`编辑会员：${editing?.nickname || editing?.phone}`}
        onCancel={() => {
          setEditOpen(false)
          setEditing(null)
        }}
        onOk={() => editForm.submit()}
        confirmLoading={editMut.isPending}
        destroyOnClose
      >
        <Form form={editForm} layout="vertical" onFinish={handleEdit}>
          <Form.Item label="手机号">
            <Input value={editing?.phone} disabled />
          </Form.Item>
          <Form.Item name="nickname" label="昵称" rules={[{ max: 64 }]}>
            <Input placeholder="会员昵称" />
          </Form.Item>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { type: 'email', message: '邮箱格式不正确' },
              { max: 128 },
            ]}
          >
            <Input placeholder="email@example.com" />
          </Form.Item>
          <Form.Item name="gender" label="性别">
            <Radio.Group>
              <Radio value={0}>未知</Radio>
              <Radio value={1}>男</Radio>
              <Radio value={2}>女</Radio>
            </Radio.Group>
          </Form.Item>
        </Form>
      </Modal>

      {/* ===== 查看详情 Modal ===== */}
      <Modal
        open={viewOpen}
        title="会员详情"
        onCancel={() => {
          setViewOpen(false)
          setViewing(null)
        }}
        footer={<Button onClick={() => setViewOpen(false)}>关闭</Button>}
        width={680}
      >
        {viewing && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="ID">#{viewing.id}</Descriptions.Item>
            <Descriptions.Item label="手机号">{viewing.phone}</Descriptions.Item>
            <Descriptions.Item label="昵称">{viewing.nickname || '-'}</Descriptions.Item>
            <Descriptions.Item label="邮箱">{viewing.email || '-'}</Descriptions.Item>
            <Descriptions.Item label="性别">{genderLabel(viewing.gender)}</Descriptions.Item>
            <Descriptions.Item label="状态">
              {viewing.is_activate === STATUS_ACTIVE ? (
                <Tag color="success">正常</Tag>
              ) : (
                <Tag>已禁用</Tag>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="注册时间">
              {viewing.created_date ? new Date(viewing.created_date).toLocaleString('zh-CN') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="最近登录">
              {viewing.last_login_date ? new Date(viewing.last_login_date).toLocaleString('zh-CN') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="头像">
              {viewing.avatar_url ? (
                <img src={viewing.avatar_url} alt="" className="h-12 w-12 rounded object-cover" />
              ) : (
                '无'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="关联订单/预约">
              <span className="text-gray-400">
                前往「订单管理」/「预约管理」按手机号 <b>{viewing.phone}</b> 查询
              </span>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      {/* ===== 添加会员 Modal ===== */}
      <Modal
        open={addingOpen}
        title="添加会员"
        onCancel={() => {
          setAddingOpen(false)
          addForm.resetFields()
        }}
        onOk={() => addForm.submit()}
        confirmLoading={addMut.isPending}
        destroyOnClose
      >
        <Form form={addForm} layout="vertical" onFinish={handleAdd}>
          <Form.Item
            name="phone"
            label="手机号"
            rules={[
              { required: true, message: '请输入手机号' },
              { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的 11 位手机号' },
            ]}
          >
            <Input placeholder="11 位手机号" maxLength={11} />
          </Form.Item>
          <Form.Item
            name="password"
            label="初始密码"
            rules={[
              { required: true, message: '请输入初始密码' },
              { min: 6, message: '密码至少 6 位' },
            ]}
          >
            <Input.Password placeholder="≥6 位" />
          </Form.Item>
          <Form.Item name="nickname" label="昵称">
            <Input placeholder="选填" maxLength={64} />
          </Form.Item>
          <Form.Item name="email" label="邮箱" rules={[{ type: 'email', message: '邮箱格式不正确' }]}>
            <Input placeholder="选填" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}