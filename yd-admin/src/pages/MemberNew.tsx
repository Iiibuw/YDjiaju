/** 独立「添加会员」页：手机号+初始密码+昵称+邮箱。 */
import { Button, Card, Form, Input, Space, message } from 'antd'
import { ArrowLeftOutlined, PlusOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { membersAdmin } from '../api/members'

interface FormValues {
  phone: string
  password: string
  nickname?: string
  email?: string
}

export default function MemberNewPage() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const [form] = Form.useForm<FormValues>()

  const addMut = useMutation({
    mutationFn: (p: FormValues) =>
      membersAdmin.create({
        phone: p.phone,
        password: p.password,
        nickname: p.nickname ?? null,
        email: p.email ?? null,
      }),
    onSuccess: () => {
      message.success('会员已创建')
      qc.invalidateQueries({ queryKey: ['admin-members'] })
      qc.invalidateQueries({ queryKey: ['admin-members-stats'] })
      nav('/members')
    },
    onError: (e: any) => {
      message.error(e?.response?.data?.message || '创建失败')
    },
  })

  return (
    <Card
      title={
        <Space>
          <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => nav('/members')}>
            返回列表
          </Button>
          添加会员
        </Space>
      }
      extra={
        <Space>
          <Button onClick={() => nav('/members')}>取消</Button>
          <Button type="primary" icon={<PlusOutlined />} loading={addMut.isPending} onClick={() => form.submit()}>
            保存
          </Button>
        </Space>
      }
    >
      <div className="mx-auto max-w-lg">
        <Form<FormValues>
          form={form}
          layout="vertical"
          onFinish={(vals) => addMut.mutate(vals)}
          initialValues={{ phone: '', password: '', nickname: '', email: '' }}
        >
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
      </div>
    </Card>
  )
}