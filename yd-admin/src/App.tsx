import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import Login from './pages/Login'
import NewsListPage from './pages/NewsList'
import JobsPage from './pages/Jobs'
import AdminLayout from './layouts/AdminLayout'

/**
 * 后台路由（M2-1：资讯 + 招聘 + 登录）。
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
    ],
  },
  { path: '*', element: <Login /> },
])

export default function App() {
  return <RouterProvider router={router} />
}