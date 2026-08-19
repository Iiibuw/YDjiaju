/** 在线客服悬浮窗：关键词回复机器人（纯前端）。 */
import { useState } from 'react'

const QUICK_QUESTIONS = ['怎么预约到店？', '胡桃禮系列有哪些产品？', '售后服务怎么联系？']

interface ChatMsg {
  from: 'bot' | 'user'
  text: string
}

function botAnswer(text: string): string {
  const t = text.trim()
  if (!t) return '您好，请问有什么可以帮您？'
  if (/预约|到店|门店|体验/.test(t)) {
    return '您可以点击页面任意「预约到店」按钮，或拨打 400-800-1953，我们的专属顾问会为您安排到店体验与免费量尺。'
  }
  if (/胡桃禮|胡桃/.test(t)) {
    return '胡桃禮系列是我们的明星系列，采用北美 FAS 级黑胡桃木，主打现代简约风格。您可以到「产品中心」查看餐桌、餐边柜、床品等，或预约到店体验。'
  }
  if (/售后|保修|维修|客服/.test(t)) {
    return 'YD 家具提供 5 年结构保修 + 终身维护。您可拨打 400-800-1953 或到「售后服务」页面查看常见问题，我们会 48 小时内安排上门。'
  }
  if (/价格|多少钱|报价/.test(t)) {
    return '不同产品系列价格不同，胡桃禮实木餐桌参考价 ¥1280 起。您可在「产品中心」查看详情，或预约到店让设计师为您报价。'
  }
  if (/发货|物流|快递|送货/.test(t)) {
    return '下单后我们会在 3-5 个工作日内发货，全国包邮（偏远地区除外），大件家具提供送货上门 + 安装服务。'
  }
  if (/定制/.test(t)) {
    return '支持定制尺寸与材质。您可在线预约「定制服务」，设计师会根据您的户型出专属方案，工期约 30-45 天。'
  }
  if (/人工|转人工/.test(t)) {
    return '正在为您转接人工客服，请拨打 400-800-1953（9:00-21:00）或稍候，我们尽快安排顾问联系您。'
  }
  if (/你好|您好|hi|hello|在吗/i.test(t)) {
    return '您好！我是 YD 家居智能客服小 Y，可以为您解答产品、预约、售后等问题。'
  }
  return '这个问题我还在学习中～您可以试试问「怎么预约到店」「胡桃禮系列」「售后服务」等，或拨打 400-800-1953 转人工客服。'
}

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [msgs, setMsgs] = useState<ChatMsg[]>([
    { from: 'bot', text: '您好！我是 YD 家居智能客服小 Y 🛋️，请问有什么可以帮您？' },
  ])

  const send = (text: string) => {
    const t = text.trim()
    if (!t) return
    setMsgs((prev) => [...prev, { from: 'user', text: t }])
    setInput('')
    setTimeout(() => {
      setMsgs((prev) => [...prev, { from: 'bot', text: botAnswer(t) }])
    }, 400)
  }

  return (
    <>
      {/* 悬浮按钮 */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-walnut text-2xl shadow-lg transition hover:scale-105"
        title="在线客服"
      >
        {open ? '✕' : '💬'}
      </button>

      {/* 聊天窗口 */}
      {open && (
        <div className="fixed bottom-24 right-6 z-40 flex h-[480px] w-[360px] max-w-[calc(100vw-3rem)] flex-col overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-coal/10">
          <header className="flex items-center gap-3 bg-walnut px-5 py-4 text-white">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/20 text-lg">🤖</div>
            <div>
              <h3 className="font-semibold">YD 智能客服</h3>
              <p className="text-xs text-white/80">小 Y 在线 · 秒回</p>
            </div>
          </header>

          <div className="flex-1 space-y-3 overflow-y-auto bg-sand/50 p-4">
            {msgs.map((m, i) => (
              <div key={i} className={`flex ${m.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-6 ${
                    m.from === 'user'
                      ? 'rounded-br-sm bg-walnut text-white'
                      : 'rounded-bl-sm bg-white text-coal shadow-sm ring-1 ring-coal/5'
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-coal/10 bg-white p-3">
            <div className="mb-2 flex flex-wrap gap-1.5">
              {QUICK_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => send(q)}
                  className="rounded-full border border-walnut/30 bg-walnut/5 px-3 py-1 text-xs text-walnut hover:bg-walnut/10"
                >
                  {q}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && send(input)}
                placeholder="输入您的问题..."
                className="flex-1 rounded-lg border border-coal/15 px-4 py-2.5 text-sm outline-none focus:border-walnut"
              />
              <button
                onClick={() => send(input)}
                className="rounded-lg bg-walnut px-5 py-2.5 text-sm font-medium text-white hover:bg-walnut/90"
              >
                发送
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}