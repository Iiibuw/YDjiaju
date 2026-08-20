/**
 * Toast 轻提示（UI 文档 §10.4：fixed bottom center，2.2s 自动消失）。
 * 任意组件调用 useToastStore.getState().push('文案', 'success'|'error'|'info')。
 */
import { create } from 'zustand'

export interface ToastMsg {
  id: number
  text: string
  type: 'success' | 'error' | 'info'
}

interface ToastState {
  toasts: ToastMsg[]
  push: (text: string, type?: ToastMsg['type']) => void
  dismiss: (id: number) => void
}

let seq = 0

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  push: (text, type = 'info') => {
    const id = ++seq
    set((s) => ({ toasts: [...s.toasts, { id, text, type }] }))
    setTimeout(() => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), 2200)
  },
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))
