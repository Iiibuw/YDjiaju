import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import Home from './pages/Home'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import NewsList from './pages/NewsList'
import NewsDetail from './pages/NewsDetail'
import MainLayout from './layouts/MainLayout'

/**
 * 前台路由（M2-1：5 个页面，含资讯列表/详情）。
 * 用 react-router-dom v7 的 data-router API（createBrowserRouter）。
 */
const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'products', element: <Products /> },
      { path: 'products/:id', element: <ProductDetail /> },
      { path: 'news', element: <NewsList /> },
      { path: 'news/:id', element: <NewsDetail /> },
      { path: '*', element: <Home /> },
    ],
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
