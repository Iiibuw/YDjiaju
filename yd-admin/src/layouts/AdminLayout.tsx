/** 后台管理布局：左侧菜单 + 顶部栏 + 内容区 + 底部用户信息区。 */
import { useEffect, useState } from 'react'
import {
  Layout,
  Menu,
  Avatar,
  Button,
  Modal,
  Form,
  Input,
  message,
} from 'antd'
import {
  UserOutlined,
  KeyOutlined,
  LogoutOutlined,
  SwapOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'

import { setToken } from '../api/http'
import { changePassword, fetchProfile, getCaptcha, login, type AdminProfile } from '../api/auth'

const { Sider, Header, Content } = Layout

/** 品牌标题：仅文字（无图标） */
const MENU = [
  { key: '/dashboard', label: '仪表盘' },
  { key: '/products', label: '产品管理' },
  { key: '/categories', label: '分类管理' },
  { key: '/news', label: '资讯管理' },
  { key: '/jobs', label: '招聘管理' },
  { key: '/cases', label: '案例管理' },
  { key: '/orders', label: '订单管理' },
  { key: '/appointments', label: '预约管理' },
  { key: '/members', label: '会员管理' },
  { key: '/messages', label: '留言管理' },
  { key: '/depts', label: '部门管理' },
]

export default function AdminLayout() {
  const nav = useNavigate()
  const loc = useLocation()
  const [profile, setProfile] = useState<AdminProfile | null>(null)
  const [pwdOpen, setPwdOpen] = useState(false)
  const [switchOpen, setSwitchOpen] = useState(false)
  const [pwdForm] = Form.useForm<{ old_password: string; new_password: string; confirm: string }>()
  const [switchForm] = Form.useForm<{ username: string; password: string; captcha_code: string }>()
  const [switchCaptchaId, setSwitchCaptchaId] = useState('')
  const [switchCaptchaImg, setSwitchCaptchaImg] = useState('')
  const [switchLoading, setSwitchLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    fetchProfile()
      .then((p) => mounted && setProfile(p))
      .catch(() =>
        mounted &&
        setProfile({
          id: 0,
          username: 'admin',
          real_name: '管理员',
          nickname: null,
          avatar_url: null,
          email: null,
          role: 'admin',
          dept_name: null,
          data_scope: 'ALL',
        }),
      )
    return () => {
      mounted = false
    }
  }, [])

  const handleLogout = () => {
    Modal.confirm({
      title: '确认退出登录?',
      content: '退出后需要重新登录。',
      okText: '退出',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: () => {
        setToken(null)
        nav('/login', { replace: true })
      },
    })
  }

  const handleChangePwd = async (vals: { old_password: string; new_password: string }) => {
    try {
      await changePassword(vals)
      message.success('密码修改成功')
      setPwdOpen(false)
      pwdForm.resetFields()
    } catch (e: any) {
      message.error(e?.response?.data?.detail?.[0]?.msg || e?.response?.data?.message || '密码修改失败')
    }
  }

  const refreshSwitchCaptcha = async () => {
    try {
      const cap = await getCaptcha()
      setSwitchCaptchaId(cap.captcha_id)
      setSwitchCaptchaImg(cap.captcha_image)
      switchForm.setFieldValue('captcha_code', '')
    } catch {
      message.error('验证码加载失败')
    }
  }

  const handleSwitch = async (vals: { username: string; password: string; captcha_code: string }) => {
    setSwitchLoading(true)
    try {
      const r = await login({
        username: vals.username,
        password: vals.password,
        captcha_id: switchCaptchaId,
        captcha_code: vals.captcha_code,
      })
      setToken(r.access_token)
      message.success(`已切换到 ${r.real_name || vals.username}`)
      setSwitchOpen(false)
      switchForm.resetFields()
      // 重新拉取新身份
      const p = await fetchProfile()
      setProfile(p)
    } catch (e: any) {
      message.error(e?.response?.data?.message || '切换失败,请检查账号密码')
      refreshSwitchCaptcha()
    } finally {
      setSwitchLoading(false)
    }
  }

  useEffect(() => {
    if (switchOpen) refreshSwitchCaptcha()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [switchOpen])

  const displayName = profile?.real_name || profile?.username || '管理员'

  return (
    <Layout className="min-h-screen">
      <Sider
        width={220}
        theme="dark"
        style={{ backgroundColor: '#001529', height: '100vh', position: 'sticky', top: 0, overflow: 'hidden' }}
      >
        {/* ===== 侧边栏弹性容器：flex column 占满整高，用户区固定在底部 ===== */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
          }}
        >
        {/* Logo 区域：图标 + 品牌名 + 副标题 */}
        {/* ===== 品牌标题：仅文字，浅米白，无图标 ===== */}
        <div
          className="flex h-12 items-center border-b px-4"
          style={{ borderColor: 'rgba(255,255,255,0.08)' }}
        >
          <div className="flex flex-col leading-none">
            <span className="text-[13px] font-semibold tracking-wide" style={{ color: '#f5f0e6' }}>
              YD 家具
            </span>
            <span className="mt-0.5 text-[9px]" style={{ color: 'rgba(255,255,255,0.5)' }}>
              Admin Console
            </span>
          </div>
        </div>

        {/* ===== 菜单容器：flex:1 + overflow-y:auto（菜单过多时内部滚动） ===== */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '6px 0' }}>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[loc.pathname]}
            items={MENU.map((m) => ({
              key: m.key,
              label: <Link to={m.key}>{m.label}</Link>,
            }))}
            style={{
              backgroundColor: 'transparent',
              borderInlineEnd: 'none',
              color: 'rgba(255,255,255,0.88)',
            }}
            className="yd-admin-menu"
          />
        </div>
        {/* ===== Sider 底部用户区:菜单滚动时固定显示在最底部 ===== */}
        <div
          style={{
            flexShrink: 0,
            borderTop: '1px solid rgba(255,255,255,0.08)',
            backgroundColor: 'rgba(0,0,0,0.25)',
            padding: '12px 16px',
          }}
        >
          <div className="flex items-center gap-2.5">
            <Avatar size={36} icon={<UserOutlined />} src={profile?.avatar_url || undefined} style={{ backgroundColor: '#1677ff', flexShrink: 0 }}>
              {displayName[0]}
            </Avatar>
            <div className="min-w-0 flex-1 leading-tight">
              <div className="truncate text-[13px] font-bold" style={{ color: '#ffffff' }}>
                {displayName}
              </div>
              <div className="mt-0.5 truncate text-[10px]" style={{ color: 'rgba(255,255,255,0.5)' }}>
                {profile?.email || '@' + (profile?.username || 'admin')}
              </div>
            </div>
          </div>
          <div className="mt-2 flex items-center gap-1.5">
            <Button size="small" type="text" icon={<KeyOutlined />} onClick={() => setPwdOpen(true)} className="!flex-1 !text-[11px]" style={{ color: 'rgba(255,255,255,0.75)' }}>
              修改密码
            </Button>
            <Button size="small" type="text" icon={<SwapOutlined />} onClick={() => setSwitchOpen(true)} className="!flex-1 !text-[11px]" style={{ color: 'rgba(255,255,255,0.75)' }}>
              切换
            </Button>
            <Button size="small" type="text" danger icon={<LogoutOutlined />} onClick={handleLogout} className="!flex-1 !text-[11px]">
              退出
            </Button>
          </div>
        </div>

        </div>
