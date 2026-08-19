import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router'

import { getNewsDetail } from '../api/news'

const fmtDate = (iso: string | null) =>
  iso ? new Date(iso).toLocaleString('zh-CN', { dateStyle: 'long', timeStyle: 'short' }) : ''

export default function NewsDetail() {
  const params = useParams<{ id: string }>()
  const id = Number(params.id ?? '0')
  const { data, isLoading, error } = useQuery({
    queryKey: ['news', id],
    queryFn: () => getNewsDetail(id),
    enabled: id > 0,
  })

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16">
        <div className="h-8 w-3/4 animate-pulse rounded bg-coal/10" />
        <div className="mt-4 h-64 animate-pulse rounded-2xl bg-coal/5" />
      </div>
    )
  }
  if (error || !data) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <p className="text-lg text-coal/60">资讯不存在或已下线</p>
        <Link to="/news" className="mt-4 inline-block text-walnut hover:underline">
          ← 返回资讯列表
        </Link>
      </div>
    )
  }

  return (
    <article className="mx-auto max-w-3xl px-4 py-12">
      <Link to="/news" className="inline-flex items-center text-sm text-walnut hover:underline">
        ← 返回资讯列表
      </Link>

      <header className="mt-6">
        <div className="flex items-center gap-2 text-xs">
          <span className="rounded-full bg-walnut/10 px-2.5 py-1 font-medium text-walnut">
            {data.category === 'company' ? '企业新闻' :'行业资讯'}
          </span>
          {data.is_top && (
            <span className="rounded-full bg-amber-100 px-2.5 py-1 font-medium text-amber-700">置顶</span>
          )}
        </div>
        <h1 className="mt-4 text-3xl font-bold leading-tight text-coal sm:text-4xl">{data.title}</h1>
        {data.subtitle && <p className="mt-3 text-lg text-coal/70">{data.subtitle}</p>}
        <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-1 text-sm text-coal/50">
          <span>📅 {fmtDate(data.published_date)}</span>
          <span>✍ {data.author ?? 'YD 编辑部'}</span>
          {data.source && <span>来源：{data.source}</span>}
          <span>👁 {data.view_count} 次浏览</span>
        </div>
      </header>

      {data.cover_url && (
        <div className="mt-8 overflow-hidden rounded-2xl">
          <img src={data.cover_url} alt={data.title} className="w-full" />
        </div>
      )}

      <div
        className="prose prose-coal mt-10 max-w-none text-base leading-8 [&_p]:my-4 [&_h2]:mt-8 [&_h2]:text-xl [&_h2]:font-bold [&_img]:rounded-lg"
        dangerouslySetInnerHTML={{ __html: data.content }}
      />

      <div className="mt-12 border-t border-coal/10 pt-6 text-center">
        <Link to="/news" className="inline-flex items-center text-walnut hover:underline">
          ← 返回资讯列表
        </Link>
      </div>
    </article>
  )
}