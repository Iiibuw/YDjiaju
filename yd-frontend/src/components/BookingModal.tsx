/** 预约到店 Modal：接 /appointments。 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'

import { createAppointment } from '../api/orders'

interface Props {
  open: boolean
  sourcePage?: string
  onClose: () => void
}

interface FormState {
  type: string
  name: string
  phone: string
  preferred_date: string
  message: string
}

const empty: FormState = { type: 'visit', name: '', phone: '', preferred_date: '', message: '' }

const TYPES = [
  { value: 'visit', label: '到店参观' },
  { value: 'consult', label: '方案咨询' },
  { value: 'custom', label: '定制服务' },
  { value: 'other', label: '其他' },
]

export default function BookingModal({ open, sourcePage, onClose }: Props) {
  const [form, setForm] = useState<FormState>(empty)
  const [done, setDone] = useState(false)

  const mut = useMutation({
    mutationFn: () =>
      createAppointment({
        type: form.type,
        name: form.name,
        phone: form.phone,
        preferred_date: form.preferred_date ? new Date(form.preferred_date).toISOString() : null,
        message: form.message || null,
        source_page: sourcePage ?? null,
      }),
    onSuccess: () => setDone(true),
    onError: (e) => alert(`预约失败：${(e as Error).message}`),
  })

  if (!open) return null

  const canSubmit = form.name.trim() && /^1[3-9]\d{9}$/.test(form.phone)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => { setDone(false); onClose() }}>
      <div className="w-full max-w-md max-h-[calc(100vh-2rem)] overflow-y-auto rounded-2xl bg-white p-8" onClick={(e) => e.stopPropagation()}>
        {done ? (
          <div className="text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100 text-2xl text-green-600">✓</div>
            <h3 className="mt-4 text-lg font-semibold text-coal">预约成功</h3>
            <p className="mt-2 text-sm text-coal/60">专属顾问将在 1-2 个工作日内与您联系确认到店时间。</p>
            <button
              onClick={() => { setDone(false); setForm(empty); onClose() }}
              className="mt-6 w-full rounded-lg bg-walnut py-2.5 font-medium text-white hover:bg-walnut/90"
            >
              完成
            </button>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-coal">预约到店</h3>
              <button onClick={onClose} className="text-coal/40 hover:text-coal">✕</button>
            </div>
            <p className="mt-1 text-sm text-coal/50">免费上门量尺 + 一对一方案设计</p>

            <div className="mt-6 space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">预约类型</label>
                <div className="flex flex-wrap gap-2">
                  {TYPES.map((t) => (
                    <button
                      key={t.value}
                      onClick={() => setForm({ ...form, type: t.value })}
                      className={`rounded-full px-4 py-1.5 text-sm transition ${
                        form.type === t.value ? 'bg-walnut text-white' : 'border border-coal/15 text-coal/70'
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-coal">姓名 *</label>
                  <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                    placeholder="您的称呼" className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-coal">手机号 *</label>
                  <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}
                    placeholder="11 位手机号" className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">期望到店时间</label>
                <input
                  type="datetime-local"
                  value={form.preferred_date}
                  onChange={(e) => setForm({ ...form, preferred_date: e.target.value })}
                  className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">需求描述</label>
                <textarea value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })}
                  rows={3} placeholder="想看的家具、预算、户型等"
                  className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
              </div>
              <button
                disabled={!canSubmit || mut.isPending}
                onClick={() => mut.mutate()}
                className="w-full rounded-lg bg-walnut py-3 font-medium text-white transition hover:bg-walnut/90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {mut.isPending ? '提交中...' : '提交预约'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}