/** 联系我们：门店信息 + 留言表单（接 /members/messages）。 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'

import { submitMessage } from '../api/members'

const STORES = [
  { city: '广州', name: '天河体验馆', address: '天河区珠江新城花城大道 88 号 3F', phone: '020-8888-8888' },
  { city: '佛山', name: '顺德总部旗舰店', address: '顺德区乐从家具城 A 区 1 栋', phone: '0757-6666-6666' },
  { city: '深圳', name: '南山旗舰店', address: '南山区深南大道 9999 号 2F', phone: '0755-3333-3333' },
  { city: '东莞', name: '东城门店', address: '东城区世博大道 66 号 1F', phone: '0769-2222-2222' },
]

interface FormState {
  name: string
  phone: string
  email: string
  content: string
}

export default function Contact() {
  const [form, setForm] = useState<FormState>({ name: '', phone: '', email: '', content: '' })

  const mut = useMutation({
    mutationFn: (payload: FormState) => submitMessage(payload),
    onSuccess: () => {
      setForm({ name: '', phone: '', email: '', content: '' })
      alert('留言已提交，我们会尽快与您联系！')
    },
    onError: (e) => alert(`提交失败：${(e as Error).message}`),
  })

  const canSubmit = form.name.trim() && form.content.trim().length >= 5

  return (
    <>
      {/* ===== 顶部横幅 ===== */}
      <section className="bg-gradient-to-br from-walnut/10 to-sand py-16">
        <div className="container-yf text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-walnut">Contact Us</p>
          <h1 className="mt-3 text-4xl font-bold text-coal sm:text-5xl">联系我们</h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-coal/70">
            无论您是选购家具、定制设计，还是加盟合作，欢迎随时与我们联系。
          </p>
        </div>
      </section>

      {/* ===== 门店信息 ===== */}
      <section className="bg-white py-16">
        <div className="container-yf">
          <h2 className="text-2xl font-bold text-coal">门店地址</h2>
          <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {STORES.map((s) => (
              <div key={s.name} className="rounded-2xl border border-coal/5 bg-sand/40 p-6">
                <p className="text-sm font-medium uppercase tracking-widest text-walnut">{s.city}</p>
                <h3 className="mt-2 font-semibold text-coal">{s.name}</h3>
                <p className="mt-3 text-sm leading-6 text-coal/60">{s.address}</p>
                <p className="mt-2 text-sm text-walnut">{s.phone}</p>
              </div>
            ))}
          </div>
          <div className="mt-8 rounded-2xl bg-sand p-6 text-center text-sm text-coal/70">
            📞 全国服务热线：<span className="font-medium text-coal">400-800-1953</span>（9:00-21:00）
          </div>
        </div>
      </section>

      {/* ===== 留言表单 ===== */}
      <section className="bg-sand py-16">
        <div className="container-yf mx-auto max-w-2xl">
          <div className="rounded-2xl bg-white p-8 shadow-sm ring-1 ring-coal/5">
            <h2 className="text-2xl font-bold text-coal">在线留言</h2>
            <p className="mt-2 text-sm text-coal/60">留下您的需求，我们将在 1-2 个工作日内回复。</p>

            <div className="mt-6 space-y-5">
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">称呼 *</label>
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="您的称呼"
                  className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                />
              </div>
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-coal">联系电话</label>
                  <input
                    value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                    placeholder="便于我们回电"
                    className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-coal">邮箱</label>
                  <input
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    placeholder="you@example.com"
                    className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                  />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">留言内容 *</label>
                <textarea
                  value={form.content}
                  onChange={(e) => setForm({ ...form, content: e.target.value })}
                  placeholder="想了解的产品、预算、户型等（≥5 字）"
                  rows={5}
                  className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                />
              </div>
              <button
                disabled={!canSubmit || mut.isPending}
                onClick={() => mut.mutate(form)}
                className="w-full rounded-lg bg-walnut py-3 font-medium text-white transition hover:bg-walnut/90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {mut.isPending ? '提交中...' : '提交留言'}
              </button>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}