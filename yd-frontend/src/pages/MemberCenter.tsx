/** 会员中心：登录 / 注册 / 我的信息 + 我的订单 / 我的预约。 */
import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { memberLogin, memberRegister, type MemberOut } from '../api/members'
import { listMyAppointments, listMyOrders, fmtCents, ORDER_STATUS, APPT_STATUS, type AppointmentOut, type OrderOut } from '../api/orders'

const TOKEN_KEY = 'yd_member_token'

export function getMemberToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setMemberToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

interface LoginForm {
  phone: string
  password: string
}

interface RegisterForm {
  phone: string
  password: string
  nickname: string
}

export default function MemberCenter() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [member, setMember] = useState<MemberOut | null>(() => {
    const raw = localStorage.getItem('yd_member_info')
    return raw ? (JSON.parse(raw) as MemberOut) : null
  })
  const [loginForm, setLoginForm] = useState<LoginForm>({ phone: '', password: '' })
  const [regForm, setRegForm] = useState<RegisterForm>({ phone: '', password: '', nickname: '' })

  const loginMut = useMutation({
    mutationFn: (p: LoginForm) => memberLogin(p),
    onSuccess: (resp) => {
      setMemberToken(resp.access_token)
      localStorage.setItem('yd_member_info', JSON.stringify(resp.member))
      setMember(resp.member)
    },
    onError: (e) => alert(`登录失败：${(e as Error).message}`),
  })

  // 注册成功后自动登录
  const registerMut = useMutation({
    mutationFn: async (p: RegisterForm) => {
      await memberRegister({ phone: p.phone, password: p.password, nickname: p.nickname || null })
      return memberLogin({ phone: p.phone, password: p.password })
    },
    onSuccess: (resp) => {
      setMemberToken(resp.access_token)
      localStorage.setItem('yd_member_info', JSON.stringify(resp.member))
      setMember(resp.member)
    },
    onError: (e) => alert(`注册失败：${(e as Error).message}`),
  })

  const logout = () => {
    setMemberToken(null)
    localStorage.removeItem('yd_member_info')
    setMember(null)
    setMode('login')
  }

  // 已登录后拉取订单 + 预约（token 在 localStorage）
  const hasToken = !!getMemberToken()
  const { data: myOrders } = useQuery({
    queryKey: ['my-orders'],
    queryFn: () => listMyOrders(),
    enabled: hasToken && !!member,
  })
  const { data: myAppts } = useQuery({
    queryKey: ['my-appointments'],
    queryFn: () => listMyAppointments(),
    enabled: hasToken && !!member,
  })

  const orders: OrderOut[] = myOrders?.items ?? []
  const appointments: AppointmentOut[] = myAppts?.items ?? []

  const canLogin = /^1[3-9]\d{9}$/.test(loginForm.phone) && loginForm.password.length >= 6
  const canRegister = /^1[3-9]\d{9}$/.test(regForm.phone) && regForm.password.length >= 6

  // ===== 已登录视图 =====
  if (member) {
    return (
      <div className="bg-sand py-16">
        <div className="container-yf mx-auto max-w-3xl">
          <div className="rounded-2xl bg-white p-8 shadow-sm ring-1 ring-coal/5">
            <div className="flex items-center gap-6">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-walnut text-2xl font-bold text-white">
                {(member.nickname ?? member.phone).slice(0, 1)}
              </div>
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-coal">{member.nickname ?? '未设置昵称'}</h1>
                <p className="mt-1 text-sm text-coal/60">📱 {member.phone}</p>
              </div>
              <button onClick={logout} className="rounded-lg border border-coal/15 px-4 py-2 text-sm text-coal/70 hover:border-walnut hover:text-walnut">
                退出登录
              </button>
            </div>

            <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="rounded-xl bg-sand/60 p-5">
                <p className="text-2xl font-bold text-walnut">{orders.length}</p>
                <p className="mt-1 text-sm text-coal/60">我的订单</p>
              </div>
              <div className="rounded-xl bg-sand/60 p-5">
                <p className="text-2xl font-bold text-walnut">{appointments.length}</p>
                <p className="mt-1 text-sm text-coal/60">我的预约</p>
              </div>
              <div className="rounded-xl bg-sand/60 p-5">
                <p className="text-2xl font-bold text-walnut">{member.email ? '已绑定' : '未绑定'}</p>
                <p className="mt-1 text-sm text-coal/60">邮箱</p>
              </div>
            </div>

            {/* ===== 我的订单 ===== */}
            <div className="mt-8">
              <h3 className="mb-3 font-semibold text-coal">我的订单</h3>
              {orders.length === 0 ? (
                <div className="rounded-xl bg-sand/40 p-6 text-center text-sm text-coal/50">暂无订单，去「产品中心」看看吧</div>
              ) : (
                <div className="space-y-3">
                  {orders.map((o) => (
                    <div key={o.id} className="rounded-xl border border-coal/10 bg-white p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-coal">订单号：{o.order_no}</span>
                        <span className="rounded-full bg-walnut/10 px-2.5 py-0.5 text-xs text-walnut">
                          {ORDER_STATUS[o.status]?.label ?? o.status}
                        </span>
                      </div>
                      <div className="mt-3 flex items-center gap-3">
                        {o.items[0]?.cover_url && (
                          <img src={o.items[0].cover_url} alt="" className="h-12 w-12 rounded-lg object-cover" />
                        )}
                        <div className="flex-1 text-sm text-coal/70">
                          {o.items.map((it) => (
                            <div key={it.id}>{it.product_name} × {it.quantity}</div>
                          ))}
                        </div>
                        <div className="text-right">
                          <p className="font-medium text-walnut">{fmtCents(o.final_cents)}</p>
                          <p className="mt-1 text-xs text-coal/50">
                            {o.created_date ? new Date(o.created_date).toLocaleDateString('zh-CN') : ''}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* ===== 我的预约 ===== */}
            <div className="mt-8">
              <h3 className="mb-3 font-semibold text-coal">我的预约</h3>
              {appointments.length === 0 ? (
                <div className="rounded-xl bg-sand/40 p-6 text-center text-sm text-coal/50">暂无预约，点击顶部「预约到店」即可预约</div>
              ) : (
                <div className="space-y-3">
                  {appointments.map((a) => (
                    <div key={a.id} className="rounded-xl border border-coal/10 bg-white p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-coal">
                          {a.type === 'visit' ? '到店参观' : a.type === 'consult' ? '方案咨询' : a.type === 'custom' ? '定制服务' : '其他'}
                        </span>
                        <span className="rounded-full bg-walnut/10 px-2.5 py-0.5 text-xs text-walnut">
                          {APPT_STATUS[a.status]?.label ?? a.status}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-coal/60">
                        {a.preferred_date ? `期望时间：${new Date(a.preferred_date).toLocaleString('zh-CN')}` : '时间待确认'}
                      </p>
                      {a.message && <p className="mt-1 text-sm text-coal/50">需求：{a.message}</p>}
                      {a.follow_note && (
                        <p className="mt-2 rounded bg-green-50 px-2 py-1 text-xs text-green-700">跟进：{a.follow_note}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-8 rounded-xl bg-walnut/5 p-6">
              <h3 className="font-semibold text-coal">注册信息</h3>
              <p className="mt-3 text-sm text-coal/70">
                注册时间：{member.created_date ? new Date(member.created_date).toLocaleDateString('zh-CN') : '-'}
              </p>
              <p className="mt-2 text-sm text-coal/70">
                最近登录：{member.last_login_date ? new Date(member.last_login_date).toLocaleString('zh-CN') : '-'}
              </p>
            </div>

            <div className="mt-6 text-center text-sm text-coal/50">
              下单、预约功能已上线，欢迎体验。
            </div>
          </div>
        </div>
      </div>
    )
  }

  // ===== 登录/注册视图 =====
  return (
    <div className="bg-sand py-16">
      <div className="container-yf mx-auto max-w-md">
        <div className="rounded-2xl bg-white p-8 shadow-sm ring-1 ring-coal/5">
          <div className="flex rounded-lg bg-sand p-1">
            {(['login', 'register'] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 rounded-md py-2 text-sm font-medium transition ${
                  mode === m ? 'bg-white text-walnut shadow-sm' : 'text-coal/60'
                }`}
              >
                {m === 'login' ? '登录' : '注册'}
              </button>
            ))}
          </div>

          {mode === 'login' ? (
            <div className="mt-8 space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">手机号</label>
                <input
                  value={loginForm.phone}
                  onChange={(e) => setLoginForm({ ...loginForm, phone: e.target.value })}
                  placeholder="11 位手机号"
                  className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">密码</label>
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  placeholder="≥6 位"
                  className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                />
              </div>
              <button
                disabled={!canLogin || loginMut.isPending}
                onClick={() => loginMut.mutate(loginForm)}
                className="w-full rounded-lg bg-walnut py-3 font-medium text-white transition hover:bg-walnut/90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loginMut.isPending ? '登录中...' : '登录'}
              </button>
              <p className="text-center text-xs text-coal/50">演示账号：13800138001 / member123</p>
            </div>
          ) : (
            <div className="mt-8 space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">手机号</label>
                <input
                  value={regForm.phone}
                  onChange={(e) => setRegForm({ ...regForm, phone: e.target.value })}
                  placeholder="11 位手机号"
                  className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">密码</label>
                <input
                  type="password"
                  value={regForm.password}
                  onChange={(e) => setRegForm({ ...regForm, password: e.target.value })}
                  placeholder="≥6 位"
                  className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-coal">昵称</label>
                <input
                  value={regForm.nickname}
                  onChange={(e) => setRegForm({ ...regForm, nickname: e.target.value })}
                  placeholder="选填"
                  className="w-full rounded-lg border border-coal/15 px-4 py-2.5 outline-none focus:border-walnut"
                />
              </div>
              <button
                disabled={!canRegister || registerMut.isPending}
                onClick={() => registerMut.mutate(regForm)}
                className="w-full rounded-lg bg-walnut py-3 font-medium text-white transition hover:bg-walnut/90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {registerMut.isPending ? '注册中...' : '注册并登录'}
              </button>
            </div>
          )}
        </div>
        <p className="mt-6 text-center text-sm text-coal/50">
          遇到问题？<Link to="/contact" className="text-walnut hover:underline">联系我们</Link>
        </p>
      </div>
    </div>
  )
}