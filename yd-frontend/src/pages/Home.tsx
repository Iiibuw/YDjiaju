import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import ProductCard from '../components/ProductCard'
import { products, type ProductListItem } from '../api'

const BANNERS = [
  { id: 1, title: '百年家具 · 大国工匠', subtitle: '每一件家具，都见证时光', image: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1600', link: '/products' },
  { id: 2, title: '胡桃禮系列 · 新品上市', subtitle: '北美黑胡桃 · 现代简约', image: 'https://images.unsplash.com/photo-1567538096342-cd31b4c75e9b?w=1600', link: '/products?series_id=1' },
  { id: 3, title: '预约到店 · 享专属服务', subtitle: '免费方案设计 + 设计师一对一', image: 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1600', link: '/contact' },
]

const STATS = [
  { n: '500+', label: '产品 SKU' },
  { n: '120+', label: '城市门店' },
  { n: '10万+', label: '服务家庭' },
  { n: '70 年', label: '品牌历史' },
]

const PROMISES = [
  { title: '70 年传承', desc: '始于 1953，匠心不变' },
  { title: 'FAS 级原木', desc: '北美进口，纹理自然' },
  { title: '终身维护', desc: '覆盖全国的售后网络' },
]

export default function Home() {
  const { data: featured } = useQuery({
    queryKey: ['products', 'featured'],
    queryFn: () => products.listProducts({ is_top: 1, page_size: 6 }),
  })

  const featuredItems: ProductListItem[] = featured?.items ?? []

  return (
    <>
      {/* ===== Hero 轮播（M1 占位：3 张静态卡） ===== */}
      <section className="relative h-[500px] lg:h-[640px] overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${BANNERS[0].image})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-black/50 to-transparent" />
        </div>
        <div className="relative container-yf h-full flex flex-col justify-center text-white">
          <p className="text-xs uppercase tracking-[0.3em] text-white/80">{BANNERS[0].title}</p>
          <h1 className="mt-4 font-display text-4xl lg:text-6xl font-semibold leading-tight">
            {BANNERS[0].subtitle}
          </h1>
          <div className="mt-8 flex gap-4">
            <Link to="/products" className="inline-flex items-center justify-center px-8 py-3 bg-white text-ink font-medium hover:bg-white/90 transition-colors">
              浏览产品
            </Link>
            <Link to="/contact" className="inline-flex items-center justify-center px-8 py-3 border border-white/40 text-white hover:bg-white/10 transition-colors">
              预约到店
            </Link>
          </div>
        </div>
        <div className="absolute bottom-8 left-0 right-0 flex justify-center gap-2">
          {BANNERS.map((_, i) => (
            <span key={i} className={`w-8 h-0.5 ${i === 0 ? 'bg-white' : 'bg-white/40'}`} />
          ))}
        </div>
      </section>

      {/* ===== 精选产品 ===== */}
      <section className="container-yf py-20">
        <div className="flex items-end justify-between mb-10">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-gold">精选产品</p>
            <h2 className="mt-2 font-display text-3xl lg:text-4xl text-ink">工艺 · 美学 · 时光沉淀</h2>
          </div>
          <Link to="/products" className="text-sm text-stone-600 hover:text-ink">查看全部 →</Link>
        </div>

        {featuredItems.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            {featuredItems.map((p: ProductListItem) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="aspect-[4/5] bg-stone-100 animate-pulse" />
            ))}
          </div>
        )}
      </section>

      {/* ===== 品牌承诺 ===== */}
      <section className="bg-white py-20">
        <div className="container-yf">
          <div className="grid md:grid-cols-3 gap-12 text-center">
            {PROMISES.map((it) => (
              <div key={it.title}>
                <h3 className="font-display text-2xl text-ink">{it.title}</h3>
                <p className="mt-3 text-stone-500 text-sm">{it.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 数据统计 ===== */}
      <section className="bg-sand py-16">
        <div className="container-yf grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {STATS.map((it) => (
            <div key={it.label}>
              <p className="font-display text-4xl text-ink">{it.n}</p>
              <p className="mt-2 text-sm text-stone-500">{it.label}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}
