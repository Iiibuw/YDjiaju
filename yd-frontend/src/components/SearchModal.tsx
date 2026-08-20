/**
 * 站内搜索浮窗（UI 文档 §16.3：🔍 入口）。
 * 提交关键词跳转产品中心搜索；提供热门搜索标签与新闻/案例直达。
 */
import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

interface Props {
  open: boolean
  onClose: () => void
}

const HOT_WORDS = ['胡桃禮', '实木餐桌', '沙发', '餐边柜', '卧室']

export default function SearchModal({ open, onClose }: Props) {
  const [kw, setKw] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    if (open) {
      setKw('')
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  if (!open) return null

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    const q = kw.trim()
    onClose()
    if (q) navigate(`/products?keyword=${encodeURIComponent(q)}`)
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-start justify-center bg-ink/40 p-4 pt-24" onClick={onClose}>
      <div className="w-full max-w-xl max-h-[calc(100vh-2rem)] overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <form onSubmit={submit} className="flex gap-2">
          <input
            ref={inputRef}
            value={kw}
            onChange={(e) => setKw(e.target.value)}
            placeholder="搜索产品、新闻、案例…"
            className="input-yf"
          />
          <button type="submit" className="btn-gold shrink-0 px-5 py-2.5 text-sm">
            搜索
          </button>
        </form>

        <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
          <span className="text-stone-400">热门：</span>
          {HOT_WORDS.map((w) => (
            <button
              key={w}
              onClick={() => {
                onClose()
                navigate(`/products?keyword=${encodeURIComponent(w)}`)
              }}
              className="rounded-full border border-stone-200 px-3 py-1 text-stone-600 hover:border-gold hover:text-gold transition-colors"
            >
              {w}
            </button>
          ))}
        </div>

        <div className="mt-4 flex items-center justify-between border-t border-stone-100 pt-4 text-sm">
          <span className="text-stone-400">或直接浏览：</span>
          <div className="flex gap-4">
            <Link to="/news" onClick={onClose} className="text-stone-600 hover:text-gold">新闻资讯</Link>
            <Link to="/cases" onClick={onClose} className="text-stone-600 hover:text-gold">案例展示</Link>
            <Link to="/jobs" onClick={onClose} className="text-stone-600 hover:text-gold">人才招聘</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
