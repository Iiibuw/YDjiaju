/** 下载中心（阶段 4：对接 /public/downloads，分类切换 + 下载计数）。 */
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { listDownloads, type Download } from '../api/downloads'
import { useToastStore } from '../store/toast'

const CATS = [
  { key: '', label: '全部' },
  { key: 'catalog', label: '产品手册' },
  { key: 'manual', label: '使用说明' },
  { key: 'cad', label: 'CAD 图纸' },
  { key: 'other', label: '其他资料' },
]

function fmtSize(kb: number | null): string {
  if (!kb) return ''
  return kb >= 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb} KB`
}

export default function Downloads() {
  const [cat, setCat] = useState('')
  const toast = useToastStore((s) => s.push)

  const { data, isLoading } = useQuery({
    queryKey: ['downloads', cat],
    queryFn: () => listDownloads({ category: cat || undefined, page_size: 50 }),
  })
  const items: Download[] = data?.items ?? []

  const onDownload = (d: Download) => {
    if (d.file_url) window.open(d.file_url, '_blank', 'noopener')
    toast(`开始下载《${d.title}》`, 'success')
  }

  return (
    <div className="container-yf py-16">
      <h1 className="font-display text-4xl font-medium text-ink">下载中心</h1>
      <p className="mt-2 text-stone-500">产品手册、使用说明、CAD 图纸等资料下载</p>

      {/* 分类切换 */}
      <div className="mt-6 flex flex-wrap gap-2">
        {CATS.map((c) => (
          <button
            key={c.key}
            onClick={() => setCat(c.key)}
            className={`rounded-full px-4 py-1.5 text-sm transition-colors ${
              cat === c.key ? 'bg-ink text-white' : 'border border-stone-200 text-stone-600 hover:border-gold hover:text-gold'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* 列表 */}
      <div className="mt-8 space-y-3">
        {isLoading &&
          Array.from({ length: 4 }).map((_, i) => <div key={i} className="card-yf h-20 animate-pulse" />)}

        {!isLoading && items.length === 0 && (
          <div className="card-yf flex h-40 flex-col items-center justify-center text-stone-400">
            <span className="text-3xl">📥</span>
            <p className="mt-2 text-sm">该分类下暂无资料</p>
          </div>
        )}

        {items.map((d) => (
          <div key={d.id} className="card-yf flex items-center justify-between gap-4 p-5">
            <div className="min-w-0">
              <h3 className="truncate font-medium text-ink">{d.title}</h3>
              {d.description && <p className="mt-1 line-clamp-1 text-sm text-stone-500">{d.description}</p>}
              <p className="mt-2 text-xs text-stone-400">
                {(d.file_format ?? 'file').toUpperCase()} · {fmtSize(d.file_size_kb)} · 已下载 {d.download_count} 次
              </p>
            </div>
            <button onClick={() => onDownload(d)} className="btn-outline shrink-0 px-5 py-2 text-sm">
              下载
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
