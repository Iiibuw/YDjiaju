/**
 * 顶部导航（UI 文档 §16.1/§16.2）。
 * - PC(lg+)：6 项一级导航 + 二级下拉 + 右侧操作区（🔍搜索 / 📅预约 / 🛒购物车 badge / 会员）
 * - 移动端(<lg)：汉堡按钮 → 折叠面板（<details> 手风琴）
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
  {
    to: '/about',
    label: '关于我们',
    children: [
      { label: '关于YD', to: '/about#about-yd' },
      { label: '发展历程', to: '/about#history' },
      { label: '品牌介绍', to: '/about#brand' },
      { label: '联系我们', to: '/about#contact' },
    ],
  },
]

const navCls = ({ isActive }: { isActive: boolean }) =>
  `relative py-1 transition-colors after:absolute after:bottom-0 after:left-0 after:h-0.5 after:bg-gold after:transition-all ${
    isActive ? 'font-medium text-ink after:w-full' : 'text-stone-600 hover:text-ink after:w-0 hover:after:w-full'
  }`

export default function NavBar({ onOpenSearch, onOpenBooking, onOpenCart }: Props) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const count = useCartCount()

  // 会员登录态（阶段 5：读 localStorage yd_member_info；脏数据安全兜底）
  let member: { nickname?: string | null; phone?: string } | null = null
  try {
    const raw = localStorage.getItem('yd_member_info')
    member = raw ? (JSON.parse(raw) as { nickname?: string | null; phone?: string }) : null
  } catch {
    localStorage.removeItem('yd_member_info') // 脏数据清理，避免整棵树崩溃
    member = null
  }
  const memberLabel = member ? (member.nickname || member.phone || '会员').slice(0, 8) : '登录'

  return (
    <header className="sticky top-0 z-50 border-b border-stone-200/70 bg-sand/95 backdrop-blur supports-[backdrop-filter]:bg-sand/80">
      <div className="container-yf flex h-16 items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <span className="font-display text-xl font-semibold tracking-wide text-ink">
            YD <span className="text-gold">·</span> 家具
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
                {item.children && <span className="ml-0.5 text-[10px] text-stone-400">▼</span>}
              </NavLink>
              {item.children && (
                <div className="invisible absolute left-1/2 top-full z-50 -translate-x-1/2 pt-2 opacity-0 transition-all group-hover:visible group-hover:opacity-100">
                  <div className="min-w-36 rounded-xl border border-stone-200 bg-white p-1.5 shadow-lg">
                    {item.children.map((c) => (
                      <Link
                        key={c.label}
                        to={c.to}
                        className="block rounded-lg px-3 py-2 text-sm text-stone-600 hover:bg-sand hover:text-ink"
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
        <div className="flex items-center gap-1 sm:gap-3 text-sm">
          <button onClick={onOpenSearch} title="站内搜索" className="p-2 text-stone-500 hover:text-ink transition-colors" aria-label="搜索">
            🔍
          </button>
          <button
            onClick={onOpenBooking}
            className="hidden rounded-full bg-walnut px-4 py-1.5 font-medium text-white hover:bg-walnut/90 sm:inline-flex"
          >
            预约到店
          </button>
          <button onClick={onOpenCart} title="购物车" className="relative p-2 text-stone-500 hover:text-ink transition-colors" aria-label="购物车">
            🛒
            {count > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-gold px-1 text-[10px] font-semibold text-white">
                {count > 99 ? '99+' : count}
              </span>
            )}
          </button>
          <Link to={member ? '/member' : '/login'} className="hidden items-center gap-1 p-2 text-stone-500 hover:text-ink md:inline-flex" title="会员中心">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gold/15 text-xs font-semibold text-gold">
              {member ? memberLabel.slice(0, 1) : '👤'}
            </span>
            {memberLabel}
          </Link>
          {/* 管理后台入口（小图标，移动端隐藏） */}
          <a
            href="/admin/login"
            target="_blank"
            rel="noopener"
            className="hidden items-center gap-1 rounded-md border border-stone-200 bg-white px-2.5 py-1 text-xs text-stone-500 hover:border-walnut hover:text-walnut lg:inline-flex"
            title="管理后台"
          >
            <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 11.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z" />
              <path d="M5 21a7 7 0 0 1 14 0" />
            </svg>
            管理
          </a>
          {/* 移动端汉堡 */}
          <button
            onClick={() => setMobileOpen((v) => !v)}
            className="p-2 text-stone-600 lg:hidden"
            aria-label="菜单"
          >
            ☰
          </button>
        </div>
      </div>

      {/* 移动端折叠菜单 */}
      {mobileOpen && (
        <div className="border-t border-stone-200 bg-white lg:hidden">
          <div className="container-yf flex flex-col py-3 text-sm">
            <Link to="/" onClick={() => setMobileOpen(false)} className="px-3 py-2 text-stone-700 hover:bg-sand rounded-lg">
              首页
            </Link>
            {NAV.map((item) => (
              <details key={item.to} className="group">
                <summary className="flex cursor-pointer list-none items-center justify-between px-3 py-2 text-stone-700 hover:bg-sand rounded-lg">
                  <Link to={item.to} onClick={() => setMobileOpen(false)}>
                    {item.label}
                  </Link>
                  {item.children && <span className="text-stone-400">▾</span>}
                </summary>
                {item.children && (
                  <div className="ml-3 flex flex-col border-l border-stone-200 pl-3">
                    {item.children.map((c) => (
                      <Link
                        key={c.label}
                        to={c.to}
                        onClick={() => setMobileOpen(false)}
                        className="px-3 py-2 text-stone-500 hover:text-ink"
                      >
                        {c.label}
                      </Link>
                    ))}
                  </div>
                )}
              </details>
            ))}
            <div className="mt-2 flex gap-3 border-t border-stone-100 pt-3">
              <button onClick={() => { setMobileOpen(false); onOpenBooking() }} className="btn-primary flex-1 py-2 text-sm">
                预约到店
              </button>
              <Link to="/member" onClick={() => setMobileOpen(false)} className="btn-outline flex-1 py-2 text-sm text-center">
                会员中心
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
