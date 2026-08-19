/** 会员中心：登录 / 注册 / 我的信息（接 /members 系列 API）。 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { memberLogin, memberRegister, type MemberOut } from '../api/members'

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
                <p className="text-2xl font-bold text-walnut">0</p>
                <p className="mt-1 text-sm text-coal/60">我的订单</p>
              </div>
              <div className="rounded-xl bg-sand/60 p-5">
                <p className="text-2xl font-bold text-walnut">0</p>
                <p className="mt-1 text-sm text-coal/60">我的预约</p>
              </div>
              <div className="rounded-xl bg-sand/60 p-5">
                <p className="text-2xl font-bold text-walnut">{member.email ? '已绑定' : '未绑定'}</p>
                <p className="mt-1 text-sm text-coal/60">邮箱</p>
              </div>
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
              订单 / 预约功能将在 M2-3 阶段上线，敬请期待。
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