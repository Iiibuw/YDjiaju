import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { fmtSalary, listJobs } from '../api/jobs'

const CATEGORY_TABS = [
  { value: '', label: '全部岗位' },
  { value: 'social', label: '社会招聘' },
  { value: 'campus', label: '校园招聘' },
]

export default function Jobs() {
  const [category, setCategory] = useState('')
  const { data, isLoading } = useQuery({
    queryKey: ['jobs', category],
    queryFn: () => listJobs({ category: category || undefined, page_size: 30 }),
  })

  const items = data?.items ?? []

  return (
    <>
      {/* ===== 顶部横幅 ===== */}
      <section className="bg-gradient-to-br from-walnut/10 to-sand py-16">
        <div className="container-yf text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-walnut">Careers</p>
          <h1 className="mt-3 text-4xl font-bold text-coal sm:text-5xl">加入 YD</h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-coal/70">
            与我们一起，把每一件家具做成让时光铭记的作品。
          </p>
        </div>
      </section>

      {/* ===== 分类 tab ===== */}
      <section className="border-b border-coal/10 bg-card">
        <div className="container-yf flex gap-2 py-4">
          {CATEGORY_TABS.map((t) => (
            <button
              key={t.value}
              onClick={() => setCategory(t.value)}
              className={`rounded-full px-5 py-2 text-sm transition ${
                category === t.value
                  ? 'bg-walnut text-white'
                  : 'border border-coal/15 text-coal/70 hover:border-walnut hover:text-walnut'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </section>

      {/* ===== 岗位列表 ===== */}
      <section className="bg-sand py-12">
        <div className="container-yf mx-auto max-w-4xl">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((n) => (
                <div key={n} className="h-36 animate-pulse rounded-2xl bg-coal/5" />
              ))}
            </div>
          ) : items.length === 0 ? (
            <div className="py-20 text-center text-coal/50">暂无在招岗位</div>
          ) : (
            <div className="space-y-4">
              {items.map((j) => (
                <Link
                  key={j.id}
                  to={`/jobs/${j.id}`}
                  className="group flex items-center justify-between gap-6 rounded-2xl bg-card p-6 shadow-sm ring-1 ring-coal/5 transition hover:shadow-md"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold text-coal group-hover:text-walnut">{j.title}</h3>
                      <span className="rounded bg-walnut/10 px-2 py-0.5 text-xs font-medium text-walnut">
                        {j.category === 'social' ? '社招' : '校招'}
                      </span>
                    </div>
                    <p className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-coal/55">
                      {j.department && <span>🏢 {j.department}</span>}
                      {j.location && <span>📍 {j.location}</span>}
                      {j.headcount > 1 && <span>👥 招聘 {j.headcount} 人</span>}
                    </p>
                  </div>
                  <div className="shrink-0 text-right">
                    <p className="font-medium text-walnut">{fmtSalary(j.salary_min_cents, j.salary_max_cents)}</p>
                    <p className="mt-1 text-xs text-coal/50">查看详情 →</p>
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