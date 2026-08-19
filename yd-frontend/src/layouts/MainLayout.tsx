import { Link, Outlet } from 'react-router-dom'
import type { ReactNode } from 'react'

const NAV_ITEMS = [
  { to: '/', label: '首页' },
  { to: '/products', label: '产品中心' },
  { to: '/cases', label: '案例展示' },
  { to: '/news', label: '新闻资讯' },
  { to: '/jobs', label: '人才招聘' },
  { to: '/about', label: '关于我们' },
  { to: '/contact', label: '联系我们' },
]

export default function MainLayout({ children }: { children?: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-sand text-coal">
      {/* ===== 顶部导航 ===== */}
      <header className="sticky top-0 z-30 border-b border-stone-200/60 bg-white/90 backdrop-blur supports-[backdrop-filter]:bg-white/80">
        <div className="container-yf flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <span className="font-display text-xl font-semibold tracking-wide text-ink">
              YD <span className="text-gold">·</span> 家具
            </span>
          </Link>
          <nav className="hidden md:flex gap-8 text-sm text-stone-600">
            {NAV_ITEMS.map((it) => (
              <Link
                key={it.to}
                to={it.to}
                className="hover:text-ink transition-colors relative py-1 [&.active]:text-ink"
              >
                {it.label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-4 text-sm">
            <Link to="/login" className="text-stone-500 hover:text-ink" title="后台">
              后台
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">{children ?? <Outlet />}</main>

      {/* ===== 底部 ===== */}
      <footer className="border-t border-stone-200 mt-20 bg-white">
        <div className="container-yf py-12 grid md:grid-cols-4 gap-8 text-sm text-stone-600">
          <div>
            <h4 className="font-display text-base text-ink mb-4">YD 家具</h4>
            <p className="text-stone-500 leading-relaxed">
              百年家具品牌，传承匠心工艺，融合现代美学。
            </p>
          </div>
          <div>
            <h4 className="font-display text-base text-ink mb-4">产品</h4>
            <ul className="space-y-2">
              <li><Link to="/products" className="hover:text-ink">产品中心</Link></li>
              <li><Link to="/cases" className="hover:text-ink">案例展示</Link></li>
              <li><Link to="/downloads" className="hover:text-ink">下载中心</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-display text-base text-ink mb-4">关于</h4>
            <ul className="space-y-2">
              <li><Link to="/about" className="hover:text-ink">关于我们</Link></li>
              <li><Link to="/news" className="hover:text-ink">新闻资讯</Link></li>
              <li><Link to="/jobs" className="hover:text-ink">人才招聘</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-display text-base text-ink mb-4">联系</h4>
            <p className="text-stone-500 leading-relaxed">
              客服电话：400-xxx-xxxx<br />
              工作时间：9:00 - 18:00<br />
              地址：广东省佛山市顺德区
            </p>
          </div>
        </div>
        <div className="border-t border-stone-200 py-6 text-center text-xs text-stone-500">
          © 2026 YD 家具 · 基于 PRD v1.1 + UI/UX v1.0 + 开发技术文档 v1.1
        </div>
      </footer>
    </div>
  )
}
