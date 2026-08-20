/** 独立「新增岗位」页：字段/校验/提交与列表弹窗一致；岗位职责/任职要求用完整富文本。 */
import { Button, Card, Col, Form, Input, InputNumber, Row, Select, Space, Switch, message } from 'antd'
import { ArrowLeftOutlined, PlusOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { jobsAdmin, type JobCreatePayload } from '../api/jobs'
import RichTextEditor from '../components/RichTextEditor'

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

function RichField({ name, placeholder, minHeight }: { name: keyof FormValues; placeholder?: string; minHeight?: number }) {
  const f = Form.useFormInstance<FormValues>()
  const v = (f.getFieldValue(name as never) as string | undefined) ?? ''
  return (
    <RichTextEditor
      value={v}
      onChange={(html) => f.setFieldValue(name as never, html as never)}
      placeholder={placeholder}
      minHeight={minHeight}
      mode="full"
    />
  )
}

export default function JobNewPage() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const [form] = Form.useForm<FormValues>()

  const createMut = useMutation({
    mutationFn: (p: FormValues) => jobsAdmin.create(p as JobCreatePayload),
    onSuccess: () => {
      message.success('岗位已创建')
      qc.invalidateQueries({ queryKey: ['admin-jobs'] })
      nav('/jobs')
    },
    onError: (e: any) => {
      message.error(`创建失败：${e?.response?.data?.message || (e as Error).message}`)
    },
  })

  return (
    <Card
      title={
        <Space>
          <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => nav('/jobs')}>
            返回列表
          </Button>
          新建岗位
        </Space>
      }
      extra={
        <Space>
          <Button onClick={() => nav('/jobs')}>取消</Button>
          <Button type="primary" icon={<PlusOutlined />} loading={createMut.isPending} onClick={() => form.submit()}>
            保存
          </Button>
        </Space>
      }
    >
      <div className="mx-auto max-w-3xl">
        <Form<FormValues> form={form} layout="vertical" initialValues={empty} onFinish={(vals) => createMut.mutate(vals)}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="title" label="岗位名称" rules={[{ required: true, min: 2 }]}>
                <Input placeholder="如：家具设计师" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="category" label="分类" rules={[{ required: true }]}>
                <Select options={[{ value: 'social', label: '社招' }, { value: 'campus', label: '校招' }]} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="department" label="部门">
                <Input placeholder="如：设计中心" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="location" label="工作地点">
                <Input placeholder="如：广东佛山" />
              </Form.Item>
            </Col>
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
            <Col span={8}>
              <Form.Item name="headcount" label="招聘人数">
                <InputNumber min={1} max={999} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="expire_date" label="截止日期">
                <Input type="date" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="is_activate" label="激活" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="岗位职责（HTML）">
            <RichField name="description" placeholder="岗位职责，支持加粗、颜色、对齐、图片..." minHeight={220} />
          </Form.Item>
          <Form.Item name="requirement" label="任职要求（HTML）">
            <RichField name="requirement" placeholder="任职要求，支持加粗、颜色、对齐、图片..." minHeight={220} />
          </Form.Item>
        </Form>
      </div>
    </Card>
  )
}