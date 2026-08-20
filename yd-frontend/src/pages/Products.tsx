import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'

import ProductCard from '../components/ProductCard'
import FilterPanel from '../components/FilterPanel'
import { products, type ProductListItem } from '../api'
import { listCategories } from '../api/categories'

export default function Products() {
  // 三维筛选：空间 / 品类 / 系列
  const [active, setActive] = useState<Record<string, string>>({})

  // 动态分类（阶段 4：后端 /public/categories 按 kind 分组，替代静态 filterGroups）
  const { data: cats } = useQuery({
    queryKey: ['categories', 'all'],
    queryFn: () => listCategories(),
  })
  const filterGroups = useMemo(() => {
    const all = cats ?? []
    const group = (kind: string, name: string) => ({
      name,
      items: all.filter((c) => c.kind === kind).map((c) => ({ key: String(c.id), label: c.name })),
    })
    return [group('space', '空间'), group('series', '系列'), group('category', '品类')]
  }, [cats])

  const params = useMemo(() => {
    const p: products.ListParams = { page_size: 24 }
    if (active['空间']) p.space_id = Number(active['空间'])
    if (active['品类']) p.category_id = Number(active['品类'])
    if (active['系列']) p.series_id = Number(active['系列'])
    return p
  }, [active])

  const { data, isLoading, isError } = useQuery({
    queryKey: ['products', params],
    queryFn: () => products.listProducts(params),
  })

  return (
    <>
      <div className="bg-sand">
        <div className="container-yf py-12">
          <h1 className="font-display text-3xl font-semibold text-ink">产品中心</h1>
          <p className="mt-2 text-stone-500 text-sm">
            严选实木 / 意式真皮 / 极简设计 — 为您的家注入温度与诗意
          </p>
        </div>
      </div>

      <div className="container-yf py-10 grid grid-cols-1 md:grid-cols-[260px_1fr] gap-8">
        <FilterPanel
          groups={filterGroups}
          active={active}
          onChange={(key, val) => setActive((prev) => ({ ...prev, [key]: val }))}
        />

        <section>
          {isLoading && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="aspect-[4/5] bg-stone-100 animate-pulse" />
              ))}
            </div>
          )}

          {isError && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-6 text-sm">
              加载失败：后端 API 未连通（演示模式使用 Mock 数据；详见 UI/UX §第二篇 设计 Token）
            </div>
          )}

          {data && data.items.length === 0 && (
            <div className="bg-card border border-stone-200 p-12 text-center text-stone-500">
              暂无符合筛选条件的产品
            </div>
          )}

          {data && data.items.length > 0 && (
            <>
              <p className="text-xs text-stone-500 mb-4">共 {data.total} 件</p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                {data.items.map((p: ProductListItem) => (
                  <ProductCard key={p.id} product={p} />
                ))}
              </div>
            </>
          )}
        </section>
      </div>
    </>
  )
}
