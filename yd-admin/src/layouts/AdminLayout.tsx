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
  { key: '/news', label: '资讯管理' },
  { key: '/jobs', label: '招聘管理' },
  { key: '/cases', label: '案例管理' },
  { key: '/orders', label: '订单管理' },
  { key: '/appointments', label: '预约管理' },
  { key: '/members', label: '会员管理' },
  { key: '/messages', label: '留言管理' },
  { key: '/depts', label: '部门管理' },
]

/** 根据当前路径找标题——和左侧选中菜单一致 */
function resolveHeaderTitle(pathname: string): string {
  const found = MENU.find((m) => m.key === pathname)
  if (found) return `YD 家具 · ${found.label}`
  if (pathname === '/' || pathname === '') return 'YD 家具 · 内容管理'
  return 'YD 家具 · 后台管理'
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
        style={{ backgroundColor: '#001529', minHeight: '100vh', height: '100vh' }}
      >
        <div className="flex h-16 items-center justify-center border-b border-white/10">
          <Link to="/" className="font-display text-lg font-semibold tracking-wide text-white">
            YD · 管理后台
          </Link>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[loc.pathname]}
          items={MENU.map((m) => ({
            key: m.key,
            label: <Link to={m.key}>{m.label}</Link>,
          }))}
          style={{ backgroundColor: '#001529' }}
        />
      </Sider>

      <Layout className="flex flex-col">
        <Header className="!flex !items-center !justify-between !bg-white !px-6 shadow-sm">
          <h1 className="text-base font-medium text-gray-800">{resolveHeaderTitle(loc.pathname)}</h1>
          {/* 右上角账号操作：下拉菜单包含修改密码 / 切换用户 / 退出登录 */}
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