/** 后台管理布局：左侧菜单 + 顶部栏 + 内容区 + 底部管理员操作区。 */
import { useEffect, useState } from 'react'
import {
  Layout,
  Menu,
  Avatar,
  Dropdown,
  Modal,
  Form,
  Input,
  message,
} from 'antd'
import {
  UserOutlined,
  DownOutlined,
  KeyOutlined,
  LogoutOutlined,
  SwapOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'

import { setToken } from '../api/http'
import { changePassword, fetchProfile, getCaptcha, login, type AdminProfile } from '../api/auth'

const { Sider, Header, Content } = Layout

const MENU = [
  { key: '/dashboard', label: '仪表盘' },
  { key: '/news', label: '资讯管理' },
  { key: '/jobs', label: '招聘管理' },
  { key: '/cases', label: '案例管理' },
  { key: '/orders', label: '订单管理' },
  { key: '/appointments', label: '预约管理' },
  { key: '/members', label: '会员管理' },
  { key: '/messages', label: '留言管理' },
  { key: '/depts', label: '部门管理' },
]

/** 品牌线性图标：沙发 + 桌面（家具元素，简洁线性风格，32px） */
function BrandLogoMark() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-8 w-8"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {/* 沙发主体 */}
      <path d="M4 11V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v3" />
      <path d="M4 11a2 2 0 0 0-2 2v3h20v-3a2 2 0 0 0-2-2H4Z" />
      {/* 沙发扶手 */}
      <path d="M2 16v2M22 16v2" />
      {/* 桌腿 */}
      <path d="M8 6V4h8v2" />
      {/* YD 首字母负形（用短横强调） */}
      <path d="M9 13h6M12 13v2" />
    </svg>
  )
}

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
  const userDropdown = {
    items: [
      {
        key: 'pwd',
        label: '修改密码',
        icon: <KeyOutlined />,
        onClick: () => setPwdOpen(true),
      },
      {
        key: 'switch',
        label: '切换用户',
        icon: <SwapOutlined />,
        onClick: () => setSwitchOpen(true),
      },
      { type: 'divider' as const },
      {
        key: 'logout',
        label: '退出登录',
        icon: <LogoutOutlined />,
        danger: true,
        onClick: handleLogout,
      },
    ],
  }

  return (
    <Layout className="min-h-screen">
      <Sider
        width={220}
        theme="dark"
        className="!flex !flex-col"
        style={{ backgroundColor: '#001529', minHeight: '100vh', height: '100vh', position: 'sticky', top: 0 }}
      >
        {/* Logo 区域：图标 + 品牌名 + 副标题 */}
        {/* ===== 品牌 Logo：线性家具图标(32px) + 紧凑文字，顶部留白减少 ===== */}
        <div
          className="flex h-12 items-center gap-2 border-b px-3.5"
          style={{ borderColor: 'rgba(255,255,255,0.08)' }}
        >
          <span
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg"
            style={{ color: '#c9a227', backgroundColor: 'rgba(201,162,39,0.12)' }}
          >
            <BrandLogoMark />
          </span>
          <div className="flex flex-col leading-none">
            <span className="text-[13px] font-semibold tracking-wide text-white">
              YD 家具
            </span>
            <span className="mt-0.5 text-[9px]" style={{ color: 'rgba(255,255,255,0.4)' }}>
              Admin Console
            </span>
          </div>
        </div>

        {/* ===== 菜单（flex-1 撑开，把底部用户区顶到底） ===== */}
        <div className="flex-1 overflow-y-auto py-1.5">
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
              color: 'rgba(255,255,255,0.72)',
            }}
            className="yd-admin-menu"
          />
        </div>

        {/* ===== 左下角用户区：背景加深 + 头像 + 用户名 + 邮箱 + 退出 ===== */}
        <div
          className="border-t px-3.5 py-3"
          style={{
            borderColor: 'rgba(255,255,255,0.08)',
            backgroundColor: 'rgba(0,0,0,0.25)',
          }}
        >
          <div className="flex items-center gap-2.5">
            <Avatar
              size={36}
              icon={<UserOutlined />}
              src={profile?.avatar_url || undefined}
              style={{ backgroundColor: '#1677ff', flexShrink: 0 }}
            >
              {displayName[0]}
            </Avatar>
            <div className="min-w-0 flex-1 leading-tight">
              <div className="truncate text-[13px] font-medium text-white">{displayName}</div>
              <div className="mt-0.5 truncate text-[10px]" style={{ color: 'rgba(255,255,255,0.45)' }}>
                {profile?.email || `@{profile?.username || 'admin'}`}
              </div>
            </div>
            <button
              onClick={handleLogout}
              title="退出登录"
              className="flex h-7 shrink-0 items-center gap-1 rounded-md px-2 text-[11px] transition-colors"
              style={{
                color: 'rgba(255,255,255,0.65)',
                border: '1px solid rgba(255,255,255,0.15)',
              }}
              onMouseEnter={(e) => {
                const el = e.currentTarget as HTMLElement
                el.style.color = '#ff4d4f'
                el.style.borderColor = 'rgba(255,77,79,0.5)'
                el.style.backgroundColor = 'rgba(255,77,79,0.12)'
              }}
              onMouseLeave={(e) => {
                const el = e.currentTarget as HTMLElement
                el.style.color = 'rgba(255,255,255,0.65)'
                el.style.borderColor = 'rgba(255,255,255,0.15)'
                el.style.backgroundColor = 'transparent'
              }}
            >
              <LogoutOutlined style={{ fontSize: 12 }} />
              退出
            </button>
          </div>
        </div>
      </Sider>

      <Layout className="flex flex-col">
        <Header className="!flex !items-center !justify-end !bg-white !px-6 shadow-sm">
          {/* 顶部 Header：账号菜单全部放到右上角头像下拉（删除原左侧标题） */}
          <Dropdown menu={userDropdown} placement="bottomRight" trigger={['click']}>
            <a
              onClick={(e) => e.preventDefault()}
              className="group flex items-center gap-2 rounded-md border border-transparent px-2 py-1 text-sm text-gray-700 transition-all hover:border-blue-200 hover:bg-blue-50/50"
            >
              <Avatar
                size="small"
                icon={<UserOutlined />}
                src={profile?.avatar_url || undefined}
                style={{ backgroundColor: '#1677ff' }}
              >
                {displayName[0]}
              </Avatar>
              <div className="flex flex-col leading-tight">
                <span className="font-medium">{displayName}</span>
                <span className="text-[10px] text-gray-400">
                  {(profile?.role || 'admin').toUpperCase()}
                </span>
              </div>
              <DownOutlined style={{ fontSize: 10 }} className="text-gray-400 transition-transform group-hover:rotate-180" />
            </a>
          </Dropdown>
        </Header>

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