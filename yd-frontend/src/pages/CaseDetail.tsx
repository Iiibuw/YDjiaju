import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { getCaseDetail } from '../api/cases'

export default function CaseDetail() {
  const params = useParams<{ id: string }>()
  const id = Number(params.id ?? '0')
  const { data, isLoading, error } = useQuery({
    queryKey: ['case', id],
    queryFn: () => getCaseDetail(id),
    enabled: id > 0,
  })

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-16">
        <div className="h-8 w-1/2 animate-pulse rounded bg-coal/10" />
        <div className="mt-4 h-96 animate-pulse rounded-2xl bg-coal/5" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-16 text-center">
        <p className="text-lg text-coal/60">案例不存在或已下线</p>
        <Link to="/cases" className="mt-4 inline-block text-walnut hover:underline">
          ← 返回案例列表
        </Link>
      </div>
    )
  }

  return (
    <article className="bg-sand pb-16">
      {/* ===== 顶部信息 ===== */}
      <header className="bg-card py-10">
        <div className="container-yf">
          <Link to="/cases" className="inline-flex items-center text-sm text-walnut hover:underline">
            ← 返回案例列表
          </Link>
          <div className="mt-4 flex items-center gap-2 text-xs">
            {data.style && (
              <span className="rounded bg-walnut/10 px-2.5 py-1 font-medium text-walnut">{data.style}</span>
            )}
            {data.area && <span className="rounded bg-coal/5 px-2.5 py-1 text-coal/70">{data.area}</span>}
            {data.category && (
              <span className="rounded bg-coal/5 px-2.5 py-1 text-coal/70">{data.category.name}</span>
            )}
          </div>
          <h1 className="mt-4 text-3xl font-bold leading-tight text-coal sm:text-4xl">{data.title}</h1>
          <div className="mt-4 flex items-center gap-4 text-sm text-coal/50">
            <span>📅 {data.published_date ? new Date(data.published_date).toLocaleDateString('zh-CN') : '草稿'}</span>
            <span>👁 {data.view_count} 次浏览</span>
          </div>
        </div>
      </header>

      {/* ===== 主图 ===== */}
      {data.cover_url && (
        <div className="container-yf mt-8">
          <div className="overflow-hidden rounded-2xl shadow-lg">
            <img src={data.cover_url} alt={data.title} className="w-full" />
          </div>
        </div>
      )}

      {/* ===== 描述 ===== */}
      {data.description && (
        <div className="container-yf mt-10">
          <div className="rounded-2xl bg-card p-8 shadow-sm ring-1 ring-coal/5">
            <h2 className="mb-4 text-xl font-bold text-coal">项目说明</h2>
            <div
              className="prose max-w-none text-base leading-8 [&_p]:my-4 [&_h3]:mt-6 [&_h3]:text-lg [&_h3]:font-bold [&_ul]:my-3 [&_li]:my-1 [&_img]:rounded-lg"
              dangerouslySetInnerHTML={{ __html: data.description }}
            />
          </div>
        </div>
      )}

      <div className="mt-12 text-center">
        <Link to="/cases" className="inline-flex items-center text-walnut hover:underline">
          ← 返回案例列表
        </Link>
      </div>
    </article>
  )
}