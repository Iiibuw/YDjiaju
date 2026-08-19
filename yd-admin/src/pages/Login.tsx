import { Card, Typography } from 'antd'

/**
 * 后台登录页（M0 占位）
 * M1 待办：
 *  1. 拉取 GET /api/v1/auth/captcha → 显示图形验证码
 *  2. 表单 → POST /api/v1/auth/login → 存 token 到 localStorage
 *  3. 成功后跳转 /dashboard
 */
export default function Login() {
  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        background: 'linear-gradient(135deg, #f0f5ff 0%, #fafafa 100%)',
      }}
    >
      <Card style={{ width: 400 }} title="YD 后台管理系统">
        <Typography.Title level={4}>✅ M0 后台骨架已就绪</Typography.Title>
        <Typography.Paragraph>
          M1 待办：接入 <code>POST /api/v1/auth/login</code> + 图形验证码 + 角色权限。
        </Typography.Paragraph>
      </Card>
    </div>
  )
}
