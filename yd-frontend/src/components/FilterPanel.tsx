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
 * 三维筛选（空间 / 系列 / 品类）面板
 * - 白底，无大块黑色色块
 * - 选中：文字加粗 + 主色（黑胡桃）+ 底部短下划线
 * - 未选中：浅灰普通字重，无背景
 * - 分组标题加粗，字号大，与下方选项拉开更大间距
 */
export default function FilterPanel({ groups, active, onChange }: Props) {
  return (
    <aside className="bg-white p-6 space-y-8">
      {groups.map((g) => (
        <div key={g.name}>
          <h3 className="mb-4 border-b border-stone-100 pb-2 text-base font-bold tracking-wide text-stone-800">
            {g.name}
          </h3>
          <ul className="space-y-3">
            <li>
              <button
                onClick={() => onChange(g.name, '')}
                className={`relative w-full text-left text-sm transition-colors ${
                  !active[g.name]
                    ? 'font-semibold text-walnut'
                    : 'font-normal text-stone-500 hover:text-stone-800'
                }`}
              >
                全部
                {!active[g.name] && (
                  <span className="absolute -bottom-1 left-0 h-0.5 w-4 rounded-full bg-walnut" />
                )}
              </button>
            </li>
            {g.items.map((it) => {
              const isActive = active[g.name] === it.key
              return (
                <li key={it.key}>
                  <button
                    onClick={() => onChange(g.name, it.key)}
                    className={`relative w-full text-left text-sm transition-colors ${
                      isActive
                        ? 'font-semibold text-walnut'
                        : 'font-normal text-stone-500 hover:text-stone-800'
                    }`}
                  >
                    <span className="flex items-center justify-between">
                      <span>{it.label}</span>
                      {it.count !== undefined && (
                        <span className="text-xs text-stone-400">{it.count}</span>
                      )}
                    </span>
                    {isActive && (
                      <span className="absolute -bottom-1 left-0 h-0.5 w-4 rounded-full bg-walnut" />
                    )}
                  </button>
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </aside>
  )
}