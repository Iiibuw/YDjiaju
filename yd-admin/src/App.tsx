import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import Login from './pages/Login'
import NewsListPage from './pages/NewsList'
import JobsPage from './pages/Jobs'
import Cases from './pages/Cases'
import Departments from './pages/Departments'
import Members from './pages/Members'
import Messages from './pages/Messages'
import Orders from './pages/Orders'
import Appointments from './pages/Appointments'
import AdminLayout from './layouts/AdminLayout'

/**
 * 后台路由（M2-3：资讯 + 招聘 + 案例 + 部门 + 会员 + 留言 + 订单 + 预约 + 登录）。
 * 用 react-router-dom v7 的 data-router API。
 * M3：basename='/admin' 适配 nginx 反代子路径部署。
 */
const router = createBrowserRouter(
  [
    { path: '/login', element: <Login /> },
    {
      path: '/',
      element: <AdminLayout />,
      children: [
        { index: true, element: <NewsListPage /> },
        { path: 'news', element: <NewsListPage /> },
        { path: 'jobs', element: <JobsPage /> },
        { path: 'cases', element: <Cases /> },
        { path: 'depts', element: <Departments /> },
        { path: 'members', element: <Members /> },
        { path: 'messages', element: <Messages /> },
        { path: 'orders', element: <Orders /> },
        { path: 'appointments', element: <Appointments /> },
      ],
    },
    { path: '*', element: <Login /> },
  ],
  { basename: '/admin' },
)

export default function App() {
  return <RouterProvider router={router} />
}