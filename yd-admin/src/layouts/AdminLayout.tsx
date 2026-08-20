/** 后台管理布局：左侧菜单 + 顶部栏 + 内容区 + 底部管理员操作区。 */
import { useEffect, useState } from 'react'
import {
  Layout,
  Menu,
  Avatar,
  Dropdown,
  Button,
  Modal,
  Form,
  Input,
  Space,
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

const { Sider, Header, Content, Footer } = Layout

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
  const displayRole = (profile?.role || 'admin').toUpperCase()

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
      <Sider width={220} theme="dark" className="!bg-[#1f1f1f]">
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
        />
      </Sider>

      <Layout className="flex flex-col">
        <Header className="!flex !items-center !justify-between !bg-white !px-6 shadow-sm">
          <h1 className="text-base font-medium text-gray-800">YD 家具 · 内容管理</h1>
          <Dropdown menu={userDropdown} placement="bottomRight" trigger={['click']}>
            <a
              onClick={(e) => e.preventDefault()}
              className="flex items-center gap-2 text-sm text-gray-700 hover:text-blue-600"
            >
              <Avatar size="small" icon={<UserOutlined />} src={profile?.avatar_url || undefined}>
                {displayName[0]}
              </Avatar>
              <span>{displayName}</span>
              <DownOutlined style={{ fontSize: 10 }} />
            </a>
          </Dropdown>
        </Header>

        <Content className="!bg-gray-50 flex-1 p-6">
          <Outlet />
        </Content>

        <Footer className="!bg-white !border-t !border-gray-200 px-6 py-3">
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-gray-500">
            <Space size="middle" wrap>
              <span>YD 家具管理系统 · v1.0</span>
              <span className="text-gray-300">|</span>
              <span>
                角色: <b className="text-gray-700">{displayRole}</b>
              </span>
              <span className="text-gray-300">|</span>
              <span>
                部门: <b className="text-gray-700">{profile?.dept_name || '—'}</b>
              </span>
              <span className="text-gray-300">|</span>
              <span>
                数据权限: <b className="text-gray-700">{profile?.data_scope || 'ALL'}</b>
              </span>
            </Space>
            <Space size="small">
              <Button
                size="small"
                type="text"
                icon={<KeyOutlined />}
                onClick={() => setPwdOpen(true)}
              >
                修改密码
              </Button>
              <Button
                size="small"
                type="text"
                icon={<SwapOutlined />}
                onClick={() => setSwitchOpen(true)}
              >
                切换用户
              </Button>
              <Button
                size="small"
                type="text"
                danger
                icon={<LogoutOutlined />}
                onClick={handleLogout}
              >
                退出登录
              </Button>
            </Space>
          </div>
        </Footer>
      </Layout>

      {/* 浮动左下角管理员入口（截图 3 风格：简洁圆形头像 + 用户名 + 退出） */}
      <div className="fixed bottom-4 left-4 z-50 flex items-center gap-2 rounded-md bg-white px-1.5 py-1 shadow-md ring-1 ring-black/5">
        <Avatar
          size={32}
          style={{ backgroundColor: '#1677ff', flexShrink: 0 }}
          icon={<UserOutlined />}
        >
          {displayName[0]}
        </Avatar>
        <div className="flex flex-col pr-2 leading-tight">
          <span className="text-xs font-medium text-gray-800">{displayName}</span>
          <span className="text-[10px] text-gray-400">({profile?.username})</span>
        </div>
        <Button size="small" type="text" danger onClick={handleLogout}>
          退出
        </Button>
      </div>

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