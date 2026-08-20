/** 购物车结算页（/checkout）：清单 + 收货信息 → 提交订单（阶段 5）。 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'

import { createOrder } from '../api/orders'
import { useCartStore, useCartTotal } from '../store/cart'
import { useToastStore } from '../store/toast'

const fmtCents = (c: number) => `¥${(c / 100).toLocaleString('zh-CN', { minimumFractionDigits: 0 })}`

export default function CartCheckout() {
  const items = useCartStore((s) => s.items)
  const clear = useCartStore((s) => s.clear)
  const total = useCartTotal()
  const toast = useToastStore((s) => s.push)
  const navigate = useNavigate()

  const [form, setForm] = useState({ receiver_name: '', receiver_phone: '', receiver_address: '', remark: '' })
  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }))

  const mut = useMutation({
    mutationFn: () =>
      createOrder({
        items: items.map((i) => ({ product_id: i.id, quantity: i.qty })),
        receiver_name: form.receiver_name,
        receiver_phone: form.receiver_phone,
        receiver_address: form.receiver_address,
        remark: form.remark || null,
      }),
    onSuccess: (o) => {
      clear()
      toast(`订单 ${o.order_no} 提交成功`, 'success')
      navigate('/member')
    },
    onError: (e) => toast(`下单失败：${(e as Error).message}`, 'error'),
  })

  if (items.length === 0) {
    return (
      <div className="container-yf flex flex-col items-center justify-center py-32 text-stone-400">
        <span className="text-5xl">🛒</span>
        <p className="mt-4">购物车为空，先去挑选心仪的家具吧</p>
        <Link to="/products" className="mt-6 text-gold hover:underline">去产品中心 →</Link>
      </div>
    )
  }

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.receiver_name.trim()) return toast('请填写收货人姓名', 'error')
    if (!/^1[3-9]\d{9}$/.test(form.receiver_phone)) return toast('请填写 11 位有效手机号', 'error')
    if (form.receiver_address.trim().length < 5) return toast('请填写详细收货地址', 'error')
    mut.mutate()
  }

  return (
    <div className="container-yf grid gap-10 py-14 lg:grid-cols-[1fr_360px]">
      {/* 商品清单 */}
      <section>
        <h1 className="font-display text-2xl font-medium text-ink">确认订单</h1>
        <div className="card-yf mt-6 divide-y divide-stone-100">
          {items.map((it) => (
            <div key={it.id} className="flex items-center gap-4 p-4">
              {it.cover ? (
                <img src={it.cover} alt={it.name} className="h-16 w-16 rounded-lg object-cover" />
              ) : (
                <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-sand text-stone-300">图</div>
              )}
              <div className="flex-1">
                <p className="text-sm font-medium text-ink">{it.name}</p>
                {it.spec && <p className="text-xs text-stone-400">{it.spec}</p>}
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-gold">{fmtCents(it.priceCents)}</p>
                <p className="text-xs text-stone-400">× {it.qty}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 收货信息 + 提交 */}
      <section>
        <h2 className="font-display text-xl font-medium text-ink">收货信息</h2>
        <form onSubmit={submit} className="card-yf mt-4 space-y-4 p-5">
          <input value={form.receiver_name} onChange={set('receiver_name')} placeholder="收货人姓名" className="input-yf" />
          <input value={form.receiver_phone} onChange={set('receiver_phone')} placeholder="手机号" className="input-yf" inputMode="numeric" />
          <textarea value={form.receiver_address} onChange={set('receiver_address')} placeholder="详细收货地址" rows={3} className="input-yf resize-none" />
          <input value={form.remark} onChange={set('remark')} placeholder="备注（可选）" className="input-yf" />
          <div className="flex items-center justify-between border-t border-stone-100 pt-4">
            <span className="text-sm text-stone-500">合计</span>
            <span className="font-display text-2xl font-semibold text-ink">{fmtCents(total)}</span>
          </div>
          <button type="submit" disabled={mut.isPending} className="btn-gold w-full py-3 disabled:opacity-60">
            {mut.isPending ? '提交中…' : '提交订单'}
          </button>
          <p className="text-center text-xs text-stone-400">登录会员下单可在「我的订单」查看（游客订单不关联账号）</p>
        </form>
      </section>
    </div>
  )
}
