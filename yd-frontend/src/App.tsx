import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'

/**
 * 路由（M0 占位，M1 补全 14 个页面）
 * 严格对齐原型：
 *  - prototype_前台首页.html → pages/Home/Home.tsx
 *  - prototype_产品中心.html → pages/Products/Products.tsx
 *  - ...
 */
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="*" element={<Home />} />
    </Routes>
  )
}
