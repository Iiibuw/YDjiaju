import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import NewsCard from '../components/NewsCard'
import { listNews } from '../api/news'

type Tab = 'all' | 'company' | 'industry'

const TABS: { key: Tab; label: string }[] = [
  { key: 'all', label: '全部资讯' },
  { key: 'company', label: '企业新闻' },
  { key: 'industry', label: '行业资讯' },
]

export default function NewsList() {
  const [tab, setTab] = useState<Tab>('all')
  const { data, isLoading } = useQuery({
    queryKey: ['news', tab],
    queryFn: () => listNews(tab === 'all' ? undefined : { category: tab, page_size: 24 }),
  })

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      {/* 头部 */}
      <div className="mb-10 text-center">
        <p className="text-sm font-medium uppercase tracking-widest text-walnut">News & Insights</p>
        <h1 className="mt-2 text-4xl font-bold text-coal">资讯中心</h1>
        <p className="mt-4 text-coal/60">了解 YD 家居最新动态与行业洞察</p>
      </div>

      {/* Tabs */}
      <div className="mb-8 flex justify-center gap-2 border-b border-coal/10">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`relative -mb-px px-4 py-2.5 text-sm font-medium transition ${
              tab === t.key ? 'border-b-2 border-walnut text-walnut' : 'border-b-2 border-transparent text-coal/60 hover:text-coal'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* 列表 */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-72 animate-pulse rounded-2xl bg-coal/5" />
          ))}
        </div>
      ) : !data?.items.length ? (
        <div className="py-16 text-center text-coal/50">暂无资讯</div>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {data.items.map((n) => (
            <NewsCard key={n.id} news={n} />
          ))}
        </div>
      )}
    </div>
  )
}