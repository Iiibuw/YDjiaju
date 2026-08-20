/**
 * 购物车 store（zustand + localStorage 持久化，key=yd_cart 对齐 UI 文档 §18.2）。
 * 结算页/我的订单在阶段 5（M6）接入，本阶段提供 add/remove/updateQty 与 badge 计数。
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface CartItem {
  id: number
  name: string
  priceCents: number
  cover: string | null
  qty: number
  spec?: string
}

interface CartState {
  items: CartItem[]
  /** 加入购物车：已存在则累加数量。 */
  add: (item: Omit<CartItem, 'qty'> & { qty?: number }) => void
  remove: (id: number) => void
  updateQty: (id: number, qty: number) => void
  clear: () => void
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      add: (item) => {
        const items = get().items
        const existing = items.find((i) => i.id === item.id)
        if (existing) {
          set({ items: items.map((i) => (i.id === item.id ? { ...i, qty: i.qty + (item.qty ?? 1) } : i)) })
        } else {
          set({ items: [...items, { ...item, qty: item.qty ?? 1 }] })
        }
      },
      remove: (id) => set({ items: get().items.filter((i) => i.id !== id) }),
      updateQty: (id, qty) =>
        set({ items: get().items.map((i) => (i.id === id ? { ...i, qty: Math.max(1, qty) } : i)) }),
      clear: () => set({ items: [] }),
    }),
    { name: 'yd_cart' },
  ),
)

/** 购物车徽标数量与合计（供 NavBar/CartDrawer 使用）。 */
export function useCartCount(): number {
  return useCartStore((s) => s.items.reduce((sum, i) => sum + i.qty, 0))
}

export function useCartTotal(): number {
  return useCartStore((s) => s.items.reduce((sum, i) => sum + i.priceCents * i.qty, 0))
}
