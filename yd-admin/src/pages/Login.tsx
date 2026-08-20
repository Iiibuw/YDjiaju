/** 后台登录页：调用真实后端 /api/v1/auth/*，登录成功时把 token 持久化到 localStorage。 */
import { useEffect, useState } from 'react'
import { Alert, Button, Card, Form, Input, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'

import { getCaptcha, login } from '../api/auth'
import { setToken } from '../api/http'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const [captcha, setCaptcha] = useState<Awaited<ReturnType<typeof getCaptcha>> | null>(null)
  const [captchaError, setCaptchaError] = useState<string | null>(null)
  const [loginError, setLoginError] = useState<string | null>(null)
  const nav = useNavigate()

  async function refreshCaptcha() {
    setCaptchaError(null)
    try {
      const c = await getCaptcha()
      setCaptcha(c)
    } catch (e: any) {
      setCaptcha(null)
      setCaptchaError(
        `验证码加载失败：${e?.message ?? '网络错误'}。请确认后端服务已启动（8000 端口）且未被代理拦截。`,
      )
    }
  }

  // 进入登录页自动加载验证码
  useEffect(() => {
    refreshCaptcha()
  }, [])

  async function onFinish(values: { username: string; password: string; captcha: string }) {
    setLoginError(null)
    if (!captcha) {
      setLoginError('验证码尚未加载成功，请先点击上方重试')
      return
    }
    setLoading(true)
    try {
      const data = await login({
        username: values.username,
        password: values.password,
        captcha_id: captcha.captcha_id,
        captcha_code: values.captcha.toUpperCase(),
      })
      setToken(data.access_token)
      nav('/depts')
    } catch (e: any) {
      setLoginError(e?.message ?? '登录失败，请重试')
      refreshCaptcha() // 验证码一次性，失败后换新
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
      <Card style={{ width: 440 }} title="YD 后台管理系统">
        <Typography.Paragraph type="secondary">
          演示账号：<b>admin / admin123</b> · 验证码以图片为准（Dev 模式可填 ABCD）
        </Typography.Paragraph>

        {captchaError && (
          <Alert
            type="error"
            showIcon
            message="验证码加载失败"
            description={captchaError}
            action={
              <Button size="small" onClick={refreshCaptcha}>
                重试
              </Button>
            }
            style={{ marginBottom: 16 }}
          />
        )}

        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item label="账号" name="username" rules={[{ required: true }]}>
            <Input placeholder="admin" autoComplete="username" />
          </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true, min: 6 }]}>
            <Input.Password placeholder="admin123" autoComplete="current-password" />
          </Form.Item>
          <Form.Item label="图形验证码" name="captcha" rules={[{ required: true, len: 4 }]}>
            <Input
              placeholder="4 位字符"
              maxLength={4}
              disabled={!captcha}
              style={{ textTransform: 'uppercase' }}
            />
          </Form.Item>
          <div className="mb-3">
            {captcha ? (
              <img
                src={captcha.captcha_image}
                alt="captcha"
                onClick={refreshCaptcha}
                style={{ height: 40, cursor: 'pointer', border: '1px solid #d9d9d9' }}
              />
            ) : (
              <span className="text-gray-400">验证码图片加载中...</span>
            )}
            <Typography.Text type="secondary" style={{ marginLeft: 12 }}>
              点击图片刷新
            </Typography.Text>
          </div>

          {loginError && (
            <Alert
              type="error"
              showIcon
              message="登录失败"
              description={loginError}
              style={{ marginBottom: 16 }}
            />
          )}

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
