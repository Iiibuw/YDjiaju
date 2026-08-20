import { Link } from 'react-router'

import type { NewsListItem } from '../api/news'

const fmtDate = (iso: string | null) =>
  iso ? new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }) : ''

export default function NewsCard({ news }: { news: NewsListItem }) {
  return (
    <Link
      to={`/news/${news.id}`}
      className="group block overflow-hidden rounded-2xl bg-card shadow-sm ring-1 ring-coal/5 transition hover:-translate-y-0.5 hover:shadow-lg"
    >
      <div className="relative aspect-[16/9] overflow-hidden bg-sand">
        {news.cover_url ? (
          <img
            src={news.cover_url}
            alt={news.title}
            loading="lazy"
            className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-coal/40">暂无封面</div>
        )}
        <div className="absolute left-3 top-3 flex gap-1.5">
          {news.is_top && (
            <span className="rounded-full bg-walnut px-2.5 py-0.5 text-xs font-medium text-white">置顶</span>
          )}
          {news.is_recommend && (
            <span className="rounded-full bg-amber-500 px-2.5 py-0.5 text-xs font-medium text-white">推荐</span>
          )}
        </div>
        <div className="absolute right-3 top-3">
          <span className="rounded-full bg-black/60 px-2 py-0.5 text-xs text-white">
            {news.category === 'company' ? '企业新闻' :'行业资讯'}
          </span>
        </div>
      </div>
      <div className="p-5">
        <h3 className="line-clamp-2 text-lg font-semibold text-coal transition group-hover:text-walnut">
          {news.title}
        </h3>
        {news.summary && (
          <p className="mt-2 line-clamp-2 text-sm leading-6 text-coal/70">{news.summary}</p>
        )}
        <div className="mt-4 flex items-center justify-between text-xs text-coal/50">
          <span>{news.author ?? 'YD 编辑部'}</span>
          <div className="flex items-center gap-3">
            <span>{fmtDate(news.published_date)}</span>
            <span>👁 {news.view_count}</span>
          </div>
        </div>
      </div>
    </Link>
  )
}