/**
 * 前台主布局（M4 骨架）：NavBar / Footer / 全局浮窗（搜索·预约·客服·购物车·Toast）。
 * 页面内容经 <Outlet /> 渲染。
 */
import { useState, type ReactNode } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

import BookingModal from '../components/BookingModal'
import CartDrawer from '../components/CartDrawer'
import ChatWidget from '../components/ChatWidget'
import Footer from '../components/Footer'
import NavBar from '../components/NavBar'
import SearchModal from '../components/SearchModal'
import Toast from '../components/Toast'

export default function MainLayout({ children }: { children?: ReactNode }) {
  const [bookingOpen, setBookingOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [cartOpen, setCartOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="flex min-h-screen flex-col bg-sand text-coal">
      <NavBar
        onOpenSearch={() => setSearchOpen(true)}
        onOpenBooking={() => setBookingOpen(true)}
        onOpenCart={() => setCartOpen(true)}
      />

      <main className="flex-1">{children ?? <Outlet />}</main>

      <Footer />

      {/* 全局浮窗（UI 文档 §16.3） */}
      <SearchModal open={searchOpen} onClose={() => setSearchOpen(false)} />
      <BookingModal open={bookingOpen} sourcePage={location.pathname} onClose={() => setBookingOpen(false)} />
      <CartDrawer open={cartOpen} onClose={() => setCartOpen(false)} />
      <ChatWidget />
      <Toast />
    </div>
  )
}
