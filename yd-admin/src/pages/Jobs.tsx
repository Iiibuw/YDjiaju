/** 后台招聘管理：岗位列表 + 新建/编辑 + 删除 + 投递记录查看。 */
import { useState } from 'react'
import {
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Select,
  Space,
  Switch,
  Table,
  Tabs,
  Tag,
  message,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import {
  jobsAdmin,
  fmtSalary,
  STAGE_COLORS,
  STAGE_LABELS,
  type ApplicationItem,
  type JobCreatePayload,
  type JobItem,
} from '../api/jobs'

const CATEGORY_LABELS: Record<string, string> = { social: '社招', campus: '校招' }

interface FormValues {
  title: string
  category: 'social' | 'campus'
  department?: string
  location?: string
  salary_min_cents?: number
  salary_max_cents?: number
  headcount: number
  description?: string
  requirement?: string
  expire_date?: string
  is_activate: boolean
}

const empty: FormValues = {
  title: '',
  category: 'social',
  department: '',
  location: '',
  salary_min_cents: undefined,
  salary_max_cents: undefined,
  headcount: 1,
  description: '',
  requirement: '',
  expire_date: '',
  is_activate: true,
}

function JobsTab() {
  const qc = useQueryClient()
  const nav = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [keyword, setKeyword] = useState('')
  const [category, setCategory] = useState<string | undefined>()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<JobItem | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['admin-jobs', page, pageSize, keyword, category],
    queryFn: () =>
      jobsAdmin.list({ page, page_size: pageSize, keyword: keyword || undefined, category }),
  })

  const createMut = useMutation({
    mutationFn: (p: FormValues) => jobsAdmin.create(p as JobCreatePayload),
    onSuccess: () => {
      message.success('岗位已创建')
      setModalOpen(false)
      qc.invalidateQueries({ queryKey: ['admin-jobs'] })
    },
    onError: (e) => message.error(`创建失败：${(e as Error).message}`),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<FormValues> }) =>
      jobsAdmin.update(id, payload),
    onSuccess: () => {
      message.success('岗位已更新')
      setModalOpen(false)
      setEditing(null)
      qc.invalidateQueries({ queryKey: ['admin-jobs'] })
    },
    onError: (e) => message.error(`更新失败：${(e as Error).message}`),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => jobsAdmin.delete(id),
    onSuccess: () => {
      message.success('已删除')
      qc.invalidateQueries({ queryKey: ['admin-jobs'] })
    },
    onError: (e) => message.error(`删除失败：${(e as Error).message}`),
  })

  const columns: ColumnsType<JobItem> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    {
      title: '岗位',
      dataIndex: 'title',
      render: (t: string, r) => (
        <div>
          <div className="font-medium">{t}</div>
          <div className="text-xs text-gray-500">
            {[r.department, r.location].filter(Boolean).join(' · ')}
          </div>
        </div>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      width: 90,
      render: (c: string) => <Tag color={c === 'social' ? 'blue' : 'cyan'}>{CATEGORY_LABELS[c]}</Tag>,
    },
    {
      title: '薪资',
      width: 140,
      render: (_, r) => fmtSalary(r.salary_min_cents, r.salary_max_cents),
    },
    { title: '人数', dataIndex: 'headcount', width: 70 },
    {
      title: '截止',
      dataIndex: 'expire_date',
      width: 110,
      render: (d: string | null) => (d ? new Date(d).toLocaleDateString('zh-CN') : '长期'),
    },
    {
      title: '操作',
      width: 160,
      fixed: 'right',
      render: (_, r) => (
        <Space size="small">
          <Button size="small" type="link" onClick={() => { setEditing(r); setModalOpen(true) }}>编辑</Button>
          <Popconfirm title="确认删除该岗位？" onConfirm={() => deleteMut.mutate(r.id)}>
            <Button size="small" type="link" danger>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const formInitial = editing
    ? {
        title: editing.title,
        category: editing.category,
        department: editing.department ?? '',
        location: editing.location ?? '',
        salary_min_cents: editing.salary_min_cents ?? undefined,
        salary_max_cents: editing.salary_max_cents ?? undefined,
        headcount: editing.headcount,
        description: editing.description ?? '',
        requirement: editing.requirement ?? '',
        expire_date: editing.expire_date ? editing.expire_date.slice(0, 10) : '',
        is_activate: true,
      }
    : empty

  return (
    <>
      <Card
        title="岗位列表"
        extra={
          <Space>
            <Input.Search placeholder="搜索岗位" allowClear onSearch={setKeyword} style={{ width: 200 }} />
            <Select
              placeholder="分类"
              allowClear
              style={{ width: 120 }}
              value={category}
              onChange={setCategory}
              options={[
                { value: 'social', label: '社招' },
                { value: 'campus', label: '校招' },
              ]}
            />
            <Button type="primary" onClick={() => nav('/jobs/new')}>新建岗位</Button>
          </Space>
        }
      >
        <Table<JobItem>
          rowKey="id"
          loading={isLoading}
          dataSource={data?.items ?? []}
          columns={columns}
          scroll={{ x: 900 }}
          pagination={{ current: page, pageSize, total: data?.total, onChange: (p, ps) => { setPage(p); setPageSize(ps) } }}
        />
      </Card>

      <Modal
        open={modalOpen}
        title={editing ? '编辑岗位' : '新建岗位'}
        width={760}
        onCancel={() => { setModalOpen(false); setEditing(null) }}
        onOk={() => (document.getElementById('job-form-submit') as HTMLButtonElement | null)?.click()}
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
          <Row gutter={16}>
            <Col span={12}><Form.Item name="title" label="岗位名称" rules={[{ required: true, min: 2 }]}><Input /></Form.Item></Col>
            <Col span={12}>
              <Form.Item name="category" label="分类" rules={[{ required: true }]}>
                <Select options={[{ value: 'social', label: '社招' }, { value: 'campus', label: '校招' }]} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}><Form.Item name="department" label="部门"><Input /></Form.Item></Col>
            <Col span={12}><Form.Item name="location" label="工作地点"><Input /></Form.Item></Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="salary_min_cents" label="最低薪资（分）" tooltip="单位：分，1 元=100 分">
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="salary_max_cents" label="最高薪资（分）">
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={8}><Form.Item name="headcount" label="招聘人数"><InputNumber min={1} max={999} style={{ width: '100%' }} /></Form.Item></Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}><Form.Item name="expire_date" label="截止日期"><Input type="date" /></Form.Item></Col>
            <Col span={12}><Form.Item name="is_activate" label="激活" valuePropName="checked"><Switch /></Form.Item></Col>
          </Row>
          <Form.Item name="description" label="岗位职责（HTML）"><Input.TextArea rows={4} /></Form.Item>
          <Form.Item name="requirement" label="任职要求（HTML）"><Input.TextArea rows={4} /></Form.Item>
          <button id="job-form-submit" type="submit" style={{ display: 'none' }} />
        </Form>
      </Modal>
    </>
  )
}

