/** 关于我们：动态区块（后端 about-sections）+ 品牌故事 + 数据 + 资质 + 团队。 */
import { useQuery } from '@tanstack/react-query'

import { listAboutSections, type AboutSection } from '../api/about'

const MILESTONES = [
  { year: '1953', title: '品牌创立', desc: '佛山木工坊起家，主打手工实木家具' },
  { year: '1985', title: '品牌化', desc: '注册 YD 商标，进入标准化生产' },
  { year: '2001', title: '全国布局', desc: '门店覆盖华南六省，出口东南亚' },
  { year: '2016', title: '新零售', desc: '线上旗舰店 + 线下体验馆双渠道' },
  { year: '2023', title: '智能制造', desc: '佛山智能工厂投产，C2M 定制上线' },
]

const CERTIFICATES = ['ISO9001 质量认证', 'FSC 森林认证', '国家环保十环认证', '3C 安全认证']

const TEAM = [
  { name: '陈志远', role: '创始人 / 首席设计师', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200' },
  { name: '林晓芸', role: '设计总监', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200' },
  { name: '王建国', role: '生产总监', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200' },
]

const VALUES = [
  { icon: '🌳', title: '原材可溯', desc: '北美 FAS 级黑胡桃木，每一棵树都有来源' },
  { icon: '🛠️', title: '匠心工艺', desc: '70 年老师傅传承的榫卯 + 现代 CNC 结合' },
  { icon: '♻️', title: '绿色环保', desc: '水性漆涂装，甲醛释放达 E0 级标准' },
  { icon: '🤝', title: '终身服务', desc: '全国 500 网点，终身维护承诺' },
]

export default function About() {
  const { data: sectionsData } = useQuery({
    queryKey: ['about-sections'],
    queryFn: listAboutSections,
  })
  const sections: AboutSection[] = sectionsData ?? []

  return (
    <>
      {/* ===== 顶部横幅 ===== */}
      <section id="about-yd" className="bg-gradient-to-br from-walnut/10 to-sand py-16">
        <div className="container-yf text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-walnut">About YD</p>
          <h1 className="mt-3 text-4xl font-bold text-coal sm:text-5xl">关于 YD 家具</h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-coal/70">
            始于 1953 年，一家专注于实木家具的家族企业。我们相信，好的家具应与时光共同生长。
          </p>
        </div>
      </section>

      {/* ===== 关于我们区块（阶段 4：数据驱动 /public/about-sections，无数据时保留静态） ===== */}
      {sections.length > 0 && (
        <section className="bg-white py-20">
          <div className="container-yf space-y-16">
            {sections.map((s) => (
              <div key={s.id} id={s.code}>
                <h2 className="text-center text-3xl font-bold text-coal">{s.title}</h2>
                {s.subtitle && <p className="mt-2 text-center text-coal/60">{s.subtitle}</p>}
                {s.body && (
                  <div
                    className="mx-auto mt-8 max-w-3xl text-base leading-8 text-coal/80 [&_h3]:mt-6 [&_h3]:text-xl [&_h3]:font-semibold [&_ul]:list-disc [&_ul]:pl-6 [&_li]:my-1"
                    dangerouslySetInnerHTML={{ __html: s.body }}
                  />
                )}
                {s.images.length > 0 && (
                  <div className="mt-8 grid grid-cols-2 gap-4 lg:grid-cols-3">
                    {s.images.map((img) => (
                      <img key={img.id} src={img.url} alt={img.caption ?? s.title} className="h-52 w-full rounded-xl object-cover" />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ===== 品牌故事 ===== */}
      <section id="story" className="bg-white py-20">
        <div className="container-yf grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
          <div className="overflow-hidden rounded-2xl">
            <img
              src="https://images.unsplash.com/photo-1581539250439-c96689b5164a?w=1000"
              alt="YD 品牌故事"
              className="w-full object-cover"
            />
          </div>
          <div>
            <p className="text-sm font-medium uppercase tracking-widest text-walnut">Our Story</p>
            <h2 className="mt-3 text-3xl font-bold text-coal">七十年，一件事</h2>
            <p className="mt-6 text-base leading-8 text-coal/80">
              1953 年，我们在佛山一间小木工作坊里刨下第一片木板。从手工刨花到 CNC 精雕，从本地街坊到全国十万家庭，
              YD 始终相信：家具不只是物件，而是家的容器。
            </p>
            <p className="mt-4 text-base leading-8 text-coal/80">
              今天，我们拥有 120+ 城市门店、10 万+ 家庭用户，但每一次下料、每一道打磨，依然像七十年前那样认真。
            </p>
          </div>
        </div>
      </section>

      {/* ===== 里程碑 ===== */}
      <section id="history" className="bg-sand py-20 scroll-mt-20">
        <div className="container-yf">
          <h2 className="text-center text-3xl font-bold text-coal">发展历程</h2>
          <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-3 lg:grid-cols-5">
            {MILESTONES.map((m) => (
              <div key={m.year} className="relative rounded-2xl bg-white p-6 shadow-sm ring-1 ring-coal/5">
                <p className="font-display text-2xl font-bold text-walnut">{m.year}</p>
                <p className="mt-2 font-semibold text-coal">{m.title}</p>
                <p className="mt-2 text-sm leading-6 text-coal/60">{m.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 品牌价值 ===== */}
      <section id="promise" className="bg-white py-20 scroll-mt-20">
        <div className="container-yf">
          <h2 className="text-center text-3xl font-bold text-coal">品牌承诺</h2>
          <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {VALUES.map((v) => (
              <div key={v.title} className="rounded-2xl border border-coal/5 bg-sand/50 p-8 text-center">
                <div className="text-4xl">{v.icon}</div>
                <h3 className="mt-4 text-lg font-semibold text-coal">{v.title}</h3>
                <p className="mt-2 text-sm leading-6 text-coal/60">{v.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 资质 ===== */}
      <section id="certificates" className="bg-sand py-20 scroll-mt-20">
        <div className="container-yf">
          <h2 className="text-center text-3xl font-bold text-coal">资质认证</h2>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            {CERTIFICATES.map((c) => (
              <div key={c} className="rounded-full border border-walnut/30 bg-white px-6 py-3 text-sm font-medium text-walnut">
                ✓ {c}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 团队 ===== */}
      <section id="team" className="bg-white py-20 scroll-mt-20">
        <div className="container-yf">
          <h2 className="text-center text-3xl font-bold text-coal">核心团队</h2>
          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
            {TEAM.map((t) => (
              <div key={t.name} className="text-center">
                <div className="mx-auto h-28 w-28 overflow-hidden rounded-full ring-4 ring-walnut/10">
                  <img src={t.avatar} alt={t.name} className="h-full w-full object-cover" />
                </div>
                <h3 className="mt-4 font-semibold text-coal">{t.name}</h3>
                <p className="mt-1 text-sm text-coal/50">{t.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 联系信息（页面最底部新增区块） ===== */}
      <section id="contact" className="bg-sand py-16 scroll-mt-20">
        <div className="container-yf">
          <h2 className="text-center text-3xl font-bold text-coal">联系信息</h2>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
            <div className="rounded-2xl bg-white p-6 text-center ring-1 ring-coal/5">
              <div className="text-3xl">📞</div>
              <h3 className="mt-3 text-sm font-semibold uppercase tracking-widest text-walnut">联系电话</h3>
              <p className="mt-3 text-2xl font-bold text-coal">400-xxx-xxxx</p>
              <p className="mt-1 text-xs text-coal/50">全国统一服务热线</p>
            </div>
            <div className="rounded-2xl bg-white p-6 text-center ring-1 ring-coal/5">
              <div className="text-3xl">⏰</div>
              <h3 className="mt-3 text-sm font-semibold uppercase tracking-widest text-walnut">工作时间</h3>
              <p className="mt-3 text-2xl font-bold text-coal">9:00 — 18:00</p>
              <p className="mt-1 text-xs text-coal/50">周一至周日 全年无休</p>
            </div>
            <div className="rounded-2xl bg-white p-6 text-center ring-1 ring-coal/5">
              <div className="text-3xl">📍</div>
              <h3 className="mt-3 text-sm font-semibold uppercase tracking-widest text-walnut">公司地址</h3>
              <p className="mt-3 text-base font-semibold text-coal">广东省佛山市顺德区</p>
              <p className="mt-1 text-xs text-coal/50">YD 家具总部</p>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}