/** 后台仪表盘：数据卡片 + 趋势图 + 订单占比 + 待办事项。 */
import { useMemo } from 'react'
import { Card, Col, List, Row, Tag } from 'antd'
import {
  FileTextOutlined,
  CalendarOutlined,
  TeamOutlined,
  ShoppingCartOutlined,
  MessageOutlined,
  RightOutlined,
} from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { fetchDashboardStats } from '../api/dashboard'

const ORDER_STATUS_LABELS: Record<string, string> = {
  pending: '待付款',
  paid: '已付款',
  shipped: '已发货',
  completed: '已完成',
  refunding: '退款中',
  refunded: '已退款',
  closed: '已关闭',
}

// ============ 迷你折线图（SVG） ============
function MiniLineChart({ data, color = '#1677ff' }: { data: number[]; color?: string }) {
  const W = 320
  const H = 110
  const pad = 8
  const max = Math.max(...data, 1)
  const step = (W - pad * 2) / Math.max(data.length - 1, 1)
  const pts = data.map((v, i) => [
    pad + i * step,
    H - pad - ((H - pad * 2) * v) / max,
  ])
  const path = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0]},${p[1]}`).join(' ')
  const area = `${path} L${pts[pts.length - 1][0]},${H - pad} L${pts[0][0]},${H - pad} Z`
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: 110 }}>
      <defs>
        <linearGradient id={`grad-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#grad-${color.replace('#', '')})`} />
      <path d={path} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      {pts.map((p, i) => (
        <circle key={i} cx={p[0]} cy={p[1]} r="3" fill="#fff" stroke={color} strokeWidth="1.5" />
      ))}
    </svg>
  )
}

