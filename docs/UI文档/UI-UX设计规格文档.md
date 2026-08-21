# YD家居 平台 UI/UX 设计规格文档

> **版本**：v1.0 ｜ **日期**：2026-08-18 ｜ **状态**：正式发布
> **依据**：PRD v1.2 + 14 个高保真原型 HTML
> **技术栈**：前台 React + Tailwind CSS ｜ 后台 React + Ant Design ｜ 后端 FastAPI
> **设计工具**：ui-ux-pro-max 设计智能（设计系统检索 + UX 规范库）

---

## 目录

- [第一篇 · 基础与策略](#第一篇--基础与策略)
- [第二篇 · 前台设计系统（React + Tailwind）](#第二篇--前台设计系统react--tailwind)
- [第三篇 · 后台设计系统（React + Ant Design）](#第三篇--后台设计系统react--ant-design)
- [第四篇 · 信息架构与导航](#第四篇--信息架构与导航)
- [第五篇 · 前台页面规格](#第五篇--前台页面规格)
- [第六篇 · 后台页面规格](#第六篇--后台页面规格)
- [第七篇 · 组件库规范](#第七篇--组件库规范)
- [第八篇 · 交互与体验规范](#第八篇--交互与体验规范)
- [第九篇 · 响应式与移动端](#第九篇--响应式与移动端)
- [第十篇 · 可访问性与交付清单](#第十篇--可访问性与交付清单)

---

# 第一篇 · 基础与策略

## 1. 文档信息与版本

| 项 | 内容 |
|---|---|
| 文档名称 | YD家居平台 UI/UX 设计规格文档 |
| 版本 | v1.1 |
| 创建日期 | 2026-08-18 |
| 依据 | PRD v1.2（§1–§13.1）+ 14 个高保真原型 HTML |
| 覆盖范围 | 前台展示系统 12 页 + 后台管理系统 11 模块 + 设计系统 + 组件库 + 交互规范 |
| 读者对象 | 前端工程师、UI 设计师、产品经理、测试工程师 |
| 验收用途 | 开发还原依据 + UI 走查清单 + 测试验收参考 |
| 本版更新 | **v1.1（2026-08-21）**：① 重写 §33 产品管理——表格列对齐开发实现（封面/标题/副标题/系列/空间/品类/最低价/最高价/排序/状态/创建时间/操作 12 列），表单新增「风格」字段；② 新增 §33.1 分类管理（空间/系列/品类 三 Tab，后台维护、前台筛选栏自动同步）；③ §17 后台菜单新增「分类管理」 |

## 2. 项目背景与设计目标

YD家居平台是"展示 + 线索 + 部分电商"的混合模式官网及后台系统。参考站点蓝鸟家居为典型展示型官网，本项目在其基础上扩展为支持部分商品在线下单、预约线索、招聘投递、智能客服的完整运营闭环。

**设计目标**：

1. **品牌温润感** — 前台以暖灰石色 + 金色点缀传递家居品牌的温度与品质，区别于冷色调科技站
2. **展示优先、线索为本** — 视觉重心在产品图与案例图，转化路径以预约/咨询留资为主要目标
3. **前后台风格分离** — 前台 Tailwind 暖色优雅（Lexend + Source Sans 3），后台 AntD 蓝色专业（Inter），各成体系
4. **角色驱动** — 后台按 5 类角色渲染菜单与权限，数据隔离
5. **移动端闭环** — 关键路径（浏览/预约/下单）在移动端完整可用
6. **渐进增强** — 动效尊重 `prefers-reduced-motion`，图片懒加载，无障碍可达

## 3. 设计原则

| 编号 | 原则 | 说明 | 落地要求 |
|------|------|------|---------|
| P1 | 品牌温润 | 暖灰石色（stone/sand）为底，金色（gold #CA8A04）为品牌强调色 | 前台全站统一 Token，不引入冷色调 |
| P2 | 展示优先 | 产品/案例图占据视觉重心，文字辅助 | 卡片图占比 ≥ 60%，标题简洁 |
| P3 | 线索为本 | 每个页面均有明确的预约/咨询/下单入口 | 顶部操作区 + 页脚 + 浮窗三重触达 |
| P4 | 风格分离 | 前台暖色优雅，后台蓝色专业 | 两套独立 Design Token，不混用 |
| P5 | 角色驱动 | 后台菜单按角色权限渲染 | 5 角色 × 11 模块映射，前端控制显隐 + 服务端强制 |
| P6 | 渐进增强 | 动效可降级，图片懒加载，无障碍可达 | `prefers-reduced-motion` + aria-label + 键盘导航 |

## 4. 用户角色与核心场景

### 4.1 前台用户

| 用户类型 | 核心场景 | 关键路径 |
|---------|---------|---------|
| C 端消费者 | 浏览产品/案例 → 查价格库存 → 在线咨询/预约 → 部分商品下单 | 首页→产品中心→产品详情→加购→结算→我的订单 |
| B 端客户 | 了解品牌实力 → 招商加盟咨询 → 批量采购询价 | 关于我们→案例→在线预约→客服咨询 |
| 求职者 | 查看招聘信息 → 投递简历 → 跟踪进度 | 招聘→岗位详情→投递→我的投递 |
| 海外访客 | 英文版浏览（本期不做，二期规划） | — |

### 4.2 后台角色

| 角色 | 菜单权限 | 典型场景 |
|------|---------|---------|
| 超级管理员（admin） | 全部 11 模块 | 系统配置、权限分配、全局监控 |
| 内容编辑（editor） | 仪表盘/轮播图/新闻/案例/关于我们/招聘/留言 | 新闻发布、案例维护、留言回复 |
| 产品管理员（product） | 仪表盘/轮播图/产品/订单 | 产品上下架、SKU/库存维护 |
| 客服运营（service） | 仪表盘/预约/留言/订单 | 线索跟进、客服回复、订单处理 |
| 订单专员（order） | 仪表盘/订单/预约 | 订单发货、退款处理 |

---

# 第二篇 · 前台设计系统（React + Tailwind）

## 5. 色彩系统

### 5.1 品牌 Token 定义

前台采用 Tailwind 自定义色彩，以暖灰石色为底、金色为品牌强调色：

```javascript
// tailwind.config.js
colors: {
  ink:   '#1C1917',  // 主标题/Logo底/深色背景
  stone2:'#44403C',  // 次级文字/导航默认态
  gold:  '#CA8A04',  // 品牌强调色（按钮/链接/装饰线/徽标）
  sand:  '#FAFAF9',  // 页面背景
  coal:  '#0C0A09',  // 最深文字
}
```

### 5.2 色彩使用规范

| Token | Hex | 语义 | 用途 | Tailwind 类名示例 |
|-------|-----|------|------|------------------|
| ink | `#1C1917` | 主色 | 标题文字、Logo 底色、深色区块背景、按钮描边 | `text-ink` `bg-ink` `border-ink` |
| stone2 | `#44403C` | 次级 | 导航默认态、次级文字、图标 | `text-stone2` |
| gold | `#CA8A04` | 强调 | 品牌按钮、链接、激活态、装饰线、徽标 | `bg-gold` `text-gold` `border-gold` |
| sand | `#FAFAF9` | 背景 | 页面背景、卡片底色 | `bg-sand` |
| coal | `#0C0A09` | 极深 | 最深文字（少用） | `text-coal` |

### 5.3 语义色（补充）

| 语义 | Hex | 用途 | Tailwind 类名 |
|------|-----|------|-------------|
| 成功 | `#16A34A` | 成功状态、已发布、已回复 | `text-green-600` `bg-green-50` |
| 警告 | `#CA8A04` | 待处理、提醒（与品牌色一致） | `text-gold` |
| 危险 | `#EF4444` | 删除、错误、退出登录 | `text-red-500` `text-red-600` |
| 信息 | `#3B82F6` | 信息提示（少用，避免与后台蓝色混淆） | `text-blue-500` |

### 5.4 中性色阶（Tailwind stone 系列）

| 色阶 | Hex | 用途 |
|------|-----|------|
| stone-50 | `#FAFAF9` | 等同 sand，页面背景 |
| stone-100 | `#F5F5F4` | 卡片 hover 背景、分隔区 |
| stone-200 | `#E7E5E4` | 边框、分隔线 |
| stone-300 | `#D6D3D1` | 输入框边框、禁用态 |
| stone-400 | `#A8A29E` | 占位文字、辅助文字 |
| stone-500 | `#78716C` | 次级说明文字 |
| stone-600 | `#57534E` | 表单 label |
| stone-800 | `#292524` | 深色区块次级文字 |
| stone-900 | `#1C1917` | 等同 ink |

## 6. 字体系统

### 6.1 字体家族

| 用途 | 字体 | 字重 | 引入方式 |
|------|------|------|---------|
| 标题 | Lexend | 300/400/500/600/700 | Google Fonts |
| 正文 | Source Sans 3 | 300/400/500/600/700 | Google Fonts |

```html
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&family=Source+Sans+3:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
```

```javascript
// tailwind.config.js
fontFamily: {
  head: ['Lexend', 'sans-serif'],   // h1–h6, .font-head
  body: ['Source Sans 3', 'sans-serif'], // body 默认
}
```

```css
body { font-family: 'Source Sans 3', sans-serif; }
h1, h2, h3, .font-head { font-family: 'Lexend', sans-serif; }
```

### 6.2 字号阶梯

| 级别 | Tailwind 类 | 字号 | 行高 | 用途 |
|------|------------|------|------|------|
| Display | `text-5xl` | 48px | leading-tight | 首页 Hero 主标题 |
| H1 | `text-4xl` | 36px | leading-tight | 页面主标题（产品中心/关于我们 banner） |
| H2 | `text-3xl` | 30px | leading-tight | 区块标题 |
| H3 | `text-xl` | 20px | leading-snug | 卡片标题、弹窗标题 |
| H4 | `text-lg` | 18px | leading-snug | 子区块标题 |
| Body | `text-base` | 16px | leading-relaxed | 正文（移动端最小 16px） |
| Body-sm | `text-sm` | 14px | leading-normal | 次级正文、表单、按钮 |
| Caption | `text-xs` | 12px | leading-normal | 标签、辅助说明、脚注 |
| Micro | `text-[11px]` | 11px | leading-normal | 进度阶段标签、徽标数字 |

### 6.3 字重规范

| 字重 | 数值 | 用途 |
|------|------|------|
| Light | 300 | 大标题装饰性文字 |
| Regular | 400 | 正文 |
| Medium | 500 | 导航、按钮、卡片标题 |
| Semibold | 600 | 区块标题、强调 |
| Bold | 700 | Logo、Hero 标题、KPI 数值 |

## 7. 间距与栅格

### 7.1 间距基准

采用 **8px 基准**（Tailwind 默认 4px 间距体系，实际使用 8 的倍数）：

| Token | 值 | 用途 |
|-------|-----|------|
| space-1 | 4px | 图标与文字间距 |
| space-2 | 8px | 紧凑元素间距 |
| space-3 | 12px | 按钮内边距、列表项间距 |
| space-4 | 16px | 卡片内边距、表单项间距 |
| space-6 | 24px | 区块间距、卡片间距 |
| space-8 | 32px | 区块内边距 |
| space-12 | 48px | 区块垂直间距 |
| space-14 | 56px | 大区块垂直间距 |

### 7.2 容器与栅格

| 属性 | 值 | 说明 |
|------|-----|------|
| 最大宽度 | `max-w-7xl` (1280px) | 全站统一内容区 |
| 水平内边距 | `px-4 sm:px-6` | 移动端 16px / 桌面端 24px |
| 栅格列数 | 12 列（Tailwind grid） | 产品网格使用 `grid-cols-2 md:grid-cols-4` |
| 卡片间距 | `gap-6` (24px) | 产品/案例/新闻卡片统一 |

### 7.3 断点定义

| 断点 | 前缀 | 宽度 | 布局变化 |
|------|------|------|---------|
| 默认 | — | <640px | 单列、移动端导航折叠 |
| sm | `sm:` | ≥640px | 部分双列、Hero 高度增加 |
| md | `md:` | ≥768px | 2 列网格、操作区显示 |
| lg | `lg:` | ≥1024px | 4 列网格、顶部导航完整显示 |
| xl | `xl:` | ≥1280px | max-w-7xl 容器居中 |

## 8. 图标与图形

### 8.1 图标规范

| 属性 | 规范 |
|------|------|
| 图标库 | 内联 SVG（线性风格，stroke-width 1.5–2） |
| 尺寸 | 导航/操作区 `w-5 h-5` (20px)；移动端菜单 `w-6 h-6` (24px)；客服浮窗 `w-7 h-7` (28px) |
| 颜色 | 跟随 `currentColor`，使用 `text-stone2` / `text-gold` / `text-sand` |
| viewBox | 统一 `0 0 24 24` |
| stroke | `fill="none" stroke="currentColor" stroke-width="1.8"` |

**禁止**：使用 emoji 作为 UI 图标。

### 8.2 品牌徽标

```html
<!-- 导航栏 Logo -->
<span class="inline-flex items-center justify-center w-9 h-9 rounded-md bg-ink text-gold font-head font-bold">YD</span>
<span class="font-head text-xl font-semibold text-ink">YD家具</span>
```

### 8.3 占位图规范

原型中产品/案例图采用 CSS 渐变 + 内联 SVG 家具图标作为占位：

```css
.prod-thumb {
  background: linear-gradient(135deg, #f5f5f4 0%, #e7e5e4 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
/* 深色版本（页脚等） */
.prod-thumb-dark {
  background: linear-gradient(135deg, #1C1917, #44403C);
}
```

生产环境替换为真实产品图，使用 `<img loading="lazy">` + WebP 格式 + srcset 响应式。

## 9. 阴影、圆角与边框

### 9.1 圆角

| Token | 值 | 用途 |
|-------|-----|------|
| rounded-md | 6px | 小按钮、输入框、徽标 |
| rounded-lg | 8px | 按钮、卡片图、输入框 |
| rounded-xl | 12px | 卡片、弹窗内层 |
| rounded-2xl | 16px | 弹窗、大型卡片 |
| rounded-full | 9999px | 圆形头像、胶囊按钮、标签 chip、客服浮窗 |

### 9.2 阴影

| 级别 | Tailwind 类 | 用途 |
|------|------------|------|
| 基础 | `shadow` | 卡片默认 |
| 悬浮 | `shadow-lg` | 下拉菜单、弹窗 |
| 强悬浮 | `shadow-xl` | 客服浮窗按钮 |
| 极强 | `shadow-2xl` | 用户菜单下拉 |

### 9.3 边框

| 用途 | 类名 | 色值 |
|------|------|------|
| 卡片边框 | `border border-stone-200` | #E7E5E4 |
| 输入框边框 | `border border-stone-300` | #D6D3D1 |
| 输入框聚焦 | `focus:border-gold` | #CA8A04 |
| 深色区块边框 | `border-gold/20` | gold 20% 透明度 |
| 分隔线 | `border-stone-200` / `border-white/10`（深色） | — |

## 10. 动效规范

### 10.1 过渡时长

| 类型 | 时长 | 缓动函数 | 用途 |
|------|------|---------|------|
| 微交互 | 150–200ms | ease | hover 颜色变化、按钮态切换 |
| 展开 | 200ms | ease-out | 下拉菜单、子导航 |
| 弹窗 | 200–300ms | opacity ease | Modal 显示/隐藏 |
| 轮播 | 600ms | opacity ease | 幻灯片切换 |
| 抽屉 | 250ms | transform ease | 后台 Drawer 滑入 |

### 10.2 Hover 反馈

```css
/* 导航链接下划线动画 */
.nav-link { position: relative; }
.nav-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -6px;
  height: 2px;
  width: 0;
  background: #CA8A04;
  transition: width .2s ease;
}
.nav-link:hover::after,
.nav-link.active::after { width: 100%; }

/* 子导航展开 */
.sub-nav {
  opacity: 0;
  visibility: hidden;
  transform: translateY(8px);
  transition: all .2s ease;
}
.nav-item:hover .sub-nav {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}
```

### 10.3 轮播

```css
.carousel-slide {
  transition: opacity .6s ease;
  cursor: pointer;
}
.carousel-slide:hover .slide-hint { opacity: 1; }
```

### 10.4 Toast

```css
#toast {
  position: fixed;
  left: 50%;
  bottom: 40px;
  transform: translateX(-50%) translateY(20px);
  opacity: 0;
  transition: all .3s;
}
#toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
/* 2.2s 后自动消失 */
```

### 10.5 购物车徽标动画

```javascript
// 徽标数字变化时的弹性动画
badge.animate(
  [{ transform: 'scale(1)' }, { transform: 'scale(1.4)' }, { transform: 'scale(1)' }],
  { duration: 350 }
);
```

### 10.6 降级策略

```css
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
```

---

# 第三篇 · 后台设计系统（React + Ant Design）

## 11. 色彩系统

### 11.1 品牌 Token 定义

后台采用 Ant Design 蓝色为主色，配合暗色侧边栏，体现专业管理感：

```javascript
// tailwind.config.js（后台自定义）
colors: {
  primary:  '#1677ff',  // 主操作色（AntD Blue 6）
  primaryh: '#4096ff',  // hover 色（AntD Blue 5）
  ink:      '#1f2937',  // 主文字（slate-800）
  stone2:   '#6b7280',  // 次级文字（gray-500）
  sand:     '#f5f7fa',  // 内容区背景
}
```

### 11.2 色彩使用规范

| Token | Hex | 语义 | 用途 |
|-------|-----|------|------|
| primary | `#1677ff` | 主操作 | 按钮、激活态菜单、链接、图表主线 |
| primaryh | `#4096ff` | hover | 按钮 hover、链接 hover |
| ink | `#1f2937` | 主文字 | 标题、正文 |
| stone2 | `#6b7280` | 次级 | 说明文字、表头 |
| sand | `#f5f7fa` | 背景 | 内容区底色 |

### 11.3 侧边栏暗色系

| 元素 | 色值 | 用途 |
|------|-----|------|
| 侧边栏背景 | `bg-slate-900` (#0F172A) | 暗色侧边栏 |
| 菜单默认文字 | `text-slate-300` (#CBD5E1) | 未激活菜单项 |
| 菜单 hover | `bg-slate-800` (#1E293B) + `text-white` | hover 高亮 |
| 菜单激活 | `bg-primary` (#1677ff) + `text-white` | 当前模块 |
| 侧边栏边框 | `border-slate-700` (#334155) | 分隔线 |

### 11.4 语义色

| 语义 | 操作色类 | Hex | 用途 |
|------|---------|-----|------|
| 编辑 | `.act-edit` | `#1677ff` | 编辑按钮 |
| 删除 | `.act-del` | `#ef4444` | 删除按钮 |
| 新增 | `.act-add` | `#16a34a` | 新增/回复按钮 |
| 成功 | `text-green-600` | `#16a34a` | 已发布、已回复、✓ |
| 危险 | `text-red-600` | `#ef4444` | 错误、删除确认 |
| 禁用 | `text-slate-300` | `#CBD5E1` | — 占位 |

## 12. 字体系统

| 用途 | 字体 | 字重 | 引入 |
|------|------|------|------|
| 全局 | Inter | 300/400/500/600/700 | Google Fonts |

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
```

```css
body { font-family: 'Inter', sans-serif; }
```

### 字号阶梯

| 级别 | Tailwind 类 | 字号 | 用途 |
|------|------------|------|------|
| H1 | `text-2xl` | 24px | 登录页标题 |
| H2 | `text-lg` | 18px | 模块标题（顶栏） |
| H3 | `text-base` | 16px | 卡片标题 |
| Body | `text-sm` | 14px | 表格、表单、正文 |
| Caption | `text-xs` | 12px | 说明文字、表头 |
| KPI | `text-2xl font-bold` | 24px | 仪表盘指标数值 |
| 微标 | `text-[10px]` | 10px | 图表轴标签 |

## 13. 布局规范

### 13.1 整体框架

```
┌──────────────────────────────────────────────┐
│ 侧边栏 224px  │  顶栏（模块标题 + 刷新 + 用户）  │
│ (w-56)        ├──────────────────────────────┤
│               │                              │
│  Logo + 菜单   │  内容区 #adminContent         │
│               │  padding: 1.5rem (p-6)       │
│               │  overflow-y: auto            │
│               │                              │
│  底部：角色信息  │                              │
└───────────────┴──────────────────────────────┘
```

| 区域 | 尺寸 | 样式 |
|------|------|------|
| 侧边栏宽度 | 224px (`w-56`) | `bg-slate-900` 固定左侧 |
| 顶栏高度 | ~52px (`py-3`) | `bg-white border-b border-slate-200` |
| 内容区内边距 | 24px (`p-6`) | `overflow-y-auto` |
| 登录页 | 全屏居中 | `min-h-screen` + 渐变背景 |

### 13.2 登录页

```
┌─────────────────────────────────────┐
│       渐变背景 (slate-900 → slate-800)  │
│                                     │
│        ┌─────────────────┐          │
│        │  YD 后台管理      │          │
│        │  企业管理运营平台   │          │
│        │                  │          │
│        │  账号 [________]  │          │
│        │  密码 [________]  │          │
│        │  [    登录    ]   │          │
│        │                  │          │
│        │  演示账号提示框     │          │
│        └─────────────────┘          │
│           max-w-sm, rounded-2xl      │
└─────────────────────────────────────┘
```

### 13.3 Modal 与 Drawer

| 组件 | 尺寸 | 触发 | 用途 |
|------|------|------|------|
| Modal | `max-w-lg` 居中 | `.modal.show` → `display:flex` | 新增/编辑/删除确认 |
| Drawer | 右侧滑出 `max-w-[480px]` | `transform: translateX(100%→0)` | 详情查看、复杂表单 |

## 14. 表格与表单规范

### 14.1 表格规范

```css
table { width: 100%; border-collapse: collapse; font-size: .85rem; }
th {
  text-align: left;
  color: #6b7280;
  font-weight: 500;
  padding: .6rem .8rem;
  border-bottom: 1px solid #e5e7eb;
  background: #fafafa;
}
td { padding: .6rem .8rem; border-bottom: 1px solid #f1f5f9; }
tr:hover td { background: #f8fafc; }
```

| 元素 | 样式 |
|------|------|
| 表头 | `bg-gray-50` + `text-gray-500` + `font-medium` |
| 表体行 | 默认白底，hover `#f8fafc` |
| 行分隔 | `border-bottom: 1px solid #f1f5f9` |
| 图片列 | `h-10 w-16 object-cover rounded border` |
| 长文本列 | `max-w-[220px] truncate` + `title` 悬停显示全文 |
| 空数据 | `text-slate-400 text-center py-6` "暂无数据" |

### 14.2 表单规范

| 元素 | 样式 | 校验 |
|------|------|------|
| 输入框 | `border-slate-300 rounded-lg px-3 py-2.5 focus:border-primary focus:outline-none` | required 属性 + 失焦校验 |
| 下拉框 | 同输入框（SELECTS 配置驱动） | — |
| 多行文本 | `rows="6"` textarea（新闻正文/产品描述） | — |
| 文件上传 | `<input type="file" accept="image/*">` + 本地预览 | FileReader |
| 只读字段 | 新增时不渲染（READONLY 配置） | — |
| label | `block text-sm text-slate-500 mb-1` | — |

---

# 第四篇 · 信息架构与导航

## 15. 前台站点地图

```
首页
├─ 产品中心（筛选：系列/空间/品类） → 产品详情（SKU/价格/库存/加购）
├─ 案例（实景案例列表） → 案例详情
├─ 新闻（企业新闻 / 行业资讯） → 新闻详情
├─ 招聘（社会招聘 / 校园招聘） → 岗位详情 + 投递 + 我的投递
├─ 关于我们（关于YD / 发展历程 / 品牌介绍 / 联系我们）
├─ 下载中心（画册PDF，仅页脚/搜索触达）
├─ 在线预约（表单弹窗）
├─ 在线客服（浮窗 + 智能应答）
├─ 站内搜索（弹窗 + 结果聚合）
├─ 购物车结算 → 我的订单
└─ 会员中心（登录/注册/个人中心/我的订单/我的预约）
```

## 16. 前台导航结构

### 16.1 顶部导航（PC 端 lg+）

```
┌─────────────────────────────────────────────────────────────────┐
│ [YD] YD家具  │ 首页 产品中心▼ 案例 新闻▼ 招聘▼ 关于我们▼ │ 🔍 📅 💬 🛒 会员登录 │
└─────────────────────────────────────────────────────────────────┘
                  一级导航(6项) + 二级下拉       右侧操作区(5项)
```

**一级导航**：首页 / 产品中心 / 案例 / 新闻 / 招聘 / 关于我们

**二级下拉**：

| 一级 | 二级项 | 路由 |
|------|--------|------|
| 产品中心 | 全部产品 / 客厅精选 / 卧室精选 / 书房精选 / 茶室精选 / 办公家具 | `?space=客厅` 等 |
| 新闻 | 企业新闻 / 行业资讯 | `#corp` / `#ind` |
| 招聘 | 社会招聘 / 校园招聘 | `#social` / `#campus` |
| 关于我们 | 关于YD / 发展历程 / 品牌介绍 / 联系我们 | `#about-yd` / `#history` / `#brand` / `#contact` |

**右侧操作区**：站内搜索(🔍) / 在线预约(📅) / 在线客服(💬) / 购物车(🛒+badge) / 会员登录(按钮→登录后变头像)

**导航样式**：
- `sticky top-0 z-50 bg-sand/95 backdrop-blur border-b border-stone-200`
- 导航链接：hover 下划线展开动画（gold 色，200ms）
- 激活态：`text-ink font-medium` + 下划线满宽

### 16.2 移动端导航（<lg）

- 汉堡菜单按钮 `lg:hidden`
- 点击展开手风琴式折叠菜单
- 二级菜单使用 `<details>` 标签实现展开/收起
- 底部含在线预约 + 会员登录按钮

### 16.3 全局浮窗

- **客服浮窗**：`fixed right-5 bottom-5 z-50 w-14 h-14 rounded-full bg-gold`，hover 放大 1.05
- **Toast**：`fixed bottom-40px center`，2.2s 自动消失

## 17. 后台菜单结构

### 17.1 角色权限映射

| 模块 key | 模块名 | admin | editor | product | service | order |
|---------|--------|:-----:|:------:|:-------:|:-------:|:-----:|
| dashboard | 仪表盘 | ✓ | ✓ | ✓ | ✓ | ✓ |
| carousel | 轮播图管理 | ✓ | ✓ | ✓ | — | — |
| product | 产品管理 | ✓ | — | ✓ | — | — |
| category | 分类管理（v1.1 新增） | ✓ | — | ✓ | — | — |
| case | 案例管理 | ✓ | ✓ | — | — | — |
| news | 新闻管理 | ✓ | ✓ | — | — | — |
| recruit | 招聘管理 | ✓ | ✓ | — | — | — |
| about | 关于我们管理 | ✓ | ✓ | — | — | — |
| booking | 预约管理 | ✓ | — | — | ✓ | ✓ |
| message | 留言管理 | ✓ | ✓ | — | ✓ | — |
| order | 订单管理 | ✓ | — | ✓ | ✓ | ✓ |
| system | 系统管理 | ✓ | — | — | — | — |

> **实际菜单顺序（v1.1 对齐实现）**：仪表盘 → 产品管理 → 分类管理 → 资讯管理 → 招聘管理 → 案例管理 → 订单管理 → 预约管理 → 会员管理 → 留言管理 → 部门管理

### 17.2 菜单渲染逻辑

```javascript
// 登录后按角色过滤模块
buildSideMenu() {
  sideMenu.innerHTML = currentRole.modules.map(m =>
    `<div class="side-item ${m===currentMod?'active':''}" onclick="goMod('${m}')">${MOD_LABEL[m]}</div>`
  ).join('');
}
```

- 菜单项样式：`side-item`（`cursor-pointer` + `rounded-lg` + `hover:bg-slate-800` + `active:bg-primary`）
- 底部显示当前角色头像 + 角色名 + 角色 key + 退出按钮

## 18. 页面路由与跳转逻辑

### 18.1 前台路由

| 页面 | 文件 | 路由参数 |
|------|------|---------|
| 首页 | `prototype_前台首页_YD家具.html` | — |
| 产品中心 | `prototype_产品中心_YD家具.html` | `?space=客厅`（空间筛选） |
| 产品详情 | `prototype_产品详情_YD家具.html` | `?id=1` 或 `?series=&cat=&model=` |
| 案例展示 | `prototype_案例展示_YD家具.html` | — |
| 新闻资讯 | `prototype_新闻资讯_YD家具.html` | `#corp` / `#ind`（hash 锚点） |
| 新闻详情 | `prototype_新闻详情_YD家具.html` | `?id=1` |
| 招聘 | `prototype_招聘_YD家具.html` | `#social` / `#campus` |
| 关于我们 | `prototype_关于我们_YD家具.html` | `#about-yd` / `#history` / `#brand` / `#contact` |
| 下载中心 | `prototype_下载中心_YD家具.html` | — |
| 购物车结算 | `prototype_购物车结算_YD家具.html` | — |
| 我的订单 | `prototype_我的订单_YD家具.html` | — |
| 我的预约 | `prototype_我的预约_YD家具.html` | — |

### 18.2 本地存储 Key

| Key | 用途 | 类型 |
|-----|------|------|
| `yd_member` | 会员登录态 | `{name, phone}` JSON（仅昵称+手机号，**密码不落地存储**） |
| `yd_cart` | 购物车 | `[{id,name,price,img,qty,color,size}]` |
| `yd_orders` | 订单列表 | `[{no,items,total,status,created,eta,log}]` |
| `yd_booking` | 预约记录 | `{name,phone,type,msg,time,status}` |
| `yd_applications` | 招聘投递 | `[{job,stage,time}]` |
| `yd_admin_logged` | 后台登录态 | `'1'` |
| `yd_admin_role` | 后台角色 | `'admin'` 等 |

---

# 第五篇 · 前台页面规格

> 每页统一规格：路由 / 布局结构 / 核心区块 / 交互行为 / 响应式 / 验收要点

## 19. 首页

**路由**：`prototype_前台首页_YD家具.html`

### 布局结构

```
┌─────────────────────────────────────────────┐
│ 顶部导航（sticky）                             │
├─────────────────────────────────────────────┤
│ Hero 轮播（h-420px / sm:h-520px）              │
│ 6 张幻灯片 + 左右箭头 + 圆点指示器              │
├─────────────────────────────────────────────┤
│ 推荐产品（grid-cols-2 md:grid-cols-4 gap-6）   │
├─────────────────────────────────────────────┤
│ 最新案例（横向卡片 / grid）                     │
├─────────────────────────────────────────────┤
│ 新闻头条（列表 / 卡片）                        │
├─────────────────────────────────────────────┤
│ 页脚（4 列：品牌/关于/快捷入口/联系方式）        │
└─────────────────────────────────────────────┘
```

### 核心区块

| 区块 | 组件 | 数据来源 | 交互 |
|------|------|---------|------|
| Hero 轮播 | Carousel | 后台轮播图管理（6 张） | 整张可点击 `data-href` 跳转；hover 显示提示；左右箭头切换；圆点跳转 |
| 推荐产品 | ProductCard ×4 | 产品列表（buy=true） | 点击跳转产品详情 |
| 最新案例 | CaseCard ×3 | 案例列表 | 点击跳转案例详情 |
| 新闻头条 | NewsCard ×3 | 新闻列表 | 点击跳转新闻详情 |

### 轮播图交互

- 自动播放：5s 间隔切换
- 切换方式：opacity 渐变（600ms）
- 点击跳转：`data-href` 指向产品详情/案例/预约/产品中心
- 第 4 张 `data-book="1"` 触发预约弹窗
- hover 显示 `.slide-hint` 提示文字

### 验收要点

- [ ] 6 张轮播图均可点击跳转
- [ ] 轮播自动播放 + 手动箭头 + 圆点三种切换方式
- [ ] 移动端 Hero 高度 420px，桌面端 520px
- [ ] 推荐产品 4 列（桌面）/ 2 列（移动）
- [ ] 页脚含下载中心快捷入口

## 20. 产品中心

**路由**：`prototype_产品中心_YD家具.html`（支持 `?space=客厅` 筛选）

### 布局结构

```
┌─────────────────────────────────────────────┐
│ Banner 区（bg-ink text-sand py-12）           │
│ "PRODUCTS" + "产品中心" + 副标题               │
├─────────────────────────────────────────────┤
│ 筛选区                                         │
│ 系列：[全部] [胡桃禮] [柏悦] [如意春] ...      │
│ 空间：[全部] [客厅] [卧室] [书房] ...          │
│ 品类：[全部] [沙发] [床] [桌] ...             │
│ 关键词：[________________]                    │
├─────────────────────────────────────────────┤
│ "共 20 款产品"                                │
│ 产品网格 grid-cols-2 md:grid-cols-4 gap-6     │
├─────────────────────────────────────────────┤
│ 页脚                                          │
└─────────────────────────────────────────────┘
```

### 筛选交互

- **三维筛选**：系列 / 空间 / 品类，使用 chip 组件（`rounded-full`）
- **URL 参数**：`?space=客厅` 初始化空间筛选
- **关键词搜索**：`oninput` 实时过滤
- **chip 样式**：默认 `border-stone-300 text-stone2`，激活 `bg-gold text-ink border-gold`

### 产品卡片

```
┌──────────────────┐
│   占位图 (4:3)    │  ← prod-thumb 渐变 + SVG 图标
│                  │
├──────────────────┤
│ 胡桃禮 · 客厅     │  ← series + space（text-xs text-gold）
│ 实木沙发          │  ← name（font-semibold text-ink）
│ ¥12,800          │  ← price（text-gold font-bold）
│ [库存 12 件]     │  ← stock（text-xs）
└──────────────────┘
```

### 验收要点

- [ ] 三维筛选可组合使用
- [ ] `?space=` URL 参数正确初始化筛选
- [ ] 关键词实时过滤
- [ ] 产品卡片点击跳转详情页
- [ ] 共 20 个产品数据

## 21. 产品详情

**路由**：`prototype_产品详情_YD家具.html?id=1`（或 `?series=&cat=&model=`）

### 布局结构

```
┌─────────────────────────────────────────────┐
│ 面包屑：首页 / 产品中心 / 胡桃禮·实木沙发        │
├──────────────────┬──────────────────────────┤
│                  │ 胡桃禮 · 客厅 · 沙发       │
│  主图 (prod-thumb) │ 实木沙发                  │
│  w-full h-80     │ ¥12,800                  │
│                  │ 库存 12 件 · 支持在线下单    │
│                  │                          │
│ [图1][图2][图3]  │ 颜色：[原木色][深胡桃][墨黑] │
│                  │ 尺寸：[单人][双人][三人]    │
│                  │ [加入购物车] [立即购买]    │
├──────────────────┴──────────────────────────┤
│ 产品参数                                      │
│ 材质：黑胡桃实木                                │
│ 风格：现代简约                                 │
│ 适用空间：客厅                                 │
│ 是否定制：否                                   │
│ 标签：客厅/实木                                │
│ 描述：胡桃禮实木沙发以北美黑胡桃为主材...        │
└─────────────────────────────────────────────┘
```

### SKU 选择交互

- 颜色/尺寸使用 `.sku-opt` 组件
- 激活态：`active` class（`bg-gold text-ink`）
- 选择后更新 `curColor` / `curSize` 变量

### 加购/购买

- **加入购物车**：写入 `yd_cart`（同 ID + 同 color + 同 size 则 qty++），更新徽标，toast 提示
- **立即购买**：未登录 → 弹登录弹窗 + toast"请先登录会员"；已登录 → 加购后 600ms 跳结算页
- **仅展示产品**（`buy=false`）：toast"该商品仅展示，暂不支持在线下单"

### 验收要点

- [ ] 图集缩略图可切换主图
- [ ] SKU 颜色/尺寸可选择
- [ ] 加购后购物车徽标数字 +1 并弹性动画
- [ ] 立即购买需登录态校验
- [ ] 仅展示产品不显示购买按钮或点击提示

## 22. 案例展示

**路由**：`prototype_案例展示_YD家具.html`

### 布局

- Banner 区 + 筛选（空间/风格）+ 案例卡片网格
- 案例卡片：实景图 + 空间/风格标签 + 标题 + 所用产品
- 点击进入案例详情（图集 + 所用产品 + 户型/面积/描述）

## 23. 新闻资讯

**路由**：`prototype_新闻资讯_YD家具.html#corp`（企业新闻）/ `#ind`（行业资讯）

### 布局

- 二级导航通过 hash 锚点驱动分类
- 新闻卡片：封面图 + 分类标签 + 标题 + 日期 + 摘要
- 点击跳转新闻详情页（`prototype_新闻详情_YD家具.html?id=`）
- 支持分页

## 24. 新闻详情

**路由**：`prototype_新闻详情_YD家具.html?id=1`

### 布局

- 面包屑 + 标题 + 发布时间/分类
- 富文本正文渲染
- 相关推荐（同分类新闻）

## 25. 招聘

**路由**：`prototype_招聘_YD家具.html#social`（社招）/ `#campus`（校招）

### 布局

```
┌─────────────────────────────────────────────┐
│ Banner 区                                     │
├─────────────────────────────────────────────┤
│ [社会招聘] [校园招聘] [我的投递]  ← chip 切换    │
├─────────────────────────────────────────────┤
│ 岗位卡片列表                                    │
│ ┌─────────────────────────┐                  │
│ │ 实木家具结构设计师  研发设计  │                  │
│ │ 上海                     │                  │
│ │ 负责实木家具结构设计...    │                  │
│ │ [投递简历]               │                  │
│ └─────────────────────────┘                  │
├─────────────────────────────────────────────┤
│ 页脚                                          │
└─────────────────────────────────────────────┘
```

### 我的投递进度跟踪

5 阶段进度条：

```
  ①          ②          ③          ④          ⑤
职位申请  →  简历筛选  →  面试考核  →  Offer签约 → 入职报到
  ●———————●———————————●———————————○———————————○
 gold     gold       gold       stone      stone
```

- 已完成阶段：`bg-gold text-ink`（实心圆 + gold 连线）
- 未完成阶段：`bg-stone-200 text-stone-500`（空心圆 + stone 连线）
- 当前阶段：`text-gold font-semibold`（文字高亮）
- 支持撤销申请（`splice` 删除 + toast）

### 投递交互

- 未登录点击投递 → 弹登录弹窗 + toast"请先登录会员再投递"
- 已登录 → 弹投递表单 → 提交写入 `yd_applications` → toast"投递成功，可在「我的投递」跟踪进度"

### 验收要点

- [ ] hash 锚点正确切换社招/校招/我的投递
- [ ] 投递需登录态校验
- [ ] 我的投递 5 阶段进度正确渲染
- [ ] 撤销申请可用

## 26. 关于我们

**路由**：`prototype_关于我们_YD家具.html#about-yd` / `#history` / `#brand` / `#contact`

### 发展历程时间线

```
  1953      1985      2008      2020      2026      2053
品牌创立 → 规模化 → 全国零售 → 数字化 → 温润生活 → 百年愿景
   ●—————————●——————————●——————————●——————————●——————————○
 gold      gold      gold      gold      gold      gold(愿景)
```

- 横向时间线（`flex` 布局，6 节点）
- 节点：金色圆点 `bg-gold ring-4 ring-gold/20` + 卡片（年份/标题/描述）
- 连接线：`bg-gradient-to-r from-gold/60 to-gold/20`
- 覆盖品牌"百年店"叙事（1953 创立 → 2053 愿景）

### 联系我们

| 字段 | 内容 |
|------|------|
| 公司地址 | 上海市黄浦区南京东路 1 号 YD 大厦 |
| 销售热线 | 400-888-8888（`tel:` 链接） |
| 服务热线 | 400-888-9999（`tel:` 链接） |
| 邮箱 | contact@yd-home.com |
| 社交媒体 | 微信 / 视频号 / 抖音 / 小红书 |
| 预约按钮 | "预约到店咨询" → 打开预约弹窗 |

### 验收要点

- [ ] 4 个区块通过 hash 锚点定位
- [ ] 时间线横向渲染 6 节点
- [ ] 联系我们电话为 `tel:` 可点击链接
- [ ] 预约按钮触发预约弹窗

## 27. 下载中心

**路由**：`prototype_下载中心_YD家具.html`（仅页脚/搜索触达）

### 布局

- 画册 PDF 列表（3 份）
- 每项：标题 + 文件信息 + 下载按钮
- 下载交互：点击 → "下载中…" → "下载完成" 状态切换

## 28. 购物车结算

**路由**：`prototype_购物车结算_YD家具.html`

### 布局

```
┌─────────────────────────────────────────────┐
│ 购物车（标题）                                 │
├─────────────────────────────────────────────┤
│ ┌──────────────────────────────────────┐    │
│ │ [图] 胡桃禮·实木沙发  ¥12,800         │    │
│ │      [- 1 +]  [删除]                 │    │
│ └──────────────────────────────────────┘    │
│ ┌──────────────────────────────────────┐    │
│ │ [图] 柏悦·真皮软床    ¥8,800          │    │
│ │      [- 1 +]  [删除]                 │    │
│ └──────────────────────────────────────┘    │
├─────────────────────────────────────────────┤
│ 小计：¥21,600                                │
│ 总计：¥21,600                                │
│ [提交订单]                                   │
├─────────────────────────────────────────────┤
│ 空状态：购物车为空（cartEmpty）                 │
└─────────────────────────────────────────────┘
```

### 交互

- **数量调整**：`-` / `+` 按钮，最小 1
- **删除**：移除该项 + toast"已移除"
- **提交订单**：未登录 → 弹登录 + toast"请先登录会员再结算"；空车 → toast"购物车为空"；正常 → 生成订单写入 `yd_orders`，清空购物车，800ms 跳转我的订单
- **订单数据**：`{no, items, total, status:'待付款', created, eta:3天后, log:['待付款·等待仓库拣货']}`

## 29. 我的订单 / 我的预约

### 我的订单

**路由**：`prototype_我的订单_YD家具.html`

- 订单列表（来自 `yd_orders`）
- 每项：订单号 + 商品列表 + 总金额 + 状态 + 创建时间 + 预计送达
- 状态流转：待付款 → 已付款 → 已发货 → 已完成（退款中 / 已退款 / 已关闭 为异常分支）

### 我的预约

**路由**：`prototype_我的预约_YD家具.html`

- 预约列表（来自 `yd_booking`）
- 每项：姓名 + 电话 + 需求类型 + 留言 + 状态 + 时间

---

# 第六篇 · 后台页面规格

> 每模块统一规格：菜单 key + 角色权限 + 页面布局 + 数据字段 + 操作 + 弹窗

## 30. 登录页

**路由**：`prototype_后台管理_YD家具.html`（初始状态）

### 布局

- 全屏渐变背景 `bg-gradient-to-br from-slate-900 to-slate-800`
- 居中卡片 `max-w-sm rounded-2xl shadow-xl p-8`
- 标题"YD 后台管理" + 副标题"企业管理运营平台"
- 表单：账号 + 密码 + 登录按钮
- 演示账号提示框（5 个角色 + 密码 123456）

### 登录逻辑

```javascript
function doLogin(e) {
  // 1. 校验密码（演示密码 123456）
  // 2. 匹配角色 key（ROLES[u] || 'admin'）
  // 3. 写入 sessionStorage + localStorage
  // 4. enterApp() → 隐藏登录页 + 显示主框架 + 渲染菜单 + 默认进入仪表盘
}
```

### 验收要点

- [ ] 密码错误 toast 提示
- [ ] 登录成功跳转仪表盘
- [ ] 5 个角色均可登录
- [ ] 会话过期重定向登录页

## 31. 仪表盘

**菜单 key**：`dashboard` ｜ **角色权限**：全部

### 布局

```
┌──────────────────────────────────────────────┐
│ KPI 卡片区（grid-cols-2 md:grid-cols-5）       │
│ ┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐         │
│ │访问量││预约量││留言量││订单量││销售额│         │
│ │7,239││  2  ││  2  ││  2  ││21,000│         │
│ └─────┘└─────┘└─────┘└─────┘└─────┘         │
├──────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐           │
│ │ 近 7 日访问量   │ │ 销售额趋势(万元)│           │
│ │  柱状图        │ │  折线图        │           │
│ │  带数值标注     │ │  带数值标注     │           │
│ │  周一~周日     │ │  周一~周日     │           │
│ └──────────────┘ └──────────────┘           │
└──────────────────────────────────────────────┘
```

### KPI 卡片

| 指标 | 数据来源 | 格式 |
|------|---------|------|
| 访问量(PV/UV) | seedStats() 动态计算 | `toLocaleString()` |
| 预约量 | `DB.booking.length` | 整数 |
| 留言量 | `DB.message.length` | 整数 |
| 订单量 | `DB.order.length` | 整数 |
| 销售额(趋势) | seedStats() 计算 | `toLocaleString()` |

### 图表

- **柱状图**：近 7 日访问量，`bg-primary` 柱条，顶部数值标注，底部周一~周日标签
- **折线图**：销售额趋势，SVG `polyline` + 圆点 + 数值标注 + 轴标签

## 32. 轮播图管理

**菜单 key**：`carousel` ｜ **角色权限**：admin / editor / product

### 表格字段

| 列名 | 字段 | 类型 | 可编辑 |
|------|------|------|--------|
| 图片 | img | 图片上传 | ✓ |
| 标题 | title | 文本 | ✓ |
| 位置 | pos | 下拉（首页/案例详情/新闻） | ✓ |
| 跳转类型 | link | 下拉（产品/案例/新闻） | ✓ |
| 系列 | series | 文本 | ✓ |
| 类别 | cat | 文本 | ✓ |
| 型号 | model | 文本 | ✓ |
| 排序 | sort | 数字 | ✓ |
| 启用 | on | 下拉（是/否） | ✓ |

### 操作

- 新增 / 编辑（Modal 表单）/ 删除（二次确认）/ 预览

## 33. 产品管理

**菜单 key**：`product` ｜ **角色权限**：admin / product ｜ **路由**：`/admin/products`（列表）、`/admin/products/new`（新增）、`/admin/products/edit/:id`（编辑）

### 表格字段（v1.1 对齐开发实现，共 12 列）

| 列名 | 字段 | 类型 | 说明 |
|------|------|------|------|
| ID | id | 只读 | 自增主键 |
| 封面 | cover_url | 图片 | 缩略图 48×48，无图显示占位 |
| 产品标题 | name | 文本 | 主标题，加粗 |
| 副标题 | subtitle | 文本 | 次行小字，灰色 |
| 系列 | series_name | 文本 | 关联 categories.type='series' |
| 空间 | space_name | 文本 | 关联 categories.type='space' |
| 品类 | category_name | 文本 | 关联 categories.type='category' |
| 最低价 / 最高价 | min_price_cents / max_price_cents | 金额 | **存储单位分，展示 ÷100 转元**，如 ¥9.80 – 10.80 |
| 排序 | sort | 数字 | 数值大者靠前（前台优先级高） |
| 状态 | status | Tag | 草稿灰 / 上架绿 / 下架橙 |
| 创建时间 | created_date | 时间 | — |
| 操作 | — | 按钮组 | 编辑 / 上架·下架切换 / 删除（二次确认 Modal） |

**筛选栏**：标题关键词搜索 + 空间下拉（读取 `/admin/categories?kind=space`）+ 状态下拉（`status_filter`）。

### 产品表单（新增 / 编辑）

| 字段 | 控件 | 必填 | 说明 |
|------|------|------|------|
| 产品标题 | Input | ✅ | 1–128 字 |
| 状态 | Radio | ✅ | 草稿 draft / 上架 on_sale / 下架 off_sale |
| 副标题 | Input | - | ≤255 字 |
| **风格** | Input | - | **v1.1 新增**（products.style），如 现代简约 / 新中式 / 轻奢风 |
| 系列 / 空间 / 品类 | Select 下拉 | 三选一 | 选项来自分类管理接口（不再手输） |
| 封面图 | Upload | - | 单图，上传后回显缩略图 |
| 产品详情 | 富文本 HTML | - | 详情页渲染 |
| 最低价 / 最高价 | InputNumber | - | **单位：分**；前端校验 最低价 ≤ 最高价（后端 CHECK `chk_products_amount` 双保险） |
| 排序号 | InputNumber | - | 默认 0，数值大靠前 |

### SKU 与库存

- 预留：`product_skus` 表（颜色/尺寸/材质组合变体），当前实现未接入，后续迭代启用
- 库存：SKU 级，后台可调整（预留）

---

## 33.1 分类管理（v1.1 新增）

**菜单 key**：`category` ｜ **角色权限**：admin / product ｜ **路由**：`/admin/categories`

> 空间 / 系列 / 品类 三类字典统一维护，**前台产品中心筛选栏自动同步**（读取 `/public/categories?kind=`）。

### 页面布局

- 顶部 **Tabs 三个**：`空间` / `系列` / `品类`
- 每个 Tab 一张表格 + 右上「新增」按钮

### 表格字段

| 列名 | 字段 | 说明 |
|------|------|------|
| ID | id | 只读 |
| 名称 | name | 中文名，如 客厅 / 胡桃禮 / 实木餐桌 |
| 排序 | sort | 数值大靠前 |
| 状态 | is_activate | 启用 Tag / 禁用 |
| 操作 | — | 编辑（Modal）/ 删除（二次确认，被产品引用时后端拒绝 → 400）/ 启用·禁用 |

### 新增 / 编辑（Modal）

- 名称（必填）、排序号（选填，默认 0）、启用状态开关
- 保存后**前台筛选栏实时出现新分类**（react-query 轮询 30s + 聚焦刷新）

### 验收要点

1. 后台新增空间分类「书房」→ 前台产品中心左侧筛选「空间」立即出现「书房」
2. 删除被产品引用的分类 → 弹「该分类已被产品引用，无法删除」错误提示
3. 分类禁用后，前台筛选栏不再显示该分类

## 34–41. 其他后台模块

### 案例管理（case）

角色：admin / editor ｜ 字段：标题/空间/风格/所含产品(数组)/创建时间/修改时间

### 新闻管理（news）

角色：admin / editor ｜ 字段：标题/分类(下拉)/内容(textarea)/状态(下拉)/发布时间

### 招聘管理（recruit）

角色：admin / editor ｜ 字段：岗位/类型(下拉)/部门(下拉)/状态(下拉)/开始时间(只读)/结束时间
- 投递状态 5 阶段流转与前台"我的投递"对齐

### 关于我们管理（about）

角色：admin / editor ｜ 4 区块列表（关于YD/发展历程/品牌介绍/联系我们）
- 点击"维护"打开 Modal 编辑区块内容
- 发展历程含时间线节点维护

### 预约管理（booking）

角色：admin / service / order ｜ 字段：姓名/电话/需求类型(下拉)/状态(下拉)/来源(下拉)/预约时间

### 留言管理（message）

角色：admin / editor / service ｜ 字段：姓名/来源(下拉)/内容/状态(下拉)/留言时间/回复时间
- "回复"按钮打开回复表单，保存后状态标记"已回复"

### 订单管理（order）

角色：admin / product / service / order ｜ 字段：订单号/用户/金额/状态(下拉)
- 状态：待付款/已付款/已发货/已完成/退款中/已退款/已关闭

### 系统管理（system）

角色：admin ｜ 含两个子模块：
1. **角色权限矩阵**：5 角色 × 11 模块的 ✓/— 矩阵表
2. **操作审计日志**：操作/操作人/对象/IP/时间（示例数据）

---

# 第七篇 · 组件库规范

## 42. 前台通用组件

### 42.1 Button 按钮

| 变体 | 样式 | 用途 |
|------|------|------|
| Primary | `bg-gold text-white hover:bg-amber-700` | 主要操作（登录/提交/预约） |
| Outline | `border border-ink text-ink hover:bg-ink hover:text-white` | 次要操作（会员登录按钮） |
| Gold（CSS类） | `.btn-gold { background:#CA8A04;color:#1C1917; }` hover→`#B45309` | 弹窗内主按钮 |
| Ghost | `hover:bg-stone-100` | 图标按钮 |

```html
<!-- Primary -->
<button class="px-3 py-2 rounded-md bg-gold text-white text-sm font-medium hover:bg-amber-700 transition-colors cursor-pointer">在线预约</button>

<!-- Outline -->
<button class="px-3 py-2 rounded-md border border-ink text-ink text-sm hover:bg-ink hover:text-white transition-colors cursor-pointer">会员登录</button>
```

### 42.2 NavBar 导航栏

```html
<header class="sticky top-0 z-50 bg-sand/95 backdrop-blur border-b border-stone-200">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <div class="flex items-center justify-between h-16">
      <!-- Logo -->
      <!-- Nav (hidden lg:flex) -->
      <!-- Actions (hidden md:flex) -->
      <!-- Mobile menu button (lg:hidden) -->
    </div>
  </div>
</header>
```

### 42.3 ProductCard 产品卡片

```html
<a href="产品详情?id=1" class="block bg-white rounded-xl border border-stone-200 overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
  <div class="prod-thumb aspect-[4/3] flex items-center justify-center">
    <!-- SVG 家具图标 -->
  </div>
  <div class="p-4">
    <p class="text-xs text-gold">胡桃禮 · 客厅</p>
    <h3 class="font-semibold text-ink mt-1">实木沙发</h3>
    <p class="text-gold font-bold mt-2">¥12,800</p>
    <p class="text-xs text-stone-500 mt-1">库存 12 件</p>
  </div>
</a>
```

### 42.4 Carousel 轮播

```html
<section class="relative h-[420px] sm:h-[520px] overflow-hidden bg-ink">
  <div id="carouselTrack" class="relative w-full h-full">
    <div class="carousel-slide absolute inset-0" data-href="跳转URL">
      <!-- 幻灯片内容 -->
    </div>
  </div>
  <button id="prevSlide" class="absolute left-4 top-1/2 -translate-y-1/2">‹</button>
  <button id="nextSlide" class="absolute right-4 top-1/2 -translate-y-1/2">›</button>
  <div id="carouselDots" class="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2"></div>
</section>
```

### 42.5 Modal 弹窗

```html
<div id="xxxModal" class="modal-mask" onclick="if(event.target===this)this.classList.remove('show')">
  <div class="bg-white rounded-2xl w-full max-w-md p-7">
    <div class="flex justify-between items-center mb-5">
      <h3 class="font-head text-2xl text-ink">标题</h3>
      <button class="text-stone-400 text-2xl" onclick="closeModal('xxxModal')">&times;</button>
    </div>
    <!-- 内容 -->
  </div>
</div>
```

```css
.modal-mask {
  position: fixed; inset: 0;
  background: rgba(12,10,9,.6);
  backdrop-filter: blur(3px);
  z-index: 100;
  display: none;
  align-items: center; justify-content: center;
  padding: 1rem;
}
.modal-mask.show { display: flex; }
```

### 42.6 ChatWidget 客服浮窗

```html
<!-- 悬浮按钮 -->
<button class="fixed right-5 bottom-5 z-50 w-14 h-14 rounded-full bg-gold text-ink shadow-xl flex items-center justify-center hover:scale-105 transition" aria-label="在线客服">
  <svg>...</svg>
</button>

<!-- 会话浮窗 -->
<div id="chatModal" class="modal-mask">
  <div class="bg-white rounded-2xl w-full max-w-md h-[480px] flex flex-col">
    <!-- 头部：在线状态 + 标题 + 关闭 -->
    <!-- 消息区：chat-body h-320px overflow-y-auto -->
    <!-- 快捷问题：chat-quick 胶囊按钮 -->
    <!-- 输入区：input + 发送按钮 -->
  </div>
</div>
```

### 42.7 其他前台组件

| 组件 | 规格 |
|------|------|
| CaseCard | 同 ProductCard，标签为空间/风格 |
| NewsCard | 封面 + 分类标签 + 标题 + 日期 |
| Chip 筛选标签 | `rounded-full border px-4 py-1.5` + active 态 `bg-gold text-ink` |
| Toast | `fixed bottom-40px center` + `bg-ink text-white border-gold` + 2.2s 消失 |
| Avatar | `w-10 h-10 rounded-full bg-gold text-ink font-bold` |
| Timeline | 横向 6 节点 + 金色圆点 + 渐变连线 |
| Footer | 4 列 grid + 深色 bg-ink + gold 链接 hover |

## 43. 前台业务组件

### 43.1 BookForm 预约表单

```html
<form id="bookForm" onsubmit="return doBooking(event)">
  <input id="bkName" required placeholder="姓名" class="...">
  <input id="bkPhone" required placeholder="电话" class="...">
  <select id="bkType" class="...">
    <option>到店预约</option>
    <option>产品咨询</option>
    <option>定制需求</option>
    <option>其它</option>
  </select>
  <textarea id="bkMsg" rows="3" placeholder="留言" class="..."></textarea>
  <button class="btn-gold w-full py-2.5 rounded-lg">提交预约</button>
</form>
```

### 43.2 LoginForm 登录表单

- 手机号 + 密码
- 登录成功：写 `yd_member` + 关弹窗 + 头像替换按钮 + toast

### 43.3 投递进度组件

5 阶段横向进度条，详见 §25。

## 44. 后台通用组件

### 44.1 DataTable 数据表格

```javascript
// TABLE_CFG 配置驱动
const TABLE_CFG = {
  product: {
    cols: [['series','系列'],['cat','类别'],...],
    ops: true  // 显示操作列
  }
};
```

```html
<table id="tbl_product">
  <tr><th>系列</th><th>类别</th>...<th>操作</th></tr>
  <tr>
    <td>胡桃禮</td><td>沙发</td>...
    <td>
      <span class="act-btn act-edit" onclick="openEdit('product',1)">编辑</span>
      <span class="act-btn act-del" onclick="openDel('product',1)">删除</span>
    </td>
  </tr>
</table>
```

### 44.2 ActBtn 操作按钮

```css
.act-btn { cursor: pointer; padding: .25rem .6rem; border-radius: 6px; font-size: .8rem; transition: all .15s; }
.act-edit { color: #1677ff; }
.act-edit:hover { background: #e6f0ff; }
.act-del { color: #ef4444; }
.act-del:hover { background: #fee2e2; }
.act-add { color: #16a34a; }
.act-add:hover { background: #dcfce7; }
```

### 44.3 KpiCard 指标卡

```html
<div class="kpi">
  <p class="text-xs text-slate-400">访问量(PV/UV)</p>
  <p class="text-2xl font-bold text-slate-800 mt-1">7,239</p>
</div>
```

### 44.4 SideMenu 侧边栏菜单

```html
<aside class="w-56 bg-slate-900 text-white shrink-0 flex flex-col">
  <div class="px-5 py-4 border-b border-slate-700">YD 后台</div>
  <nav id="sideMenu" class="flex-1 p-3 space-y-1">
    <div class="side-item active" data-mod="dashboard">仪表盘</div>
    <!-- 角色过滤后的菜单项 -->
  </nav>
  <div class="p-3 border-t border-slate-700">
    <!-- 角色头像 + 名称 + 退出 -->
  </div>
</aside>
```

### 44.5 其他后台组件

| 组件 | 规格 |
|------|------|
| SearchBar | `input + border-slate-300 + focus:border-primary` + 新增按钮 |
| EditModal | `max-w-lg` 居中 + 表单字段配置驱动 |
| EditDrawer | 右侧滑出 `max-w-[480px]` + transform 动画 |
| ConfirmDialog | 删除二次确认 Modal |
| RefreshBtn | `⟳ 刷新` + toast"已刷新数据" |
| UserDropdown | 头像 + 下拉（修改密码/切换账号/退出） |
| StatusTag | 状态色映射 |

## 45. 弹窗体系

| 弹窗 ID | 触发 | 用途 | 尺寸 |
|---------|------|------|------|
| loginModal | 会员登录按钮 / 需登录操作 | 登录表单 | max-w-md |
| bookingModal | 在线预约按钮 | 预约表单 | max-w-md |
| chatModal | 客服按钮 / 浮窗 | 客服会话 | max-w-md h-480px |
| searchModal | 搜索按钮 | 站内搜索 | max-w-lg |
| changePwdModal | 修改密码 | 密码修改 | max-w-md |
| applyModal | 投递简历 | 招聘投递 | max-w-md |
| memberModal | 个人中心 | 会员中心 | max-w-md |
| modalBox（后台） | 新增/编辑/删除 | 后台表单 | max-w-lg |
| drawerBox（后台） | 详情/复杂表单 | 后台抽屉 | max-w-480px |

---

# 第八篇 · 交互与体验规范

## 46. 交互模式

### 46.1 Hover 反馈

| 元素 | Hover 效果 | 实现 |
|------|-----------|------|
| 导航链接 | gold 下划线展开 | `.nav-link::after` width 0→100% |
| 卡片 | 阴影加深 | `hover:shadow-lg transition-shadow` |
| 按钮 | 背景色变化 | `hover:bg-amber-700 transition-colors` |
| 表格行 | 浅灰高亮 | `tr:hover td { background:#f8fafc }` |
| 客服浮窗 | 放大 1.05 | `hover:scale-105 transition` |
| 图标按钮 | 背景高亮 | `hover:bg-stone-100` / `hover:bg-slate-100` |

### 46.2 Cursor 规范

**所有可点击元素必须添加 `cursor-pointer`**：

- 导航链接 `<a>`
- 按钮 `<button>`
- 可点击卡片
- 操作按钮（编辑/删除/新增）
- 菜单项
- 下拉触发器

### 46.3 点击防抖

- 异步操作（登录/提交/下单）期间禁用按钮
- 表单 `onsubmit="return doXxx(event)"` + `e.preventDefault()` 防止重复提交

## 47. 状态反馈

| 状态 | 表现 | 触发 |
|------|------|------|
| Loading | 按钮禁用 + spinner | 异步操作 >300ms |
| Skeleton | 骨架屏占位 | 内容加载中 |
| Empty | "暂无数据" / "购物车为空" | 列表为空 |
| Error | 红色文字 + toast | 校验失败/操作错误 |
| Success | toast 提示（2.2s） | 操作成功 |
| Badge | 购物车数字 + 弹性动画 | 加购成功 |

### Toast 规范

```javascript
function toast(t) {
  const el = document.getElementById('toast');
  el.textContent = t;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2200);
}
```

- 位置：`fixed bottom-40px center`
- 样式：`bg-ink text-white border-gold rounded-xl`
- 动画：opacity + translateY，300ms
- 持续：2.2s 自动消失

## 48. 表单规范

### 48.1 校验规则

| 字段类型 | 校验 | 提示 |
|---------|------|------|
| 必填 | `required` 属性 | 浏览器原生提示 |
| 手机号 | 11 位数字 | toast"请输入正确手机号" |
| 密码 | 非空 | toast"请输入密码" |
| 密码确认 | 原密码匹配 | toast"原密码错误" |

### 48.2 表单样式

```html
<!-- 输入框 -->
<input required class="w-full border border-stone-300 rounded-lg px-3 py-2.5 mb-4 focus:border-gold focus:outline-none" placeholder="请输入手机号">

<!-- Label -->
<label class="block text-sm text-stone-600 mb-1">手机号</label>

<!-- 下拉框 -->
<select class="w-full border border-stone-300 rounded-lg px-3 py-2.5 focus:border-gold focus:outline-none">
  <option>到店预约</option>
</select>

<!-- 多行文本 -->
<textarea rows="3" class="w-full border border-stone-300 rounded-lg px-3 py-2.5 focus:border-gold focus:outline-none" placeholder="留言"></textarea>
```

## 49. 在线客服交互

### 49.1 智能应答

```javascript
function botAnswer(q) {
  q = q.toLowerCase();
  if (q.includes('价格')) return '实木家具按系列定价，如胡桃禮沙发 ¥12,800。';
  if (q.includes('预约')) return '点击右上角「在线预约」填写需求，顾问 1 个工作日内联系。';
  if (q.includes('售后')) return '非人为损坏 1 年内免费维修，7 天无理由退换（定制除外）。';
  if (q.includes('地址') || q.includes('门店')) return '总部：上海市黄浦区南京东路 1 号 YD 大厦。';
  if (q.includes('电话') || q.includes('热线')) return '销售热线 400-888-8888，服务热线 400-888-9999。';
  if (q.includes('人工')) return '正在为您转接人工客服～';
  return '感谢咨询，可留下问题或电话，我们会尽快回复。也可拨 400-888-9999。';
}
```

### 49.2 快捷问题

6 个快捷按钮（胶囊样式）：
- 价格咨询 / 如何预约 / 售后政策 / 门店地址 / 联系电话 / 转人工

### 49.3 消息气泡

| 类型 | 样式 |
|------|------|
| 机器人 | `bg-stone-100 text-ink border-bottom-left-radius:4px` |
| 用户 | `bg-gold text-ink margin-left:auto border-bottom-right-radius:4px` |

### 49.4 XSS 防护

```javascript
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}
```

用户输入必须经 `escapeHtml` 处理后再插入 DOM。

## 50. 会员登录态交互

### 50.1 登录流程

```
点击"会员登录" → 弹出 loginModal
     ↓
输入手机号+密码 → doLogin()
     ↓
写入 localStorage.yd_member = {name, phone}
     ↓
关闭弹窗 → updateMemberUI()
     ↓
隐藏 #loginBtn → 显示 #avatarBtn（圆形头像）
     ↓
toast"登录成功"
```

### 50.2 头像下拉菜单

```html
<div id="userMenu" class="hidden fixed right-4 top-16 z-[70] w-44 bg-white rounded-xl shadow-2xl border border-stone-200 py-2">
  <div class="px-4 py-2 border-b text-sm text-stone-500">会员姓名</div>
  <a href="#" class="block px-4 py-2 hover:bg-sand hover:text-gold">个人中心</a>
  <a href="我的订单" class="block px-4 py-2 hover:bg-sand hover:text-gold">我的订单</a>
  <a href="我的预约" class="block px-4 py-2 hover:bg-sand hover:text-gold">我的预约</a>
  <button onclick="openChangePwd()" class="hover:bg-sand hover:text-gold">修改密码</button>
  <button onclick="logout()" class="text-red-600 hover:bg-red-50">退出登录</button>
</div>
```

### 50.3 持久化

- 登录态存储于 `localStorage.yd_member`
- 页面加载时 `updateMemberUI()` 读取并渲染
- 退出登录：`localStorage.removeItem('yd_member')`

---

# 第九篇 · 响应式与移动端

## 51. 断点定义

| 断点 | 前缀 | 宽度 | 典型设备 |
|------|------|------|---------|
| — | — | <640px | 手机竖屏 |
| sm | `sm:` | ≥640px | 手机横屏 / 小平板 |
| md | `md:` | ≥768px | 平板竖屏 |
| lg | `lg:` | ≥1024px | 平板横屏 / 小桌面 |
| xl | `xl:` | ≥1280px | 桌面 |

## 52. 移动端导航折叠

### 52.1 触发条件

- `lg:hidden` 汉堡菜单按钮，`<1024px` 显示
- `hidden lg:flex` 顶部导航，`<1024px` 隐藏

### 52.2 折叠菜单结构

```html
<div id="mobileMenu" class="lg:hidden hidden border-t border-stone-200 bg-sand">
  <nav class="flex flex-col gap-1">
    <a href="首页" class="py-2 text-ink font-medium">首页</a>
    <details>
      <summary class="py-2 text-stone2">产品中心</summary>
      <div class="pl-4 space-y-1">
        <a href="?space=客厅" class="block py-1 text-sm text-stone-300">客厅精选</a>
        <!-- ... -->
      </div>
    </details>
    <!-- 其他一级 + 二级 -->
    <a href="后台管理" class="py-2 text-gold font-medium">后台登录 →</a>
    <div class="flex gap-3 py-3 border-t">
      <button class="bg-gold text-white">在线预约</button>
      <button class="border border-ink">会员登录</button>
    </div>
  </nav>
</div>
```

## 53. 移动端关键路径

### 浏览路径

```
首页（移动端导航折叠） → 产品中心（2 列网格） → 产品详情（单列） → 加购 → 购物车 → 结算
```

### 预约路径

```
任意页面 → 右上角"在线预约"（移动端在折叠菜单内）/ 浮窗 → 预约弹窗 → 提交
```

### 下单路径

```
产品详情 → 加购 → 购物车结算 → 登录（如未登录） → 提交订单 → 我的订单
```

## 54. 图片自适应与触摸目标

### 54.1 图片规范

- 使用 `loading="lazy"` 懒加载
- `object-cover` 保持比例
- 响应式：`srcset` + WebP 格式
- 占位图：CSS 渐变 + SVG 图标

### 54.2 触摸目标

- **最小 44×44px**（WCAG 推荐）
- 导航项：`py-2`（约 40px+，含文字）
- 按钮：`px-3 py-2`（约 36px+，含文字）
- 客服浮窗：`w-14 h-14`（56px，超过最小）
- 图标按钮：`p-2` + 图标 20px（约 36px，接近最小）

---

# 第十篇 · 可访问性与交付清单

## 55. 无障碍规范

### 55.1 对比度

| 文字类型 | 要求 | 当前达标情况 |
|---------|------|------------|
| 主文字（ink #1C1917 on sand #FAFAF9） | ≥4.5:1 | ✓ 达标（约 16:1） |
| 次级文字（stone2 #44403C on sand） | ≥4.5:1 | ✓ 达标（约 9:1） |
| 金色文字（gold #CA8A04 on white） | ≥4.5:1 | ⚠ 需验证（约 3.8:1，大文字 ≥3:1 达标） |
| 白色文字 on gold | ≥4.5:1 | ⚠ 需验证 |

**建议**：gold 色用于大文字（≥18px）或装饰，小正文使用 stone-600 以上。

### 55.2 Aria 标签

所有图标按钮必须有 `aria-label`：

```html
<button aria-label="站内搜索"><svg>...</svg></button>
<button aria-label="在线客服"><svg>...</svg></button>
<button aria-label="打开菜单" aria-expanded="false"><svg>...</svg></button>
```

### 55.3 键盘导航

- Tab 顺序与视觉顺序一致
- 焦点环可见：`focus:outline-none` 需配合 `focus:border-gold` 或自定义 `focus:ring`
- ESC 关闭弹窗（建议增加）
- 表单可用 Tab 键依次聚焦

### 55.4 表单 Label

```html
<label class="block text-sm text-stone-600 mb-1" for="phone">手机号</label>
<input id="phone" required ...>
```

### 55.5 图片 Alt 文本

```html
<img src="product.jpg" alt="胡桃禮·实木沙发 - 北美黑胡桃材质，客厅会客场景">
```

### 55.6 降级

- `prefers-reduced-motion: reduce` → 禁用所有 transition 和 animation
- 颜色不作为唯一信息指示（状态需配合文字/图标）

## 56. 交付前检查清单

### 视觉质量

- [ ] 无 emoji 用作 UI 图标（使用 SVG）
- [ ] 所有图标来自统一图标集（内联 SVG，viewBox 0 0 24 24）
- [ ] 品牌徽标正确（YD 黑底金字）
- [ ] Hover 态不引起布局位移（仅颜色/阴影/opacity 变化）
- [ ] 使用主题色直接（`bg-gold`）而非 `var()` 包装

### 交互

- [ ] 所有可点击元素有 `cursor-pointer`
- [ ] Hover 态有明确视觉反馈
- [ ] 过渡时长 150–300ms（微交互）
- [ ] 焦点态可见（键盘导航）

### 主题与对比度

- [ ] 前台暖色系统一（stone/sand/gold）
- [ ] 后台蓝色系统一（primary #1677ff）
- [ ] 文字对比度 ≥4.5:1
- [ ] 边框在浅色背景可见（`border-stone-200`）

### 布局

- [ ] 导航栏 sticky + backdrop-blur
- [ ] 内容不被固定元素遮挡
- [ ] 响应式断点：375px / 768px / 1024px / 1440px
- [ ] 移动端无水平滚动
- [ ] 统一 `max-w-7xl` 容器

### 无障碍

- [ ] 图片有 alt 文本
- [ ] 表单有 label
- [ ] 颜色非唯一指示
- [ ] `prefers-reduced-motion` 已尊重

### 功能

- [ ] 前台 11 页均可访问
- [ ] 后台 11 模块按角色渲染
- [ ] 购物车加购→结算→订单闭环
- [ ] 招聘投递→进度跟踪闭环
- [ ] 客服智能应答 6 关键词
- [ ] 会员登录态全站持久化

## 57. 版本记录与变更日志

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-08-18 | 初版发布，覆盖前台 12 页 + 后台 11 模块 + 设计系统 + 组件库 + 交互规范 |

---

> **文档结束**
> 本文档基于 PRD v1.1 与 14 个高保真原型撰写，作为 YD家居平台前端开发还原与验收依据。
> 后续原型迭代或 PRD 变更时，需同步更新本文档对应章节。
