/** 独立「新增案例」页：字段/校验/提交与列表弹窗一致；项目详情用完整富文本。 */
import { Button, Card, Form, Input, InputNumber, Select, Space, message } from 'antd'
import { ArrowLeftOutlined, PlusOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { casesAdmin, type CaseCreatePayload } from '../api/cases'
import RichTextEditor from '../components/RichTextEditor'

interface FormValues {
  title: string
  cover_url: string
  style?: string
  area?: string
  description?: string
  sort?: number
}

const empty: FormValues = {
  title: '',
  cover_url: '',
  style: '',
  area: '',
  description: '',
  sort: 0,
}

const STYLE_OPTIONS = [
  { value: '现代简约', label: '现代简约' },
  { value: '现代北欧', label: '现代北欧' },
  { value: '新中式', label: '新中式' },
  { value: '轻奢风', label: '轻奢风' },
  { value: '极简', label: '极简' },
  { value: '工业风', label: '工业风' },
]

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

export default function CaseNewPage() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const [form] = Form.useForm<FormValues>()

  const createMut = useMutation({
    mutationFn: (p: FormValues) => casesAdmin.create(p as CaseCreatePayload),
    onSuccess: () => {
      message.success('案例已创建')
      qc.invalidateQueries({ queryKey: ['admin-cases'] })
      nav('/cases')
    },
    onError: (e: any) => {
      message.error(`创建失败：${e?.response?.data?.message || (e as Error).message}`)
    },
  })

  return (
    <Card
      title={
        <Space>
          <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => nav('/cases')}>
            返回列表
          </Button>
          新建案例
        </Space>
      }
      extra={
        <Space>
          <Button onClick={() => nav('/cases')}>取消</Button>
          <Button type="primary" icon={<PlusOutlined />} loading={createMut.isPending} onClick={() => form.submit()}>
            保存
          </Button>
        </Space>
      }
    >
      <div className="mx-auto max-w-3xl">
        <Form<FormValues> form={form} layout="vertical" initialValues={empty} onFinish={(vals) => createMut.mutate(vals)}>
          <Form.Item name="title" label="案例标题" rules={[{ required: true, min: 2 }]}>
            <Input placeholder="如：胡桃禮·广州海珠湾花园别墅" />
          </Form.Item>
          <Form.Item name="cover_url" label="封面图 URL" rules={[{ required: true, type: 'url', message: '请输入 https:// 开头的图片链接' }]}>
            <Input placeholder="https://..." />
          </Form.Item>
          <div className="grid grid-cols-3 gap-4">
            <Form.Item name="style" label="风格">
              <Select allowClear placeholder="选择风格" options={STYLE_OPTIONS} />
            </Form.Item>
            <Form.Item name="area" label="面积">
              <Input placeholder="如 120㎡" />
            </Form.Item>
            <Form.Item name="sort" label="排序">
              <InputNumber min={0} max={999} style={{ width: '100%' }} />
            </Form.Item>
          </div>
          <Form.Item name="description" label="项目详情（HTML）">
            <RichField name="description" placeholder="项目详情，支持加粗、颜色、对齐、图片..." minHeight={300} />
          </Form.Item>
        </Form>
      </div>
    </Card>
  )
}