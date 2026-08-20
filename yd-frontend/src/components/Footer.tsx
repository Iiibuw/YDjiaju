/** 页脚（UI 文档 §16 布局：产品/关于/联系 + 版权行）。 */
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="mt-20 border-t border-stone-200 bg-card">
      <div className="container-yf grid gap-8 py-12 text-sm text-stone-600 md:grid-cols-4">
        <div>
          <h4 className="font-display mb-4 text-base text-ink">YD 家具</h4>
          <p className="leading-relaxed text-stone-500">百年家具品牌，传承匠心工艺，融合现代美学。</p>
        </div>
        <div>
          <h4 className="font-display mb-4 text-base text-ink">产品</h4>
          <ul className="space-y-2">
            <li><Link to="/products" className="hover:text-ink">产品中心</Link></li>
            <li><Link to="/cases" className="hover:text-ink">案例展示</Link></li>
            <li><Link to="/downloads" className="hover:text-ink">下载中心</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-display mb-4 text-base text-ink">关于</h4>
          <ul className="space-y-2">
            <li><Link to="/about" className="hover:text-ink">关于我们</Link></li>
            <li><Link to="/news" className="hover:text-ink">新闻资讯</Link></li>
            <li><Link to="/jobs" className="hover:text-ink">人才招聘</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-display mb-4 text-base text-ink">联系</h4>
          <p className="leading-relaxed text-stone-500">
            客服电话：400-xxx-xxxx<br />
            工作时间：9:00 - 18:00<br />
            地址：广东省佛山市顺德区
          </p>
        </div>
      </div>
      <div className="border-t border-stone-200 py-6 text-center text-xs text-stone-500">
        © 2026 YD 家具 · 基于 PRD v1.1 + UI/UX v1.0 + 开发技术文档 v1.1
      </div>
    </footer>
  )
}
