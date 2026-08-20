import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { applyJob, fmtSalary, getJobDetail } from '../api/jobs'

interface ApplyForm {
  name: string
  phone: string
  email: string
}

const emptyForm: ApplyForm = { name: '', phone: '', email: '' }

export default function JobDetail() {
  const params = useParams<{ id: string }>()
  const id = Number(params.id ?? '0')
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState<ApplyForm>(emptyForm)
  const [done, setDone] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['job', id],
    queryFn: () => getJobDetail(id),
    enabled: id > 0,
  })

  const applyMut = useMutation({
    mutationFn: () => applyJob({ job_id: id, name: form.name, phone: form.phone, email: form.email || null }),
    onSuccess: () => {
      setDone(true)
    },
    onError: (e) => alert(`投递失败：${(e as Error).message}`),
  })

  const canApply = form.name.trim() && /^1[3-9]\d{9}$/.test(form.phone)

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16">
        <div className="h-8 w-2/3 animate-pulse rounded bg-coal/10" />
        <div className="mt-6 h-64 animate-pulse rounded-2xl bg-coal/5" />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <p className="text-lg text-coal/60">岗位不存在或已下线</p>
        <Link to="/jobs" className="mt-4 inline-block text-walnut hover:underline">← 返回招聘列表</Link>
      </div>
    )
  }

  return (
    <article className="bg-sand pb-16">
      {/* ===== 顶部 ===== */}
      <header className="bg-card py-10">
        <div className="container-yf mx-auto max-w-3xl">
          <Link to="/jobs" className="inline-flex items-center text-sm text-walnut hover:underline">← 返回招聘列表</Link>
          <div className="mt-4 flex items-center gap-2 text-xs">
            <span className="rounded bg-walnut/10 px-2.5 py-1 font-medium text-walnut">
              {data.category === 'social' ? '社会招聘' : '校园招聘'}
            </span>
            {data.department && <span className="rounded bg-coal/5 px-2.5 py-1 text-coal/70">{data.department}</span>}
            {data.location && <span className="rounded bg-coal/5 px-2.5 py-1 text-coal/70">📍 {data.location}</span>}
          </div>
          <h1 className="mt-4 text-3xl font-bold leading-tight text-coal sm:text-4xl">{data.title}</h1>
          <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
            <div className="text-sm text-coal/50">
              <span className="mr-4">👥 招聘 {data.headcount} 人</span>
              {data.expire_date && <span>⏰ 截止 {new Date(data.expire_date).toLocaleDateString('zh-CN')}</span>}
            </div>
            <button
              onClick={() => { setDone(false); setModalOpen(true) }}
              className="rounded-lg bg-walnut px-6 py-2.5 font-medium text-white transition hover:bg-walnut/90"
            >
              立即投递
            </button>
          </div>
        </div>
      </header>

      {/* ===== 薪资卡 ===== */}
      <div className="container-yf mx-auto max-w-3xl">
        <div className="mt-8 rounded-2xl bg-card p-6 shadow-sm ring-1 ring-coal/5">
          <div className="flex items-center justify-between">
            <span className="text-sm text-coal/50">薪资范围</span>
            <span className="text-2xl font-bold text-walnut">{fmtSalary(data.salary_min_cents, data.salary_max_cents)}</span>
          </div>
        </div>

        {/* ===== 职责 ===== */}
        {data.description && (
          <div className="mt-6 rounded-2xl bg-card p-8 shadow-sm ring-1 ring-coal/5">
            <h2 className="mb-4 text-xl font-bold text-coal">岗位职责</h2>
            <div className="prose max-w-none leading-8 text-coal/80 [&_p]:my-3 [&_ul]:my-3 [&_li]:my-1"
              dangerouslySetInnerHTML={{ __html: data.description }} />
          </div>
        )}

        {/* ===== 要求 ===== */}
        {data.requirement && (
          <div className="mt-6 rounded-2xl bg-card p-8 shadow-sm ring-1 ring-coal/5">
            <h2 className="mb-4 text-xl font-bold text-coal">任职要求</h2>
            <div className="prose max-w-none leading-8 text-coal/80 [&_p]:my-3 [&_ul]:my-3 [&_li]:my-1"
              dangerouslySetInnerHTML={{ __html: data.requirement }} />
          </div>
        )}
      </div>

      {/* ===== 投递 Modal ===== */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => setModalOpen(false)}>
          <div className="w-full max-w-md max-h-[calc(100vh-2rem)] overflow-y-auto rounded-2xl bg-card p-8" onClick={(e) => e.stopPropagation()}>
            {done ? (
              <div className="text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100 text-2xl text-green-600">✓</div>
                <h3 className="mt-4 text-lg font-semibold text-coal">投递成功</h3>
                <p className="mt-2 text-sm text-coal/60">您的简历已进入人才库，HR 将在 3-5 个工作日内联系您。</p>
                <button
                  onClick={() => setModalOpen(false)}
                  className="mt-6 w-full rounded-lg bg-walnut py-2.5 font-medium text-white hover:bg-walnut/90"
                >
                  完成
                </button>
              </div>
            ) : (
              <>
                <h3 className="text-lg font-semibold text-coal">投递岗位：{data.title}</h3>
                <p className="mt-1 text-sm text-coal/50">请填写联系信息</p>
                <div className="mt-6 space-y-4">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-coal">姓名 *</label>
                    <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                      placeholder="您的姓名"
                      className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-coal">手机号 *</label>
                    <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}
                      placeholder="11 位手机号"
                      className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-coal">邮箱</label>
                    <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                      placeholder="you@example.com"
                      className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut" />
                  </div>
                  <button
                    disabled={!canApply || applyMut.isPending}
                    onClick={() => applyMut.mutate()}
                    className="w-full rounded-lg bg-walnut py-3 font-medium text-white transition hover:bg-walnut/90 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {applyMut.isPending ? '提交中...' : '确认投递'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </article>
  )
}