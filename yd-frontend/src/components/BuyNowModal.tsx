/** 立即购买 Modal：填收货信息 → POST /orders。 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'

import { createOrder, fmtCents } from '../api/orders'

interface Props {
  open: boolean
  productId: number
  productName: string
  productCover: string | null
  priceCents: number
  onClose: () => void
}

interface FormState {
  receiver_name: string
  receiver_phone: string
  receiver_address: string
  remark: string
}

const empty: FormState = { receiver_name: '', receiver_phone: '', receiver_address: '', remark: '' }

export default function BuyNowModal({ open, productId, productName, productCover, priceCents, onClose }: Props) {
  const [form, setForm] = useState<FormState>(empty)
  const [done, setDone] = useState(false)
  const [orderNo, setOrderNo] = useState('')

  const mut = useMutation({
    mutationFn: () =>
      createOrder({
        items: [{ product_id: productId, quantity: 1 }],
        ...form,
      }),
    onSuccess: (o) => {
      setOrderNo(o.order_no)
      setDone(true)
    },
    onError: (e) => alert(`下单失败：${(e as Error).message}`),
  })

  if (!open) return null

  const canSubmit = form.receiver_name.trim() && /^1[3-9]\d{9}$/.test(form.receiver_phone) && form.receiver_address.trim().length >= 5

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => { setDone(false); onClose() }}>
      <div className="w-full max-w-lg rounded-2xl bg-white p-8" onClick={(e) => e.stopPropagation()}>
        {done ? (
          <div className="text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100 text-2xl text-green-600">✓</div>
            <h3 className="mt-4 text-lg font-semibold text-coal">下单成功</h3>
            <p className="mt-2 text-sm text-coal/60">订单号：{orderNo}</p>
            <p className="mt-1 text-sm text-coal/60">请到「会员中心 - 我的订单」查看进度。</p>
            <button
              onClick={() => { setDone(false); setForm(empty); onClose() }}
              className="mt-6 w-full rounded-lg bg-walnut py-2.5 font-medium text-white hover:bg-walnut/90"
            >
              完成
            </button>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-4">
              {productCover && (
                <img src={productCover} alt={productName} className="h-16 w-16 rounded-lg object-cover" />
              )}
              <div className="flex-1">
                <h3 className="font-semibold text-coal">{productName}</h3>
                <p className="mt-1 text-sm">
                  <span className="font-medium text-walnut">{fmtCents(priceCents)}</span>
                  <span className="ml-2 text-coal/50">× 1</span>
                </p>
              </div>
              <button onClick={onClose} className="text-coal/40 hover:text-coal">✕</button>
            </div>

            <div className="mt-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-coal">收货人 *</label>
                  <input value={form.receiver_name} onChange={(e) => setForm({ ...form, receiver_name: e.target.value })}
                    placeholder="姓名" className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-coal">手机号 *</label>
                  <input value={form.receiver_phone} onChange={(e) => setForm({ ...form, receiver_phone: e.target.value })}
                    placeholder="11 位手机号" className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">收货地址 *</label>
                <input value={form.receiver_address} onChange={(e) => setForm({ ...form, receiver_address: e.target.value })}
                  placeholder="省市区 + 详细地址" className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">备注</label>
                <input value={form.remark} onChange={(e) => setForm({ ...form, remark: e.target.value })}
                  placeholder="选填" className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
              </div>
              <button
                disabled={!canSubmit || mut.isPending}
                onClick={() => mut.mutate()}
                className="w-full rounded-lg bg-walnut py-3 font-medium text-white transition hover:bg-walnut/90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {mut.isPending ? '提交中...' : `提交订单（${fmtCents(priceCents)}）`}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}