import { Routes, Route } from 'react-router-dom'
import Login from './pages/Login'

/**
 * 后台路由（M0 占位，M1 接入 ProLayout + 11 模块）
 * 严格对齐 prototype_后台管理_YD家具.html
 */
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="*" element={<Login />} />
    </Routes>
  )
}
