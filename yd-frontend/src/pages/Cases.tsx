import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { listCases } from '../api/cases'

const STYLES = [
  { id: 0, label: '全部' },
  { id: 1, label: '现代简约' },
  { id: 2, label: '现代北欧' },
  { id: 3, label: '新中式' },
  { id: 4, label: '轻奢风' },
]

export default function Cases() {
  const { data, isLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: () => listCases({ page_size: 24 }),
  })

  const items = data?.items ?? []

  return (
    <>
      {/* ===== 顶部横幅 ===== */}
      <section className="bg-gradient-to-br from-walnut/10 to-sand py-16">
        <div className="container-yf text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-walnut">Cases Showcase</p>
          <h1 className="mt-3 text-4xl font-bold text-coal sm:text-5xl">客户实景案例</h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-coal/70">
            100+ 实景落地项目，覆盖全国家庭，涵盖现代简约、北欧、新中式等多种风格。
          </p>
        </div>
      </section>

      {/* ===== 风格筛选 ===== */}
      <section className="border-b border-coal/10 bg-white">
        <div className="container-yf flex flex-wrap items-center gap-2 py-4">
          {STYLES.map((s) => (
            <button
              key={s.id}
              className={`rounded-full px-4 py-1.5 text-sm transition ${
                s.id === 0
                  ? 'bg-walnut text-white'
                  : 'border border-coal/15 text-coal/70 hover:border-walnut hover:text-walnut'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </section>

      {/* ===== 案例卡片网格 ===== */}
      <section className="bg-sand py-12">
        <div className="container-yf">
          {isLoading ? (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((n) => (
                <div key={n} className="h-80 animate-pulse rounded-2xl bg-coal/5" />
              ))}
            </div>
          ) : items.length === 0 ? (
            <div className="py-20 text-center text-coal/50">暂无案例</div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((c) => (
                <Link
                  key={c.id}
                  to={`/cases/${c.id}`}
                  className="group block overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-coal/5 hover:shadow-lg"
                >
                  <div className="aspect-[4/3] overflow-hidden bg-coal/5">
                    {c.cover_url ? (
                      <img
                        src={c.cover_url}
                        alt={c.title}
                        className="h-full w-full object-cover transition group-hover:scale-105"
                        loading="lazy"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center text-coal/40">暂无封面</div>
                    )}
                  </div>
                  <div className="p-5">
                    <div className="mb-2 flex items-center gap-2 text-xs">
                      {c.style && (
                        <span className="rounded bg-walnut/10 px-2 py-0.5 font-medium text-walnut">
                          {c.style}
                        </span>
                      )}
                      {c.area && <span className="text-coal/50">{c.area}</span>}
                    </div>
                    <h3 className="line-clamp-2 font-semibold text-coal group-hover:text-walnut">{c.title}</h3>
                    <p className="mt-3 flex items-center gap-3 text-xs text-coal/50">
                      <span>👁 {c.view_count}</span>
                      <span>{c.published_date ? new Date(c.published_date).toLocaleDateString('zh-CN') : ''}</span>
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  )
}