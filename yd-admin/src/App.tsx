import { createBrowserRouter, RouterProvider, redirect } from 'react-router-dom'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import NewsListPage from './pages/NewsList'
import NewsNewPage from './pages/NewsNew'
import NewsEditPage from './pages/NewsEdit'
import JobsPage from './pages/Jobs'
import Cases from './pages/Cases'
import Departments from './pages/Departments'
import Members from './pages/Members'
import Messages from './pages/Messages'
import Orders from './pages/Orders'
import Appointments from './pages/Appointments'
import JobNewPage from './pages/JobNew'
import CaseNewPage from './pages/CaseNew'
import MemberNewPage from './pages/MemberNew'
import DeptNewPage from './pages/DeptNew'
import AdminLayout from './layouts/AdminLayout'
import { getToken } from './api/http'

/**
 * 路由守卫：无 token 直接重定向到 /login，避免进入受保护页面后全部 401 卡死。
 */
function requireAuth() {
  if (!getToken()) throw redirect('/login')
  return null
}

/**
 * 后台路由（M2-3 + M3）：资讯 + 招聘 + 案例 + 部门 + 会员 + 留言 + 订单 + 预约 + 登录。
 * - 用 react-router v7 data-router API
 * - M3：basename='/admin' 适配 nginx 反代子路径部署
 * - 守卫：所有非 /login 路由通过 loader.requireAuth 校验
 */
const router = createBrowserRouter(
  [
    { path: '/login', element: <Login /> },
    {
      path: '/',
      loader: requireAuth,
      element: <AdminLayout />,
      children: [
        { index: true, element: <Dashboard /> },
        { path: 'dashboard', element: <Dashboard />, loader: requireAuth },
        { path: 'news', element: <NewsListPage />, loader: requireAuth },
        { path: 'news/new', element: <NewsNewPage />, loader: requireAuth },
        { path: 'news/edit/:id', element: <NewsEditPage />, loader: requireAuth },
        { path: 'jobs', element: <JobsPage />, loader: requireAuth },
        { path: 'jobs/new', element: <JobNewPage />, loader: requireAuth },
        { path: 'cases', element: <Cases />, loader: requireAuth },
        { path: 'cases/new', element: <CaseNewPage />, loader: requireAuth },
        { path: 'depts', element: <Departments />, loader: requireAuth },
        { path: 'depts/new', element: <DeptNewPage />, loader: requireAuth },
        { path: 'members', element: <Members />, loader: requireAuth },
        { path: 'members/new', element: <MemberNewPage />, loader: requireAuth },
        { path: 'messages', element: <Messages />, loader: requireAuth },
        { path: 'orders', element: <Orders />, loader: requireAuth },
        { path: 'appointments', element: <Appointments />, loader: requireAuth },
      ],
    },
    // 未登录用户访问任意非白名单路径 → /login
    { path: '*', loader: requireAuth, element: <Login /> },
  ],
  { basename: '/admin' },
)

export default function App() {
  return <RouterProvider router={router} />
}