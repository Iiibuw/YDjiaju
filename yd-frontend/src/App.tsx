import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import Home from './pages/Home'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import NewsList from './pages/NewsList'
import NewsDetail from './pages/NewsDetail'
import Cases from './pages/Cases'
import CaseDetail from './pages/CaseDetail'
import About from './pages/About'
import Contact from './pages/Contact'
import Jobs from './pages/Jobs'
import JobDetail from './pages/JobDetail'
import Service from './pages/Service'
import MemberCenter from './pages/MemberCenter'
import Downloads from './pages/Downloads'
import Login from './pages/Login'
import CartCheckout from './pages/CartCheckout'
import MainLayout from './layouts/MainLayout'

/**
 * 前台路由（M2-2：13 个页面，全量页面）。
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
      { path: 'cases', element: <Cases /> },
      { path: 'cases/:id', element: <CaseDetail /> },
      { path: 'about', element: <About /> },
      { path: 'contact', element: <Contact /> },
      { path: 'jobs', element: <Jobs /> },
      { path: 'jobs/:id', element: <JobDetail /> },
      { path: 'service', element: <Service /> },
      { path: 'member', element: <MemberCenter /> },
      { path: 'downloads', element: <Downloads /> },
      { path: 'login', element: <Login /> },
      { path: 'checkout', element: <CartCheckout /> },
      { path: '*', element: <Home /> },
    ],
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