</Sider>

      <Layout className="flex flex-col">
        {/* ===== 顶部 Header：清空（账号操作全部移到左下角） ===== */}
        <Header className="!bg-white" style={{ minHeight: 0, height: 0, padding: 0, borderBottom: 'none' }} />

        <Content className="!bg-gray-50 flex-1 p-6">
          <Outlet />
        </Content>
        
      </Layout>

      {/* 修改密码 Modal */}
      <Modal
        title="修改密码"
        open={pwdOpen}
        onCancel={() => {
          setPwdOpen(false)
          pwdForm.resetFields()
        }}
        onOk={() => pwdForm.submit()}
        okText="确认修改"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={pwdForm} layout="vertical" onFinish={handleChangePwd} requiredMark>
          <Form.Item
            name="old_password"
            label="当前密码"
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password placeholder="请输入当前密码" autoComplete="current-password" />
          </Form.Item>
          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少 6 位' },
            ]}
          >
            <Input.Password placeholder="至少 6 位" autoComplete="new-password" />
          </Form.Item>
          <Form.Item
            name="confirm"
            label="确认新密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请再次输入新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'))
                },
              }),
            ]}
          >
            <Input.Password placeholder="再次输入新密码" autoComplete="new-password" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 切换用户 Modal */}
      <Modal
        title="切换用户"
        open={switchOpen}
        onCancel={() => {
          setSwitchOpen(false)
          switchForm.resetFields()
        }}
        onOk={() => switchForm.submit()}
        okText="登录并切换"
        cancelText="取消"
        confirmLoading={switchLoading}
        destroyOnClose
      >
        <Form form={switchForm} layout="vertical" onFinish={handleSwitch} requiredMark>
          <Form.Item
            name="username"
            label="账号"
            rules={[{ required: true, message: '请输入账号' }]}
          >
            <Input placeholder="请输入账号" autoComplete="username" />
          </Form.Item>
          <Form.Item
            name="password"
            label="密码"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder="请输入密码" autoComplete="current-password" />
          </Form.Item>
          <Form.Item
            name="captcha_code"
            label="验证码"
            rules={[{ required: true, message: '请输入图形验证码' }]}
          >
            <div className="flex gap-2">
              <Input placeholder="4 位字符" maxLength={8} className="flex-1" />
              <div
                onClick={refreshSwitchCaptcha}
                className="h-8 w-24 cursor-pointer overflow-hidden rounded border border-gray-200 bg-white"
                title="点击刷新"
              >
                {switchCaptchaImg ? (
                  <img src={switchCaptchaImg} alt="captcha" className="h-full w-full object-contain" />
                ) : (
                  <div className="flex h-full items-center justify-center text-xs text-gray-400">
                    <ReloadOutlined /> 加载中
                  </div>
                )}
              </div>
            </div>
            <div className="mt-1 text-xs text-gray-400">
              Dev 模式可填 <b>ABCD</b>(图片加载失败时仍可登录)
            </div>
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  )
}