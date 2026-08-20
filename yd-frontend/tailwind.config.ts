import type { Config } from 'tailwindcss'

/**
 * 设计 Token（与 UI/UX 设计规格文档 §第二篇 对齐）
 * 前台：stone/gold 暖色调 + Lexend + Source Sans 3
 *
 * v2.0（黑金奢华版，2026-08-20 用户要求）：
 * - sand → 深黑 #0d0b09（奢华黑底，替代原米白 #FAFAF9）
 * - coal / ink → 暖米白 #ece5d8（深色底上的正文色）
 * - gold → 明亮金 #c9a227（品牌强调色）
 * - walnut → 金色系 #c9a227（强调钮黑金化）
 * - stone 系列整体压暗（浅色边框/次级文本适配深色底）
 * - card #1c1812：全局卡片底色（替代 bg-white）
 */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // UI/UX §2.1 品牌色
        ink: {
          DEFAULT: '#ece5d8', // 暖米白主文本（深色底）
          soft: '#bdb5a2',
        },
        stone: {
          50: '#17140f',
          100: '#1d1a14',
          200: '#2a251c',
          300: '#3d362a',
          400: '#6b6150',
          500: '#9a917d',
          600: '#b3aa94',
          700: '#cec5b2',
        },
        gold: {
          DEFAULT: '#c9a227', // 品牌金（明亮金，奢华感）
          light: '#e0c77e',
          dark: '#8a6c3f',
          50: '#2a2417',
        },
        sand: '#0d0b09', // 页面背景（深黑褐，替代原米白）
        coal: '#ece5d8', // 主文本（暖米白）
        walnut: '#c9a227', // 强调钮（黑金化：胡桃 → 金）
        card: '#1c1812', // 全局卡片底色（替代 bg-white）
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
