/**
 * 首页
 * 严格对齐 prototype_前台首页_YD家具.html
 *
 * 当前为 M0 占位：展示页面框架、品牌色、设计 Token 集成情况。
 * M1 将：
 *  1. 拉取 `GET /api/v1/public/banners` 渲染轮播图
 *  2. 拉取 `/public/products?featured=true` 渲染精选产品
 *  3. 拉取 `/public/cases?featured=true` 渲染精选案例
 *  4. 接入顶部导航 / 页脚 / 客服浮窗
 */
export default function Home() {
  return (
    <main className="min-h-screen">
      {/* 顶部导航占位（M1 实施） */}
      <header className="border-b border-stone-200/60 bg-white/80 backdrop-blur">
        <div className="container-yf flex h-16 items-center justify-between">
          <a href="/" className="font-display text-xl font-semibold tracking-wide text-ink">
            YD <span className="text-gold">·</span> 家具
          </a>
          <nav className="hidden md:flex gap-8 text-sm text-stone-600">
            <a href="/">首页</a>
            <a href="/products">产品中心</a>
            <a href="/cases">案例</a>
            <a href="/news">新闻</a>
            <a href="/about">关于我们</a>
            <a href="/jobs">招聘</a>
            <a href="/contact">联系我们</a>
          </nav>
        </div>
      </header>

      {/* Hero 占位 */}
      <section className="relative bg-sand">
        <div className="container-yf py-20 lg:py-32 text-center">
          <p className="font-display text-xs uppercase tracking-[0.3em] text-gold">
            百年家具品牌
          </p>
          <h1 className="mt-4 font-display text-4xl lg:text-6xl font-semibold text-ink">
            每一件家具，都见证时光
          </h1>
          <p className="mt-6 text-stone-600 max-w-2xl mx-auto">
            YD 家具 · 自 1953 年起，专注实木家具的设计与制作。
            传承匠心工艺，融合现代美学，为您的家注入温度与诗意。
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <button className="btn-primary">浏览产品</button>
            <button className="btn-outline">预约到店</button>
          </div>
        </div>
      </section>

      {/* 设计 Token 状态卡（M0 验证用，M1 删除） */}
      <section className="container-yf py-12">
        <div className="bg-white border border-stone-200 rounded-lg p-6">
          <h2 className="font-display text-lg font-semibold text-ink">
            ✅ M0 基础设施已就绪
          </h2>
          <ul className="mt-4 space-y-2 text-sm text-stone-600">
            <li>✓ React 19 + Vite 5 + TypeScript 5.6</li>
            <li>✓ Tailwind CSS 设计 Token（stone/gold/sand）已落地</li>
            <li>✓ React Router 7 + TanStack Query 5 + Zustand 5</li>
            <li>⏳ M1：连接 FastAPI 后端 + 渲染产品/案例/新闻数据</li>
          </ul>
        </div>
      </section>

      <footer className="border-t border-stone-200 py-12 mt-20">
        <div className="container-yf text-center text-sm text-stone-500">
          © 2026 YD 家具 · 基于 UI/UX 设计规格文档 v1.0
        </div>
      </footer>
    </main>
  )
}
