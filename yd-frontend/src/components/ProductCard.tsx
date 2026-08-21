import { Link } from 'react-router-dom'
import type { ProductListItem } from '../api'

interface Props {
  product: ProductListItem
}

/**
 * 产品卡片（首页/产品中心/案例展示共用）
 * 严格对齐 UI/UX §第七篇
 */
export default function ProductCard({ product }: Props) {
  return (
    <Link
      to={`/products/${product.id}`}
      className="group block overflow-hidden bg-white border border-stone-200/60 hover:border-ink/30 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
    >
      <div className="aspect-[4/3] overflow-hidden bg-stone-100">
        {product.cover_url ? (
          <img
            src={product.cover_url}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full grid place-items-center text-stone-400 text-sm">暂无图</div>
        )}
        {product.is_top === 1 && (
          <span className="absolute top-3 left-3 bg-gold text-white text-xs px-2 py-1 rounded-sm">置顶</span>
        )}
      </div>
      <div className="p-5">
        <h3 className="font-display text-base text-ink leading-snug line-clamp-2 group-hover:text-gold transition-colors">
          {product.name}
        </h3>
        {product.subtitle && <p className="mt-1 text-xs text-stone-500 line-clamp-1">{product.subtitle}</p>}
        <p className="mt-3 font-display text-lg text-ink">`¥${product.price_yuan ?? '价格面议'}`</p>
      </div>
    </Link>
  )
}