function ApplicationsTab() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [stage, setStage] = useState<string | undefined>()

  const { data, isLoading } = useQuery({
    queryKey: ['admin-applications', page, pageSize, stage],
    queryFn: () => jobsAdmin.listApplications({ page, page_size: pageSize, stage }),
  })

  const columns: ColumnsType<ApplicationItem> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '岗位', dataIndex: 'job_title', width: 220, ellipsis: true },
    { title: '姓名', dataIndex: 'name', width: 100 },
    { title: '手机', dataIndex: 'phone', width: 130 },
    { title: '邮箱', dataIndex: 'email', width: 200, ellipsis: true },
    {
      title: '阶段',
      dataIndex: 'stage',
      width: 100,
      render: (s: ApplicationItem['stage']) => <Tag color={STAGE_COLORS[s]}>{STAGE_LABELS[s]}</Tag>,
    },
    {
      title: '投递时间',
      dataIndex: 'applied_date',
      width: 170,
      render: (d: string) => new Date(d).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' }),
    },
  ]

  return (
    <Card
      title="投递记录"
      extra={
        <Select
          placeholder="筛选阶段"
          allowClear
          style={{ width: 140 }}
          value={stage}
          onChange={setStage}
          options={Object.entries(STAGE_LABELS).map(([v, l]) => ({ value: v, label: l }))}
        />
      }
    >
      <Table<ApplicationItem>
        rowKey="id"
        loading={isLoading}
        dataSource={data?.items ?? []}
        columns={columns}
        scroll={{ x: 1000 }}
        pagination={{ current: page, pageSize, total: data?.total, onChange: (p, ps) => { setPage(p); setPageSize(ps) } }}
      />
    </Card>
  )
}

export default function JobsPage() {
  return (
    <Tabs
      defaultActiveKey="jobs"
      items={[
        { key: 'jobs', label: '岗位列表', children: <JobsTab /> },
        { key: 'apps', label: '投递记录', children: <ApplicationsTab /> },
      ]}
    />
  )
}