/** 后台管理布局：左侧菜单 + 顶部栏 + 内容区。 */
import { Layout, Menu, Button } from 'antd'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'

import { getToken, setToken } from '../api/http'

const { Sider, Header, Content } = Layout

const MENU = [
  { key: '/news', label: '资讯管理' },
  { key: '/jobs', label: '招聘管理' },
  { key: '/cases', label: '案例管理' },
  { key: '/depts', label: '部门管理' },
  { key: '/members', label: '会员管理' },
  { key: '/messages', label: '留言管理' },
  // M2-3 接入：订单 / 预约 / 仪表盘 ...
]

export default function AdminLayout() {
  const nav = useNavigate()
  const loc = useLocation()

  const handleLogout = () => {
    setToken(null)
    nav('/login', { replace: true })
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
      <Layout>
        <Header className="!flex !items-center !justify-between !bg-white !px-6 shadow-sm">
          <h1 className="text-base font-medium text-gray-800">YD 家具 · 内容管理</h1>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>{getToken() ? '已登录' : '未登录'}</span>
            <Button onClick={handleLogout}>退出</Button>
          </div>
        </Header>
        <Content className="!bg-gray-50 p-6">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}