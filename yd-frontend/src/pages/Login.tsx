/** 会员登录/注册页（阶段 5：真实对接 /members/login、/members/register）。 */
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'

import { memberLogin, memberRegister } from '../api/members'
import { useToastStore } from '../store/toast'

const TOKEN_KEY = 'yd_member_token'

export default function Login() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [form, setForm] = useState({ phone: '', password: '', nickname: '' })
  const navigate = useNavigate()
  const toast = useToastStore((s) => s.push)

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }))

  const mut = useMutation({
    mutationFn: async () => {
      if (mode === 'register') {
        await memberRegister({ phone: form.phone, password: form.password, nickname: form.nickname || null })
      }
      return memberLogin({ phone: form.phone, password: form.password })
    },
    onSuccess: (resp) => {
      localStorage.setItem(TOKEN_KEY, resp.access_token)
      localStorage.setItem('yd_member_info', JSON.stringify(resp.member))
      toast(`${mode === 'login' ? '登录' : '注册并登录'}成功，欢迎 ${resp.member.nickname ?? resp.member.phone}`, 'success')
      navigate('/member')
    },
    onError: (e) => toast(`失败：${(e as Error).message}`, 'error'),
  })

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!/^1[3-9]\d{9}$/.test(form.phone)) return toast('请输入 11 位有效手机号', 'error')
    if (form.password.length < 6) return toast('密码至少 6 位', 'error')
    mut.mutate()
  }

  return (
    <div className="container-yf flex justify-center py-16">
      <div className="card-yf w-full max-w-md p-8">
        <div className="flex items-center justify-between">
          <h1 className="font-display text-2xl font-medium text-ink">
            {mode === 'login' ? '会员登录' : '注册新会员'}
          </h1>
          <button
            onClick={() => setMode((m) => (m === 'login' ? 'register' : 'login'))}
            className="text-sm text-gold hover:underline"
          >
            {mode === 'login' ? '没有账号？去注册' : '已有账号？去登录'}
          </button>
        </div>

        <form onSubmit={submit} className="mt-6 space-y-4">
          <input value={form.phone} onChange={set('phone')} placeholder="手机号" className="input-yf" inputMode="numeric" />
          <input value={form.password} onChange={set('password')} type="password" placeholder="密码（至少 6 位）" className="input-yf" />
          {mode === 'register' && (
            <input value={form.nickname} onChange={set('nickname')} placeholder="昵称（可选）" className="input-yf" />
          )}
          <button type="submit" disabled={mut.isPending} className="btn-gold w-full py-3 disabled:opacity-60">
            {mut.isPending ? '提交中…' : mode === 'login' ? '登录' : '注册'}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-stone-400">
          登录后可在「会员中心」查看我的订单 / 预约 / 投递
        </p>
        <p className="mt-2 text-center text-sm">
          <Link to="/" className="text-stone-500 hover:text-gold">返回首页</Link>
        </p>
      </div>
    </div>
  )
}
