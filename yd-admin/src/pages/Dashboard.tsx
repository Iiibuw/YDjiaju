/**
 * 后台仪表盘（24 栅格固定布局）：
 * - 顶部 4 张数据卡等宽(span 6)等高
 * - 中间 3 张图表卡(10/8/6)，图表固定高度不拉伸
 * - 右侧订单占比卡正方形，环形图保持正圆
 * - 底部待办/最新会员等高，内容超出内部滚动
 * 间距统一 16px，全部由 Row/Col 栅格管理，无绝对定位。
 */
import { useEffect, useMemo, useRef } from 'react'
import { Card, Col, List, Row, Space, Tag } from 'antd'
import {
  FileTextOutlined,
  CalendarOutlined,
  TeamOutlined,
  ShoppingCartOutlined,
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

// ============ ECharts 通用 hook（本地 vendor，X 轴类目标签独立分行） ============
declare global {
  interface Window {
    echarts?: any
  }
}

function useECharts(option: any, deps: unknown[]) {
  const ref = useRef<HTMLDivElement>(null)
  const chartRef = useRef<any>(null)
  useEffect(() => {
    const el = ref.current
    if (!el || !window.echarts) return
    if (!chartRef.current) {
      chartRef.current = window.echarts.init(el)
    }
    chartRef.current.setOption(option, true)
    const onResize = () => chartRef.current?.resize()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
  useEffect(() => {
    return () => {
      chartRef.current?.dispose()
      chartRef.current = null
    }
  }, [])
  return ref
}

/** 统一 X 轴配置：interval:0 全显示 + rotate:0 + lineHeight:16 支持换行 */
const xAxisCommon = (categories: string[]) => ({
  type: 'category' as const,
  data: categories,
  boundaryGap: false,
  axisLabel: {
    interval: 0,
    rotate: 0,
    lineHeight: 16,
    color: '#6b7280',
    fontSize: 11,
    formatter: (v: string) => v,
  },
  axisLine: { lineStyle: { color: '#e5e7eb' } },
  axisTick: { show: false },
})

const gridCommon = { left: 4, right: 8, top: 24, bottom: 32, containLabel: true }

// ============ ECharts 折线图（预约趋势） ============
function EChartLine({
  categories,
  data,
  color = '#fa8c16',
}: {
  categories: string[]
  data: number[]
  color?: string
}) {
  const ref = useECharts(
    {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any[]) => {
          const p = params[0]
          return `${p.axisValue}　预约 ${p.value} 条`
        },
      },
      grid: gridCommon,
      xAxis: xAxisCommon(categories),
      yAxis: {
        type: 'value',
        minInterval: 1,
        axisLabel: { color: '#9ca3af', fontSize: 11 },
        splitLine: { lineStyle: { color: '#f3f4f6' } },
      },
      series: [
        {
          name: '预约',
          type: 'line',
          data,
          smooth: true,
          symbolSize: 6,
          lineStyle: { width: 2.5, color },
          itemStyle: { color },
          areaStyle: { color, opacity: 0.12 },
        },
      ],
    },
    [categories.join('|'), data.join('|'), color],
  )
  return <div ref={ref} className="w-full" style={{ height: 180 }} />
}

// ============ ECharts 柱状图（资讯趋势） ============
function EChartBar({
  categories,
  data,
  color = '#1677ff',
}: {
  categories: string[]
  data: number[]
  color?: string
}) {
  const ref = useECharts(
    {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any[]) => {
          const p = params[0]
          return `${p.axisValue}　发布 ${p.value} 篇`
        },
      },
      grid: gridCommon,
      xAxis: xAxisCommon(categories),
      yAxis: {
        type: 'value',
        minInterval: 1,
        axisLabel: { color: '#9ca3af', fontSize: 11 },
        splitLine: { lineStyle: { color: '#f3f4f6' } },
      },
      series: [
        {
          name: '资讯',
          type: 'bar',
          data,
          barWidth: '45%',
          itemStyle: { color, borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top', color: '#8c8c8c', fontSize: 11 },
        },
      ],
    },
    [categories.join('|'), data.join('|'), color],
  )
  return <div ref={ref} className="w-full" style={{ height: 180 }} />
}

// ============ 环形占比图（正方形容器，正圆） ============
function DonutChart({ data }: { data: { label: string; value: number; color: string }[] }) {
  const total = data.reduce((s, d) => s + d.value, 0) || 1
  const R = 54
  const C = 2 * Math.PI * R
  let offset = 0
  return (
    <div className="flex flex-col items-center justify-center gap-3" style={{ height: 220 }}>
      <div className="relative" style={{ width: 140, height: 140 }}>
        <svg viewBox="0 0 140 140" className="h-full w-full">
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
              />
            )
            offset += len
            return el
          })}
          <text x="70" y="66" textAnchor="middle" fontSize="22" fontWeight="700" fill="#333">
            {data.reduce((s, d) => s + d.value, 0)}
          </text>
          <text x="70" y="84" textAnchor="middle" fontSize="11" fill="#999">
            订单总数
          </text>
        </svg>
      </div>
      <div className="flex flex-col gap-1.5">
        {data.map((d, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span className="h-2.5 w-2.5 shrink-0 rounded-sm" style={{ backgroundColor: d.color }} />
            <span className="text-gray-600">{d.label}</span>
            <b className="text-gray-800">{d.value}</b>
          </div>
        ))}
      </div>
    </div>
  )
}