// ============ 迷你柱状图（SVG） ============
function MiniBarChart({ data, color = '#52c41a' }: { data: number[]; color?: string }) {
  const W = 320
  const H = 110
  const pad = 8
  const max = Math.max(...data, 1)
  const bw = (W - pad * 2) / data.length
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: 110 }}>
      {data.map((v, i) => {
        const h = ((H - pad * 2) * v) / max
        return (
          <g key={i}>
            <rect
              x={pad + i * bw + bw * 0.2}
              y={H - pad - h}
              width={bw * 0.6}
              height={Math.max(h, 1)}
              rx="3"
              fill={color}
              opacity="0.85"
            />
            <text
              x={pad + i * bw + bw / 2}
              y={H - pad - h - 4}
              textAnchor="middle"
              fontSize="10"
              fill="#8c8c8c"
            >
              {v}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

// ============ 环形占比图（SVG） ============
function DonutChart({ data }: { data: { label: string; value: number; color: string }[] }) {
  const total = data.reduce((s, d) => s + d.value, 0) || 1
  const R = 54
  const C = 2 * Math.PI * R
  let offset = 0
  return (
    <div className="flex items-center gap-4">
      <svg viewBox="0 0 140 140" className="h-32 w-32 shrink-0">
        <circle cx="70" cy="70" r={R} fill="none" stroke="#f0f0f0" strokeWidth="14" />
        {data.map((d, i) => {
          const frac = d.value / total
          const len = frac * C
          const el = (
            <circle
              key={i}
              cx="70"
              cy="70"
              r={R}
              fill="none"
              stroke={d.color}
              strokeWidth="14"
              strokeDasharray={`${len} ${C - len}`}
              strokeDashoffset={-offset}
              transform="rotate(-90 70 70)"
              strokeLinecap="butt"
            />
          )
          offset += len
          return el
        })}
        <text x="70" y="66" textAnchor="middle" fontSize="20" fontWeight="700" fill="#333">
          {data.reduce((s, d) => s + d.value, 0)}
        </text>
        <text x="70" y="84" textAnchor="middle" fontSize="11" fill="#999">
          订单总数
        </text>
      </svg>
      <div className="flex flex-col gap-1.5">
        {data.map((d, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: d.color }} />
            <span className="text-gray-600">{d.label}</span>
            <b className="text-gray-800">{d.value}</b>
          </div>
        ))}
      </div>
    </div>
  )
}

// ============ 主页面 ============
export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: fetchDashboardStats,
    staleTime: 60_000,
    refetchInterval: 120_000, // 2 分钟自动刷新
  })

  const c = data?.counts
  const todos = data?.todos

  const cards = useMemo(
    () => [
      { key: 'news', label: '总资讯数', value: c?.news ?? 0, icon: <FileTextOutlined />, color: '#1677ff', link: '/news' },
      { key: 'appts', label: '今日预约', value: c?.appointments ?? 0, icon: <CalendarOutlined />, color: '#fa8c16', link: '/appointments' },
      { key: 'members', label: '会员总数', value: c?.members ?? 0, icon: <TeamOutlined />, color: '#52c41a', link: '/members' },
      { key: 'orders', label: '订单总数', value: c?.orders ?? 0, icon: <ShoppingCartOutlined />, color: '#722ed1', link: '/orders' },
      { key: 'messages', label: '留言待处理', value: todos?.pending_messages ?? 0, icon: <MessageOutlined />, color: '#eb2f96', link: '/messages' },
    ],
    [c, todos],
  )

  const donutData = (data?.order_status_dist ?? []).map((d, i) => ({
    label: ORDER_STATUS_LABELS[d.status] ?? d.status,
    value: d.count,
    color: ['#1677ff', '#52c41a', '#fa8c16', '#eb2f96', '#722ed1', '#13c2c2', '#8c8c8c'][i % 7],
  }))

  const todoItems = [
    { label: '待审核资讯', value: todos?.draft_news ?? 0, link: '/news', color: '#1677ff' },
    { label: '待处理预约', value: todos?.pending_appointments ?? 0, link: '/appointments', color: '#fa8c16' },
    { label: '待回复留言', value: todos?.pending_messages ?? 0, link: '/messages', color: '#eb2f96' },
  ]

  const dayLabels = (data?.days ?? []).map((d) => d.slice(5))

  return (
    <div className="flex flex-col gap-4">
      {/* ===== 顶部数据卡片 ===== */}
      <Row gutter={[16, 16]}>
        {cards.map((card) => (
          <Col xs={24} sm={12} md={8} lg={4} key={card.key}>
            <Link to={card.link}>
              <Card
                className="!rounded-xl !shadow-sm transition-shadow hover:!shadow-md"
                styles={{ body: { padding: 16 } }}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-lg"
                    style={{ backgroundColor: `${card.color}14`, color: card.color }}
                  >
                    {card.icon}
                  </div>
                  <div className="min-w-0">
                    <div className="truncate text-xs text-gray-500">{card.label}</div>
                    <div className="text-2xl font-bold" style={{ color: '#1f1f1f' }}>
                      {card.value}
                    </div>
                  </div>
                </div>
              </Card>
            </Link>
          </Col>
        ))}
      </Row>

      {/* ===== 中间图表 ===== */}
      <Row gutter={[16, 16]}>
        {/* 近7天预约趋势 */}
        <Col xs={24} lg={10}>
          <Card
            title="最近 7 天预约趋势"
            className="!rounded-xl !shadow-sm"
            extra={<Tag color="orange"><CalendarOutlined /> 预约</Tag>}
            loading={isLoading}
          >
            <MiniLineChart data={data?.appointments ?? []} color="#fa8c16" />
            <div className="mt-1 flex justify-between px-1 text-[10px] text-gray-400">
              {dayLabels.map((d, i) => <span key={i}>{d}</span>)}
            </div>
          </Card>
        </Col>
        {/* 资讯发布趋势 */}
        <Col xs={24} lg={8}>
          <Card
            title="资讯发布趋势"
            className="!rounded-xl !shadow-sm"
            extra={<Tag color="blue"><FileTextOutlined /> 近 7 日</Tag>}
            loading={isLoading}
          >
            <MiniBarChart data={data?.news_trend ?? []} color="#1677ff" />
            <div className="mt-1 flex justify-between px-1 text-[10px] text-gray-400">
              {dayLabels.map((d, i) => <span key={i}>{d}</span>)}
            </div>
          </Card>
        </Col>
        {/* 订单状态占比 */}
        <Col xs={24} lg={6}>
          <Card title="订单状态占比" className="!rounded-xl !shadow-sm" loading={isLoading}>
            <DonutChart data={donutData} />
          </Card>
        </Col>
      </Row>

      {/* ===== 底部待办事项 ===== */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card
            title="待处理事项"
            className="!rounded-xl !shadow-sm"
            extra={<Link to="/news" className="text-xs text-gray-400">全部 →</Link>}
          >
            <List
              size="small"
              dataSource={todoItems}
              renderItem={(it) => (
                <List.Item
                  extra={
                    <Link to={it.link}>
                      <span className="flex items-center gap-1 text-xs text-gray-400 hover:text-blue-500">
                        去处理 <RightOutlined style={{ fontSize: 10 }} />
                      </span>
                    </Link>
                  }
                >
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: it.color }} />
                    <span className="text-sm text-gray-700">{it.label}</span>
                    {it.value > 0 && <Tag color="red">{it.value}</Tag>}
                  </span>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card
            title="最新会员"
            className="!rounded-xl !shadow-sm"
            extra={<Link to="/members" className="text-xs text-gray-400">全部 →</Link>}
          >
            <List
              size="small"
              dataSource={todos?.latest_members ?? []}
              renderItem={(m) => (
                <List.Item
                  extra={
                    <span className="text-xs text-gray-400">
                      {m.created_date ? new Date(m.created_date).toLocaleDateString('zh-CN') : ''}
                    </span>
                  }
                >
                  <span className="flex items-center gap-2">
                    <span className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-50 text-xs font-semibold text-blue-500">
                      {(m.nickname || m.phone || '?').slice(0, 1)}
                    </span>
                    <span className="text-sm text-gray-700">{m.nickname || '未设置昵称'}</span>
                    <span className="text-xs text-gray-400">{m.phone}</span>
                  </span>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}