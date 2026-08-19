import type { Config } from 'tailwindcss'

/**
 * 设计 Token（与 UI/UX 设计规格文档 §第二篇 对齐）
 * 前台：stone/gold 暖色调 + Lexend + Source Sans 3
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
          DEFAULT: '#b08d57', // 品牌金
          light: '#d4b78a',
          dark: '#8a6c3f',
          50: '#fbf7f0',
        },
        sand: '#f5efe6', // 浅米色背景
        coal: '#0c0a09', // 深色文字
      },
      fontFamily: {
        display: ['"Lexend"', 'system-ui', 'sans-serif'],
        body: ['"Source Sans 3"', '"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
      },
      maxWidth: {
        container: '1280px',
      },
    },
  },
  plugins: [],
} satisfies Config
