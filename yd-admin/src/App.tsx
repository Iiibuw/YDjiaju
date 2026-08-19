import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import Login from './pages/Login'

/**
 * 后台路由（M1：登录页；其他模块 M2 接入）。
 * 用 react-router-dom v7 的 data-router API。
 */
const router = createBrowserRouter([
  { path: '/login', element: <Login /> },
  { path: '/', element: <Login /> },
  { path: '*', element: <Login /> },
])

export default function App() {
  return <RouterProvider router={router} />
}
