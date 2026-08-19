interface FilterItem {
  key: string
  label: string
  count?: number
}

interface FilterGroup {
  name: string
  items: FilterItem[]
}

interface Props {
  groups: FilterGroup[]
  active: Record<string, string>
  onChange: (key: string, value: string) => void
}

/**
 * 三维筛选（系列 / 空间 / 品类）面板
 * 严格对齐 UI/UX §第八篇筛选规范
 */
export default function FilterPanel({ groups, active, onChange }: Props) {
  return (
    <aside className="bg-sand p-6 space-y-6">
      {groups.map((g) => (
        <div key={g.name}>
          <h3 className="font-display text-sm font-semibold text-ink mb-3 tracking-wide">{g.name}</h3>
          <ul className="space-y-2">
            <li>
              <button
                onClick={() => onChange(g.name, '')}
                className={`text-sm w-full text-left px-2 py-1 rounded transition-colors ${
                  !active[g.name]
                    ? 'bg-ink text-white'
                    : 'text-stone-600 hover:text-ink hover:bg-white'
                }`}
              >
                全部
              </button>
            </li>
            {g.items.map((it) => (
              <li key={it.key}>
                <button
                  onClick={() => onChange(g.name, it.key)}
                  className={`text-sm w-full text-left px-2 py-1 rounded flex items-center justify-between transition-colors ${
                    active[g.name] === it.key
                      ? 'bg-ink text-white'
                      : 'text-stone-600 hover:text-ink hover:bg-white'
                  }`}
                >
                  <span>{it.label}</span>
                  {it.count !== undefined && (
                    <span className="text-xs opacity-60">{it.count}</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </aside>
  )
}
