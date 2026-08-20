/** 独立「新增资讯」页：字段/校验/提交与列表页弹窗完全一致，保存后返回列表。 */
import { useState } from 'react'
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Switch,
  Upload,
  message,
} from 'antd'
import { ArrowLeftOutlined, PlusOutlined, UploadOutlined, EyeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { newsAdmin, type NewsCreatePayload } from '../api/news'
import { uploadImage, validateImageUrl } from '../api/uploads'
import RichTextEditor from '../components/RichTextEditor'

interface FormValues {
  title: string
  subtitle?: string
  category: 'company' | 'industry'
  cover_url?: string
  summary?: string
  content: string
  author?: string
  source?: string
  is_published: boolean
  is_top: boolean
  is_recommend: boolean
  sort?: number
}

const empty: FormValues = {
  title: '',
  subtitle: '',
  category: 'company',
  cover_url: '',
  summary: '',
  content: '',
  author: '',
  source: '',
  is_published: false,
  is_top: false,
  is_recommend: false,
  sort: 0,
}

/** 封面 URL 复合输入：手动 + 上传 + 预览 */
function CoverUrlField({ value, onChange }: { value?: string; onChange?: (v: string) => void }) {
  const [uploading, setUploading] = useState(false)

  const handleUpload = async (file: File) => {
    setUploading(true)
    try {
      const r = await uploadImage(file)
      onChange?.(r.url)
      message.success(`上传成功：${r.filename}`)
    } catch (e: any) {
      message.error(e?.response?.data?.message || e?.response?.data?.detail?.[0]?.msg || '上传失败')
    } finally {
      setUploading(false)
    }
    return false
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex gap-2">
        <Input
          value={value ?? ''}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder="https://..."
          maxLength={500}
          allowClear
          className="flex-1"
        />
        <Upload
          accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
          showUploadList={false}
          beforeUpload={handleUpload}
          disabled={uploading}
        >
          <Button icon={<UploadOutlined />} loading={uploading}>
            上传图片
          </Button>
        </Upload>
      </div>
      {value && /^https?:\/\//i.test(value) && (
        <div className="rounded border border-gray-200 bg-gray-50 p-2">
          <div className="mb-1 flex items-center gap-1 text-xs text-gray-500">
            <EyeOutlined /> 预览
          </div>
          <img
            src={value}
            alt="cover"
            className="max-h-32 max-w-xs rounded border border-gray-200 object-contain"
            onError={(e) => {
              ;(e.currentTarget as HTMLImageElement).style.display = 'none'
            }}
          />
        </div>
      )}
    </div>
  )
}

/** 富文本字段 wrapper */
function RichField({ name, placeholder, minHeight, mode }: { name: keyof FormValues; placeholder?: string; minHeight?: number; mode?: 'simple' | 'full' }) {
  const f = Form.useFormInstance<FormValues>()
  const v = (f.getFieldValue(name as never) as string | undefined) ?? ''
  return (
    <RichTextEditor
      value={v}
      onChange={(html) => f.setFieldValue(name as never, html as never)}
      placeholder={placeholder}
      minHeight={minHeight}
      mode={mode}
    />
  )
}

export default function NewsNewPage() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const [form] = Form.useForm<FormValues>()

  const createMut = useMutation({
    mutationFn: (p: FormValues) =>
      newsAdmin.create({
        ...p,
        cover_url: p.cover_url || null,
        summary: p.summary || null,
        subtitle: p.subtitle || null,
        author: p.author || null,
        source: p.source || null,
      } as NewsCreatePayload),
    onSuccess: () => {
      message.success('资讯已创建')
      qc.invalidateQueries({ queryKey: ['admin-news'] })
      nav('/news')
    },
    onError: (e: any) => {
      message.error(`创建失败：${e?.response?.data?.message || (e as Error).message}`)
    },
  })

  const handleSubmit = (vals: FormValues) => createMut.mutate(vals)

  return (
    <Card
      title={
        <Space>
          <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => nav('/news')}>
            返回列表
          </Button>
          新建资讯
        </Space>
      }
      extra={
        <Space>
          <Button onClick={() => nav('/news')}>取消</Button>
          <Button type="primary" icon={<PlusOutlined />} loading={createMut.isPending} onClick={() => form.submit()}>
            保存
          </Button>
        </Space>
      }
    >
      <div className="mx-auto max-w-3xl">
        <Form<FormValues>
          form={form}
          layout="vertical"
          initialValues={empty}
          onFinish={handleSubmit}
        >
          <Form.Item name="title" label="标题" rules={[{ required: true, min: 2, max: 128 }]}>
            <Input placeholder="请输入标题（2-128 字）" />
          </Form.Item>
          <Form.Item name="subtitle" label="副标题">
            <Input placeholder="可选" maxLength={255} />
          </Form.Item>
          <div className="grid grid-cols-2 gap-4">
            <Form.Item name="category" label="分类" rules={[{ required: true }]}>
              <Select
                options={[
                  { value: 'company', label: '企业新闻' },
                  { value: 'industry', label: '行业资讯' },
                ]}
              />
            </Form.Item>
          </div>

          <Form.Item
            name="cover_url"
            label="封面图"
            rules={[
              {
                validator: (_, v) => {
                  const msg = validateImageUrl(v)
                  return msg ? Promise.reject(new Error(msg)) : Promise.resolve()
                },
              },
            ]}
            extra={
              <span className="text-xs text-gray-500">
                支持 https 网络链接，或点击「上传图片」选择本地 png/jpg/webp/gif（≤5MB）
              </span>
            }
          >
            <CoverUrlField />
          </Form.Item>

          <Form.Item name="summary" label="摘要">
            <RichField name="summary" placeholder="一句话摘要（简易富文本）" minHeight={100} mode="simple" />
          </Form.Item>
          <Form.Item name="content" label="正文（HTML）" rules={[{ required: true, min: 1 }]}>
            <RichField name="content" placeholder="请输入正文内容，支持加粗、颜色、对齐、图片上传..." minHeight={320} mode="full" />
          </Form.Item>
          <div className="grid grid-cols-2 gap-4">
            <Form.Item name="author" label="作者">
              <Input />
            </Form.Item>
            <Form.Item name="source" label="来源">
              <Input />
            </Form.Item>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <Form.Item name="is_published" label="发布" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item name="is_top" label="置顶" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item name="is_recommend" label="推荐" valuePropName="checked">
              <Switch />
            </Form.Item>
          </div>
          <Form.Item name="sort" label="排序（数值大者优先）">
            <InputNumber min={0} max={9999} />
          </Form.Item>
        </Form>
      </div>
    </Card>
  )
}