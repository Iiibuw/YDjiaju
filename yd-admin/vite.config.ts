import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig({
  // M3：后台部署在 /admin/ 路径下（nginx 反代），生产资源必须带此前缀
  base: '/admin/',
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    host: '0.0.0.0',
    port: 5181,
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 5181,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
