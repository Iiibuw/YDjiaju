/** 页脚（UI 文档 §16 布局：产品/关于/联系 + 版权行）。
 *
 * 黑金色独立区段：v2.1 起 Footer 保留奢华配色（不依赖 token），
 * 其他页面已恢复浅色。
 */
import { Link } from 'react-router-dom'

const INK_LIGHT = '#ece5d8'
const SUB = '#bdb5a2'
const DEEP_BG = '#0d0b09'
const BORDER = '#2c2720'

export default function Footer() {
  return (
    <footer
      className="mt-20 border-t"
      style={{ backgroundColor: DEEP_BG, borderColor: BORDER }}
    >
      <div className="container-yf grid gap-8 py-12 text-sm md:grid-cols-4" style={{ color: SUB }}>
        <div>
          <h4 className="font-display mb-4 text-base" style={{ color: INK_LIGHT }}>
            YD 家具
          </h4>
          <p className="leading-relaxed" style={{ color: '#9a917d' }}>
            百年家具品牌，传承匠心工艺，融合现代美学。
          </p>
        </div>
        <div>
          <h4 className="font-display mb-4 text-base" style={{ color: INK_LIGHT }}>
            产品
          </h4>
          <ul className="space-y-2">
            <li>
              <Link
                to="/products"
                className="transition-colors hover:text-[#c9a227]"
                style={{ color: SUB }}
              >
                产品中心
              </Link>
            </li>
            <li>
              <Link
                to="/cases"
                className="transition-colors hover:text-[#c9a227]"
                style={{ color: SUB }}
              >
                案例展示
              </Link>
            </li>
            <li>
              <Link
                to="/downloads"
                className="transition-colors hover:text-[#c9a227]"
                style={{ color: SUB }}
              >
                下载中心
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <h4 className="font-display mb-4 text-base" style={{ color: INK_LIGHT }}>
            关于
          </h4>
          <ul className="space-y-2">
            <li>
              <Link
                to="/about"
                className="transition-colors hover:text-[#c9a227]"
                style={{ color: SUB }}
              >
                关于我们
              </Link>
            </li>
            <li>
              <Link
                to="/news"
                className="transition-colors hover:text-[#c9a227]"
                style={{ color: SUB }}
              >
                新闻资讯
              </Link>
            </li>
            <li>
              <Link
                to="/jobs"
                className="transition-colors hover:text-[#c9a227]"
                style={{ color: SUB }}
              >
                人才招聘
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <h4 className="font-display mb-4 text-base" style={{ color: INK_LIGHT }}>
            联系
          </h4>
          <p className="leading-relaxed" style={{ color: '#9a917d' }}>
            客服电话：400-xxx-xxxx
            <br />
            工作时间：9:00 - 18:00
            <br />
            地址：广东省佛山市顺德区
          </p>
        </div>
      </div>
      <div
        className="border-t py-6 text-center text-xs"
        style={{ borderColor: BORDER, color: '#9a917d' }}
      >
        © 2026 YD 家具 · 基于 PRD v1.1 + UI/UX v1.0 + 开发技术文档 v1.1
      </div>
    </footer>
  )
}