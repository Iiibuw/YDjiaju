/** 后台登录页：调用真实后端 /api/v1/auth/*，登录成功时把 token 持久化到 localStorage。 */
import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'

import { getCaptcha, login } from '../api/auth'
import { setToken } from '../api/http'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const [captcha, setCaptcha] = useState<Awaited<ReturnType<typeof getCaptcha>> | null>(null)
  const nav = useNavigate()

  async function refreshCaptcha() {
    try {
      const c = await getCaptcha()
      setCaptcha(c)
    } catch (e: any) {
      message.error(e?.message ?? '验证码加载失败，请点击图片重试')
    }
  }

  // 进入登录页自动加载验证码——避免用户必须先点「加载验证码」按钮才能看到表单
  useEffect(() => {
    refreshCaptcha()
  }, [])

  async function onFinish(values: { username: string; password: string; captcha: string }) {
    if (!captcha) return
    setLoading(true)
    try {
      const data = await login({
        username: values.username,
        password: values.password,
        captcha_id: captcha.captcha_id,
        captcha_code: values.captcha.toUpperCase(),
      })
      // 关键修复：把 token 持久化到 localStorage('yd_admin_token')，否则后续所有 API 都会 401
      setToken(data.access_token)
      message.success('登录成功')
      nav('/depts')
    } catch (e: any) {
      message.error(e?.message ?? '登录失败')
      refreshCaptcha()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        background: 'linear-gradient(135deg, #f0f5ff 0%, #fafafa 100%)',
      }}
    >
      <Card style={{ width: 420 }} title="YD 后台管理系统">
        <Typography.Paragraph type="secondary">
          演示账号：<b>admin / admin123</b> · 验证码以图片为准
        </Typography.Paragraph>

        {!captcha && (
          <Button type="link" onClick={refreshCaptcha}>
            加载验证码
          </Button>
        )}
        {captcha && (
          <Form layout="vertical" onFinish={onFinish}>
            <Form.Item label="账号" name="username" rules={[{ required: true }]}>
              <Input placeholder="admin" autoComplete="username" />
            </Form.Item>
            <Form.Item label="密码" name="password" rules={[{ required: true, min: 6 }]}>
              <Input.Password placeholder="admin123" autoComplete="current-password" />
            </Form.Item>
            <Form.Item label="图形验证码" name="captcha" rules={[{ required: true, len: 4 }]}>
              <Input placeholder="4 位字符" maxLength={4} style={{ textTransform: 'uppercase' }} />
            </Form.Item>
            <div className="mb-3">
              <img
                src={captcha.captcha_image}
                alt="captcha"
                onClick={refreshCaptcha}
                style={{ height: 40, cursor: 'pointer', border: '1px solid #d9d9d9' }}
              />
              <Typography.Text type="secondary" style={{ marginLeft: 12 }}>
                点击图片刷新
              </Typography.Text>
            </div>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block>
                登录
              </Button>
            </Form.Item>
          </Form>
        )}
      </Card>
    </div>
  )
}
