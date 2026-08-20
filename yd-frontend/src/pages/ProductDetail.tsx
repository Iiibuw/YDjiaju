import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import ImageGallery from '../components/ImageGallery'
import BuyNowModal from '../components/BuyNowModal'
import BookingModal from '../components/BookingModal'
import { products } from '../api'
import { useCartStore } from '../store/cart'
import { useToastStore } from '../store/toast'

export default function ProductDetail() {
  const { id } = useParams()
  const productId = Number(id)
  const [buyOpen, setBuyOpen] = useState(false)
  const [bookingOpen, setBookingOpen] = useState(false)
  const addToCart = useCartStore((s) => s.add)
  const toast = useToastStore((s) => s.push)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => products.getProductDetail(productId),
    enabled: Number.isFinite(productId) && productId > 0,
  })

  const onAddCart = () => {
    if (!data) return
    addToCart({
      id: data.id,
      name: data.name,
      priceCents: data.min_price_cents ?? data.max_price_cents ?? 0,
      cover: data.cover_url,
    })
    toast(`已加入购物车：${data.name}`, 'success')
  }

  return (
    <>
      <div className="container-yf py-6">
        <nav className="text-xs text-stone-500">
          <Link to="/" className="hover:text-ink">首页</Link>
          <span className="mx-2">/</span>
          <Link to="/products" className="hover:text-ink">产品中心</Link>
          {data && (
            <>
              <span className="mx-2">/</span>
              <span className="text-ink">{data.name}</span>
            </>
          )}
        </nav>
      </div>

      {isLoading && (
        <div className="container-yf py-20 text-center text-stone-500">加载中...</div>
      )}

      {isError && (
        <div className="container-yf py-20 text-center">
          <p className="text-stone-500">商品不存在或已下架</p>
          <Link to="/products" className="mt-4 inline-block text-ink hover:underline">
            返回产品中心 →
          </Link>
        </div>
      )}

      {data && (
        <div className="container-yf pb-20 grid md:grid-cols-2 gap-10">
          <ImageGallery
            images={[data.cover_url, ...(data.other_images ?? [])].filter(Boolean) as string[]}
            alt={data.name}
          />

          <div>
            <p className="text-xs text-gold tracking-widest uppercase">
              {data.series?.name ?? '无系列'} · {data.category?.name ?? '未分类'}
            </p>
            <h1 className="mt-3 font-display text-3xl text-ink">{data.name}</h1>
            {data.subtitle && <p className="mt-2 text-stone-500">{data.subtitle}</p>}
            <p className="mt-6 font-display text-2xl text-ink">{data.price_yuan ?? '价格面议'}</p>

            <div className="mt-8 flex gap-3">
              <button className="btn-primary flex-1" onClick={() => setBuyOpen(true)}>立即购买</button>
              <button className="btn-outline flex-1" onClick={onAddCart}>加入购物车</button>
              <button className="btn-outline flex-1" onClick={() => setBookingOpen(true)}>预约到店</button>
            </div>

            {data.specs && Object.keys(data.specs).length > 0 && (
              <div className="mt-10">
                <h3 className="font-display text-base text-ink mb-3">规格参数</h3>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                  {Object.entries(data.specs).map(([k, v]) => (
                    <div key={k} className="flex border-b border-stone-200 py-2">
                      <dt className="w-20 text-stone-500">{k}</dt>
                      <dd className="flex-1 text-ink">{String(v)}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}

            {data.description && (
              <div className="mt-10">
                <h3 className="font-display text-base text-ink mb-3">产品描述</h3>
                <div
                  className="prose prose-stone text-sm"
                  dangerouslySetInnerHTML={{ __html: data.description }}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* 下单 / 预约 Modal */}
      {data && (
        <>
          <BuyNowModal
            open={buyOpen}
            productId={data.id}
            productName={data.name}
            productCover={data.cover_url}
            priceCents={data.min_price_cents ?? data.max_price_cents ?? 0}
            onClose={() => setBuyOpen(false)}
          />
          <BookingModal open={bookingOpen} sourcePage={`/products/${data.id}`} onClose={() => setBookingOpen(false)} />
        </>
      )}
    </>
  )
}
