/** Toast 渲染组件（挂在 MainLayout 全局）。 */
import { useToastStore } from '../store/toast'

export default function Toast() {
  const toasts = useToastStore((s) => s.toasts)
  const dismiss = useToastStore((s) => s.dismiss)
  if (toasts.length === 0) return null
  return (
    <div className="fixed left-1/2 bottom-10 z-[70] flex -translate-x-1/2 flex-col items-center gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          onClick={() => dismiss(t.id)}
          className={`cursor-pointer rounded-lg px-4 py-2 text-sm text-white shadow-lg transition-all ${
            t.type === 'error' ? 'bg-red-500' : t.type === 'success' ? 'bg-green-600' : 'bg-ink/90'
          }`}
        >
          {t.text}
        </div>
      ))}
    </div>
  )
}
