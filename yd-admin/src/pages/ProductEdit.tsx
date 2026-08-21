/** 独立「编辑产品」页：加载产品详情填充表单，保存后返回列表。 */
import { useState, useEffect } from 'react'
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Upload,
  message,
} from 'antd'
import { ArrowLeftOutlined, SaveOutlined, UploadOutlined, EyeOutlined } from '@ant-design/icons'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { productsAdmin, type ProductCreatePayload, type ProductStatus } from '../api/products'
import { uploadImage, validateImageUrl } from '../api/uploads'
import RichTextEditor from '../components/RichTextEditor'

interface FormValues {
  title: string
  subtitle?: string
  series?: string
  space?: string
  style?: string
  cover_url?: string
  description?: string
  min_price_cents?: number
  max_price_cents?: number
  status: ProductStatus
  sort_no?: number
}

const STATUS_OPTIONS: { value: ProductStatus; label: string }[] = [
  { value: 'draft', label: '草稿' },
  { value: 'on_sale', label: '上架' },
  { value: 'off_sale', label: '下架' },
]

const SPACE_OPTIONS = ['客厅', '餐厅', '卧室', '书房', '茶室', '办公'].map((v) => ({ value: v, label: v }))
const STYLE_OPTIONS = ['现代简约', '现代北欧', '新中式', '轻奢风', '极简', '工业风'].map((v) => ({ value: v, label: v }))

function CoverUrlField({ value, onChange }: { value?: string; onChange?: (v: string) => void }) {
  const [uploading, setUploading] = useState(false)

  const handleUpload = async (file: File) => {
    setUploading(true)
    try {
      const r = await uploadImage(file)
      onChange?.(r.url)
      message.success(`上传成功：${r.filename}`)
    } catch (e: any) {
      message.error(e?.response?.data?.message || '上传失败')
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
        <div className="inline-flex flex-col rounded border border-gray-200 bg-gray-50 p-2">
          <div className="mb-1 flex items-center gap-1 text-xs text-gray-500">
            <EyeOutlined /> 预览
          </div>
          <img
            src={value}
            alt="cover"
            className="max-h-20 max-w-32 rounded border border-gray-200 object-contain"
            onError={(e) => {
              ;(e.currentTarget as HTMLImageElement).style.display = 'none'
            }}
          />
        </div>
      )}
    </div>
  )
}

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

export default function ProductEditPage() {
  const nav = useNavigate()
  const { id } = useParams<{ id: string }>()
  const productId = Number(id)
  const qc = useQueryClient()
  const [form] = Form.useForm<FormValues>()

  const { data: item, isLoading } = useQuery({
    queryKey: ['admin-product-detail', productId],
    queryFn: () => productsAdmin.get(productId),
    enabled: !!productId,
  })

  const updateMut = useMutation({
    mutationFn: (payload: ProductCreatePayload) => productsAdmin.update(productId, payload),
    onSuccess: () => {
      message.success('产品已更新')
      qc.invalidateQueries({ queryKey: ['admin-products'] })
      qc.invalidateQueries({ queryKey: ['admin-product-detail', productId] })
      nav('/products')
    },
    onError: (e: any) => message.error(e?.response?.data?.message || '更新失败'),
  })

  // 数据加载后填充表单
  useEffect(() => {
    if (item) {
      form.setFieldsValue({
        title: item.title,
        subtitle: item.subtitle ?? '',
        series: item.series ?? '',
        space: item.space ?? '',
        style: item.style ?? '',
        cover_url: item.cover_url ?? '',
        description: item.description ?? '',
        min_price_cents: item.min_price_cents ?? undefined,
        max_price_cents: item.max_price_cents ?? undefined,
        status: item.status ?? 'draft',
        sort_no: item.sort ?? 0,
      })
    }
  }, [item, form])

  return (
    <Card
      title={
        <Space>
          <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => nav('/products')}>
            返回列表
          </Button>
          编辑产品 #{productId}
        </Space>
      }
      extra={
        <Space>
          <Button onClick={() => nav('/products')}>取消</Button>
          <Button type="primary" icon={<SaveOutlined />} loading={updateMut.isPending} onClick={() => form.submit()}>
            保存
          </Button>
        </Space>
      }
      loading={isLoading}
    >
      <div className="mx-auto max-w-3xl">
        <Form<FormValues>
          form={form}
          layout="vertical"
          onFinish={(vals) =>
            updateMut.mutate({
              title: vals.title,
              subtitle: vals.subtitle || null,
              series: vals.series || null,
              space: vals.space || null,
              style: vals.style || null,
              cover_url: vals.cover_url || null,
              description: vals.description || null,
              min_price_cents: vals.min_price_cents,
              max_price_cents: vals.max_price_cents,
              status: vals.status,
              sort: vals.sort_no || 0,
              is_activate: true,
            })
          }
        >
          <Form.Item name="title" label="产品标题" rules={[{ required: true, min: 2, max: 128 }]}>
            <Input placeholder="请输入产品标题" />
          </Form.Item>
          <Form.Item name="subtitle" label="副标题">
            <Input placeholder="可选" maxLength={255} />
          </Form.Item>
          <div className="grid grid-cols-3 gap-4">
            <Form.Item name="series" label="系列">
              <Input placeholder="如：云杉系列" />
            </Form.Item>
            <Form.Item name="space" label="空间">
              <Select options={SPACE_OPTIONS} allowClear />
            </Form.Item>
            <Form.Item name="style" label="风格">
              <Select options={STYLE_OPTIONS} allowClear />
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
                支持 https 网络链接，或点击「上传图片」选择本地 png/jpg/webp/gif
              </span>
            }
          >
            <CoverUrlField />
          </Form.Item>

          <Form.Item name="description" label="产品详情（HTML）">
            <RichField
              name="description"
              placeholder="产品详情，支持加粗、颜色、对齐、图片..."
              minHeight={320}
              mode="full"
            />
          </Form.Item>

          <div className="grid grid-cols-3 gap-4">
            <Form.Item name="min_price_cents" label="最低价（分）" tooltip="单位：分，1 元=100 分">
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="max_price_cents" label="最高价（分）">
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item name="status" label="状态" rules={[{ required: true }]}>
              <Select options={STATUS_OPTIONS} />
            </Form.Item>
          </div>
          <Form.Item name="sort_no" label="排序号（数值大者优先）">
            <InputNumber min={0} max={9999} />
          </Form.Item>
        </Form>
      </div>
    </Card>
  )
}