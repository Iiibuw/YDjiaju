/**
 * 顶部导航（UI 文档 §16.1/§16.2）。
 * - PC(lg+)：6 项一级导航 + 二级下拉 + 右侧操作区（🔍搜索 / 📅预约 / 🛒购物车 badge / 会员）
 * - 移动端(<lg)：汉堡按钮 → 折叠面板（<details> 手风琴）
 *
 * 黑金色独立区段：v2.1 回滚时 NavBar/Footer 保留奢华配色（不依赖 token），
 * 其他页面已恢复浅色（commit f57cebc 之前的风格）。
 */
import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'

import { useCartCount } from '../store/cart'

interface Props {
  onOpenSearch: () => void
  onOpenBooking: () => void
  onOpenCart: () => void
}

const NAV = [
  {
    to: '/products',
    label: '产品中心',
    children: [
      { label: '全部产品', to: '/products' },
      { label: '客厅精选', to: '/products?space=客厅' },
      { label: '卧室精选', to: '/products?space=卧室' },
      { label: '书房精选', to: '/products?space=书房' },
      { label: '茶室精选', to: '/products?space=茶室' },
      { label: '办公家具', to: '/products?space=办公' },
    ],
  },
  { to: '/cases', label: '案例展示' },
  {
    to: '/news',
    label: '新闻资讯',
    children: [
      { label: '企业新闻', to: '/news#corp' },
      { label: '行业资讯', to: '/news#ind' },
    ],
  },
  {
    to: '/jobs',
    label: '人才招聘',
    children: [
      { label: '社会招聘', to: '/jobs#social' },
      { label: '校园招聘', to: '/jobs#campus' },
    ],
  },
  { to: '/about', label: '关于YD' },
]

// 黑金色 hardcoded（不依赖 token）—— NavBar/Footer 是固定奢华区
// v2.2：深色底从 #0d0b09 提到 #2c2520（暖深褐），让米白文字更清晰
const GOLD = '#c9a227'
const INK_LIGHT = '#ece5d8'
const SUB = '#d4ccb8' // 加亮版次级文字
const DEEPER_BG = '#3a3128'
const BORDER = '#4a3f32'

const navCls = ({ isActive }: { isActive: boolean }) =>
  `relative inline-flex items-center py-1 outline-none transition-colors focus:outline-none after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-[${GOLD}] after:transition-all ${
    isActive
      ? `font-semibold text-[${GOLD}] after:w-full`
      : `text-[${SUB}] hover:text-[${INK_LIGHT}] after:w-0 hover:after:w-full`
  }`

