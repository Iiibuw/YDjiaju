/** 售后服务：服务流程 + 常见问题 + 服务承诺。 */

const SERVICE_STEPS = [
  { icon: '📞', title: '预约登记', desc: '拨打 400 热线或在线预约，客服确认时间' },
  { icon: '🔧', title: '上门服务', desc: '工程师按约上门，专业工具规范操作' },
  { icon: '✅', title: '服务验收', desc: '服务完成后请您验收，确认满意签字' },
  { icon: '📝', title: '回访评价', desc: '72 小时内电话回访，您的评分是我们的动力' },
]

const COMMON_QUESTIONS = [
  {
    q: '家具保修期多久？',
    a: 'YD 实木家具提供 5 年结构保修、2 年表面保修。五金件、导轨等易损件保修 1 年。',
  },
  {
    q: '如何预约售后上门？',
    a: '拨打 400-800-1953 或通过官网「联系我们」留言，我们会在 24 小时内安排工程师回电。',
  },
  {
    q: '实木家具日常如何保养？',
    a: '避免阳光直射与潮湿环境；使用软布干擦；每半年使用木质家具护理油保养一次即可。',
  },
  {
    q: '定制产品出现尺寸偏差怎么办？',
    a: '定制产品出厂前经过三重尺寸校验，如仍有偏差可申请免费返工或重新制作。',
  },
]

const PROMISES = [
  { title: '5 年质保', desc: '结构件保修 5 年，非人为损坏免费维修' },
  { title: '终身维护', desc: '质保期后终身成本价维护，绝不漫天要价' },
  { title: '48h 响应', desc: '全国 500+ 服务网点，48 小时内上门' },
  { title: '无理由换新', desc: '7 天无理由退换，30 天质量问题换新' },
]

export default function Service() {
  return (
    <>
      {/* ===== 顶部横幅 ===== */}
      <section className="bg-gradient-to-br from-walnut/10 to-sand py-16">
        <div className="container-yf text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-walnut">After-sales Service</p>
          <h1 className="mt-3 text-4xl font-bold text-coal sm:text-5xl">售后服务</h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-coal/70">
            每一件 YD 家具，都是一份长久的承诺。
          </p>
        </div>
      </section>

      {/* ===== 服务承诺 ===== */}
      <section className="bg-white py-16">
        <div className="container-yf">
          <h2 className="text-center text-2xl font-bold text-coal">服务承诺</h2>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {PROMISES.map((p) => (
              <div key={p.title} className="rounded-2xl border border-walnut/10 bg-sand/40 p-8 text-center">
                <h3 className="text-lg font-bold text-walnut">{p.title}</h3>
                <p className="mt-3 text-sm leading-6 text-coal/60">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 服务流程 ===== */}
      <section className="bg-sand py-16">
        <div className="container-yf">
          <h2 className="text-center text-2xl font-bold text-coal">服务流程</h2>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {SERVICE_STEPS.map((s, i) => (
              <div key={s.title} className="relative rounded-2xl bg-white p-8 shadow-sm ring-1 ring-coal/5">
                <span className="absolute right-4 top-4 font-display text-4xl font-bold text-walnut/15">0{i + 1}</span>
                <div className="text-3xl">{s.icon}</div>
                <h3 className="mt-4 font-semibold text-coal">{s.title}</h3>
                <p className="mt-2 text-sm leading-6 text-coal/60">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 常见问题 ===== */}
      <section className="bg-white py-16">
        <div className="container-yf mx-auto max-w-3xl">
          <h2 className="text-center text-2xl font-bold text-coal">常见问题</h2>
          <div className="mt-10 space-y-4">
            {COMMON_QUESTIONS.map((qa) => (
              <details key={qa.q} className="group rounded-2xl border border-coal/10 bg-sand/30 p-6">
                <summary className="flex cursor-pointer items-center justify-between font-medium text-coal">
                  {qa.q}
                  <span className="text-walnut transition group-open:rotate-45">＋</span>
                </summary>
                <p className="mt-3 text-sm leading-7 text-coal/70">{qa.a}</p>
              </details>
            ))}
          </div>
          <div className="mt-10 rounded-2xl bg-walnut/5 p-6 text-center text-sm text-coal/70">
            📞 服务热线：<span className="font-semibold text-walnut">400-800-1953</span>（9:00-21:00，全年无休）
          </div>
        </div>
      </section>
    </>
  )
}