import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import Login from './pages/Login'
import NewsListPage from './pages/NewsList'
import JobsPage from './pages/Jobs'
import Cases from './pages/Cases'
import Departments from './pages/Departments'
import Members from './pages/Members'
import Messages from './pages/Messages'
import AdminLayout from './layouts/AdminLayout'

/**
 * 后台路由（M2-2：资讯 + 招聘 + 案例 + 部门 + 会员 + 留言 + 登录）。
 * 用 react-router-dom v7 的 data-router API。
 */
const router = createBrowserRouter([
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
    ],
  },
  { path: '*', element: <Login /> },
])

export default function App() {
  return <RouterProvider router={router} />
}