export default function NavBar({ onOpenSearch, onOpenBooking, onOpenCart }: Props) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const count = useCartCount()

  // 会员登录态
  let member: { nickname?: string | null; phone?: string } | null = null
  try {
    const raw = localStorage.getItem('yd_member_info')
    member = raw ? (JSON.parse(raw) as { nickname?: string | null; phone?: string }) : null
  } catch {
    localStorage.removeItem('yd_member_info')
    member = null
  }
  const memberLabel = member ? (member.nickname || member.phone || '会员').slice(0, 8) : '登录'

  return (
    <header
      className="sticky top-0 z-50 border-b backdrop-blur"
      style={{
        backgroundColor: 'rgba(44,37,32,0.95)',
        borderColor: BORDER,
      }}
    >
      <div className="container-yf flex h-16 items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <span className="font-display text-xl font-semibold tracking-wide" style={{ color: INK_LIGHT }}>
            YD <span style={{ color: GOLD }}>·</span> 家具
          </span>
        </Link>

        {/* PC 导航 */}
        <nav className="hidden items-center gap-7 text-sm lg:flex">
          <NavLink to="/" end className={navCls}>
            首页
          </NavLink>
          {NAV.map((item) => (
            <div key={item.to} className="group relative">
              <NavLink to={item.to} className={navCls}>
                {item.label}
                {item.children && (
                  <span className="ml-1 inline-flex text-[9px] leading-none" style={{ color: SUB }}>
                    ▼
                  </span>
                )}
              </NavLink>
              {item.children && (
                <div className="invisible absolute left-1/2 top-full z-50 -translate-x-1/2 pt-2 opacity-0 transition-all group-hover:visible group-hover:opacity-100">
                  <div
                    className="min-w-36 rounded-xl border p-1.5 shadow-lg shadow-black/50"
                    style={{ backgroundColor: DEEPER_BG, borderColor: BORDER }}
                  >
                    {item.children.map((c) => (
                      <Link
                        key={c.label}
                        to={c.to}
                        className="block rounded-lg px-3 py-2 text-sm hover:text-[#ece5d8]"
                        style={{ color: SUB }}
                        onMouseEnter={(e) => {
                          ;(e.currentTarget as HTMLElement).style.backgroundColor = '#1f1a14'
                        }}
                        onMouseLeave={(e) => {
                          ;(e.currentTarget as HTMLElement).style.backgroundColor = 'transparent'
                        }}
                      >
                        {c.label}
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </nav>

        {/* 右侧操作区 */}
        <div className="flex items-center gap-1 text-sm sm:gap-3">
          <button
            onClick={onOpenSearch}
            title="站内搜索"
            className="p-2 transition-colors"
            style={{ color: SUB }}
            aria-label="搜索"
          >
            🔍
          </button>
          <button
            onClick={onOpenBooking}
            className="hidden rounded-full px-4 py-1.5 font-medium text-[#1a150c] sm:inline-flex"
            style={{ backgroundColor: GOLD }}
          >
            预约到店
          </button>
          <button
            onClick={onOpenCart}
            title="购物车"
            className="relative p-2 transition-colors"
            style={{ color: SUB }}
            aria-label="购物车"
          >
            🛒
            {count > 0 && (
              <span
                className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[10px] font-semibold text-[#1a150c]"
                style={{ backgroundColor: GOLD }}
              >
                {count > 99 ? '99+' : count}
              </span>
            )}
          </button>
          <Link
            to={member ? '/member' : '/login'}
            className="hidden items-center gap-1 p-2 md:inline-flex"
            style={{ color: SUB }}
            title="会员中心"
          >
            <span
              className="flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold"
              style={{ backgroundColor: 'rgba(201,162,39,0.15)', color: GOLD }}
            >
              {member ? memberLabel.slice(0, 1) : '👤'}
            </span>
            {memberLabel}
          </Link>
          {/* 管理后台入口已移至首页底部，此处不再显示 */}
          {/* 移动端汉堡 */}
          <button
            onClick={() => setMobileOpen((v) => !v)}
            className="p-2 lg:hidden"
            style={{ color: SUB }}
            aria-label="菜单"
          >
            ☰
          </button>
        </div>
      </div>

      {/* 移动端折叠菜单（也保持黑金） */}
      {mobileOpen && (
        <div className="border-t lg:hidden" style={{ backgroundColor: DEEPER_BG, borderColor: BORDER }}>
          <div className="container-yf flex flex-col py-3 text-sm">
            <Link
              to="/"
              onClick={() => setMobileOpen(false)}
              className="rounded-lg px-3 py-2"
              style={{ color: INK_LIGHT }}
            >
              首页
            </Link>
            {NAV.map((item) => (
              <details key={item.to} className="group">
                <summary
                  className="flex cursor-pointer list-none items-center justify-between rounded-lg px-3 py-2"
                  style={{ color: INK_LIGHT }}
                >
                  <Link to={item.to} onClick={() => setMobileOpen(false)}>
                    {item.label}
                  </Link>
                  {item.children && <span style={{ color: SUB }}>▾</span>}
                </summary>
                {item.children && (
                  <div className="ml-3 flex flex-col border-l pl-3" style={{ borderColor: BORDER }}>
                    {item.children.map((c) => (
                      <Link
                        key={c.label}
                        to={c.to}
                        onClick={() => setMobileOpen(false)}
                        className="px-3 py-2"
                        style={{ color: SUB }}
                      >
                        {c.label}
                      </Link>
                    ))}
                  </div>
                )}
              </details>
            ))}
            <div className="mt-2 flex gap-3 border-t pt-3" style={{ borderColor: BORDER }}>
              <button
                onClick={() => {
                  setMobileOpen(false)
                  onOpenBooking()
                }}
                className="flex-1 rounded-lg py-2 text-sm font-medium text-[#1a150c]"
                style={{ backgroundColor: GOLD }}
              >
                预约到店
              </button>
              <Link
                to="/member"
                onClick={() => setMobileOpen(false)}
                className="flex-1 rounded-lg border py-2 text-center text-sm"
                style={{ borderColor: GOLD, color: GOLD }}
              >
                会员中心
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}