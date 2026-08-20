import type { Config } from 'tailwindcss'

/**
 * 设计 Token（与 UI/UX 设计规格文档 §第二篇 对齐）
 * 前台：stone/gold 暖色调 + Lexend + Source Sans 3
 *
 * v1.1（M4）对齐说明（UI 文档 §5/§6）：
 * - gold DEFAULT #CA8A04（品牌强调色琥珀金，原 #b08d57 偏暗）
 * - sand #FAFAF9（页面背景，等同 stone-50；原 #f5efe6 偏米）
 * - fontFamily 增加 head（Lexend 标题字体，文档 §6.1 命名）
 * - walnut：原型黑胡桃色（UI 文档未列，用于「预约到店」等强调钮）
 *
 * 注意：v2.0 临时改成黑金版（commit 0f6deb5）后被回滚（v2.1），
 *       NavBar / Footer 仍走硬编码黑金色独立区段。
 */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // UI/UX §2.1 品牌色
        ink: {
          DEFAULT: '#1c1917', // stone-900 主文本
          soft: '#44403c',
        },
        stone: {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
        },
        gold: {
          DEFAULT: '#ca8a04', // 品牌金（UI 文档 §5.1 #CA8A04）
          light: '#d4b78a',
          dark: '#8a6c3f',
          50: '#fbf7f0',
        },
        sand: '#fafaf9', // 页面背景（UI 文档 §5.1 #FAFAF9）
        coal: '#0c0a09', // 深色文字
        walnut: '#6b4a2f', // 黑胡桃（原型强调钮）
      },
      fontFamily: {
        head: ['"Lexend"', 'system-ui', 'sans-serif'], // UI 文档 §6.1 标题字体
        display: ['"Lexend"', 'system-ui', 'sans-serif'], // 兼容旧引用
        body: ['"Source Sans 3"', '"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
      },
      maxWidth: {
        container: '1280px',
      },
    },
  },
  plugins: [],
} satisfies Config