// ============ 主页面（24 栅格） ============
export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: fetchDashboardStats,
    staleTime: 60_000,
    refetchInterval: 120_000,
  })

  const c = data?.counts
  const todos = data?.todos

  // 顶部 4 张数据卡（等宽 span=6）
  const cards = useMemo(
    () => [
      { key: 'news', label: '总资讯数', value: c?.news ?? 0, icon: <FileTextOutlined />, color: '#1677ff', link: '/news' },
      { key: 'appts', label: '今日预约', value: c?.appointments ?? 0, icon: <CalendarOutlined />, color: '#fa8c16', link: '/appointments' },
      { key: 'members', label: '会员总数', value: c?.members ?? 0, icon: <TeamOutlined />, color: '#52c41a', link: '/members' },
      { key: 'orders', label: '订单总数', value: c?.orders ?? 0, icon: <ShoppingCartOutlined />, color: '#722ed1', link: '/orders' },
    ],
    [c],
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

  const dayLabels = (data?.days ?? []).map((d) => {
    const m = d.slice(5) // "08-15"
    return m.replace('-', '/').replace(/^0/, '') // "8/15"
  })
  const dateRangeLabel = data?.days?.length
    ? `${data.days[0].slice(5)} - ${data.days[data.days.length - 1].slice(5)}`.replace(/-/g, '/').replace(/^0(\d)/gm, '$1')
    : ''

  return (
    <div className="flex flex-col gap-4">
      {/* ===== 顶部 4 数据卡（24 栅格，等宽等高） ===== */}
      <Row gutter={[16, 16]}>
        {cards.map((card) => (
          <Col xs={24} sm={12} lg={6} key={card.key}>
            <Link to={card.link}>
              <Card
                className="!rounded-xl !shadow-sm transition-shadow hover:!shadow-md"
                styles={{ body: { padding: 16 } }}
              >
                <div className="flex items-center gap-3" style={{ height: 56 }}>
                  <div
                    className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl text-xl"
                    style={{ backgroundColor: `${card.color}14`, color: card.color }}
                  >
                    {card.icon}
                  </div>
                  <div className="min-w-0">
                    <div className="truncate text-xs text-gray-500">{card.label}</div>
                    <div className="text-2xl font-bold leading-tight" style={{ color: '#1f1f1f' }}>
                      {card.value}
                    </div>
                  </div>
                </div>
              </Card>
            </Link>
          </Col>
        ))}
      </Row>

      {/* ===== 中间图表区（10/8/6 栅格，统一间距） ===== */}
      <Row gutter={[16, 16]}>
        {/* 近7天预约趋势 */}
        <Col xs={24} lg={10}>
          <Card
            title="最近 7 天预约趋势"
            className="!rounded-xl !shadow-sm"
            extra={(
              <Space size={4}>
                {dateRangeLabel && <span className="text-xs text-gray-400 font-mono">{dateRangeLabel}</span>}
                <Tag color="orange"><CalendarOutlined /> 预约</Tag>
              </Space>
            )}
            loading={isLoading}
            styles={{ body: { padding: 12 } }}
          >
            <EChartLine categories={dayLabels} data={data?.appointments ?? []} color="#fa8c16" />

          </Card>
        </Col>
        {/* 资讯发布趋势 */}
        <Col xs={24} lg={8}>
          <Card
            title="资讯发布趋势"
            className="!rounded-xl !shadow-sm"
            extra={(
              <Space size={4}>
                {dateRangeLabel && <span className="text-xs text-gray-400 font-mono">{dateRangeLabel}</span>}
                <Tag color="blue"><FileTextOutlined /> 近 7 日</Tag>
              </Space>
            )}
            loading={isLoading}
            styles={{ body: { padding: 12 } }}
          >
            <EChartBar categories={dayLabels} data={data?.news_trend ?? []} color="#1677ff" />

          </Card>
        </Col>
        {/* 订单状态占比（正方形容器 + 正圆） */}
        <Col xs={24} lg={6}>
          <Card
            title="订单状态占比"
            className="!rounded-xl !shadow-sm"
            loading={isLoading}
            styles={{ body: { padding: 12 } }}
          >
            <DonutChart data={donutData} />
          </Card>
        </Col>
      </Row>

      {/* ===== 底部列表区（8/16 栅格，等高，内部滚动） ===== */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card
            title="待处理事项"
            className="!rounded-xl !shadow-sm"
            extra={<Link to="/news" className="text-xs text-gray-400">全部 →</Link>}
            styles={{ body: { padding: 12, height: 240, overflowY: 'auto' } }}
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
                    <span className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: it.color }} />
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
            styles={{ body: { padding: 12, height: 240, overflowY: 'auto' } }}
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
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-50 text-xs font-semibold text-blue-500">
                      {(m.nickname || m.phone || '?').slice(0, 1)}
                    </span>
                    <span className="truncate text-sm text-gray-700">{m.nickname || '未设置昵称'}</span>
                    <span className="hidden text-xs text-gray-400 sm:inline">{m.phone}</span>
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