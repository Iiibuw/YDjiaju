/**
 * 购物车抽屉（UI 文档 §16.3 🛒 + §10.5 badge 动画）。
 * 列表/数量增减/删除/合计；「去结算」在阶段 5（M6）接入。
 */
import { Link, useNavigate } from 'react-router-dom'

import { useCartStore, useCartTotal } from '../store/cart'

interface Props {
  open: boolean
  onClose: () => void
}

function fmtCents(cents: number): string {
  return `¥${(cents / 100).toLocaleString('zh-CN', { minimumFractionDigits: cents % 100 ? 2 : 0 })}`
}

export default function CartDrawer({ open, onClose }: Props) {
  const items = useCartStore((s) => s.items)
  const updateQty = useCartStore((s) => s.updateQty)
  const remove = useCartStore((s) => s.remove)
  const total = useCartTotal()
  const navigate = useNavigate()

  if (!open) return null

  const checkout = () => {
    onClose()
    navigate('/checkout')
  }

  return (
    <div className="fixed inset-0 z-[60] bg-ink/40" onClick={onClose}>
      <aside
        className="absolute right-0 top-0 flex h-full w-full max-w-md flex-col bg-white shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-center justify-between border-b border-stone-200 px-5 py-4">
          <h3 className="font-display text-lg font-medium text-ink">购物车</h3>
          <button onClick={onClose} className="text-stone-400 hover:text-ink" aria-label="关闭">✕</button>
        </header>

        {items.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-3 text-stone-400">
            <span className="text-4xl">🛒</span>
            <p className="text-sm">购物车还是空的</p>
            <Link to="/products" onClick={onClose} className="text-sm text-gold hover:underline">
              去逛逛 →
            </Link>
          </div>
        ) : (
          <>
            <ul className="flex-1 divide-y divide-stone-100 overflow-y-auto px-5">
              {items.map((it) => (
                <li key={it.id} className="flex gap-3 py-4">
                  {it.cover ? (
                    <img src={it.cover} alt={it.name} className="h-16 w-16 rounded-lg object-cover" />
                  ) : (
                    <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-sand text-stone-300">图</div>
                  )}
                  <div className="flex flex-1 flex-col justify-between py-0.5">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium text-ink line-clamp-2">{it.name}</p>
                      <button onClick={() => remove(it.id)} className="text-xs text-stone-300 hover:text-red-500" aria-label="删除">
                        ✕
                      </button>
                    </div>
                    {it.spec && <p className="text-xs text-stone-400">{it.spec}</p>}
                    <div className="mt-1 flex items-center justify-between">
                      <span className="text-sm font-semibold text-gold">{fmtCents(it.priceCents)}</span>
                      <div className="flex items-center gap-2 text-sm">
                        <button
                          onClick={() => updateQty(it.id, it.qty - 1)}
                          className="flex h-6 w-6 items-center justify-center rounded border border-stone-200 text-stone-500 hover:border-gold hover:text-gold"
                          aria-label="减少"
                        >
                          −
                        </button>
                        <span className="w-6 text-center">{it.qty}</span>
                        <button
                          onClick={() => updateQty(it.id, it.qty + 1)}
                          className="flex h-6 w-6 items-center justify-center rounded border border-stone-200 text-stone-500 hover:border-gold hover:text-gold"
                          aria-label="增加"
                        >
                          +
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
            <footer className="border-t border-stone-200 px-5 py-4">
              <div className="mb-3 flex items-center justify-between text-sm">
                <span className="text-stone-500">合计</span>
                <span className="font-display text-xl font-semibold text-ink">{fmtCents(total)}</span>
              </div>
              <button onClick={checkout} className="btn-gold w-full py-3">
                去结算
              </button>
            </footer>
          </>
        )}
      </aside>
    </div>
  )
}
