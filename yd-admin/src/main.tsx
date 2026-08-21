import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { App as AntApp, ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import './styles/index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 60 * 1000, retry: 1, refetchOnWindowFocus: false },
  },
})

// 注意:不用 StrictMode(React 19 下 double-mount 会让 ECharts 实例被 dispose 后仍被 setOption,导致图表空白)
createRoot(document.getElementById('root')!).render(
  <ConfigProvider
    locale={zhCN}
    theme={{
      token: {
        colorPrimary: '#1677ff', // UI/UX §3.1 后台品牌蓝
        borderRadius: 6,
      },
    }}
  >
    {/* antd <App>：让 Modal.confirm / message / notification 等静态函数拿到 ConfigProvider 上下文，
        消除 "Static function cannot consume dynamic theme" 警告,
        修复 React 19 下 Modal.confirm 不弹的问题 */}
    <AntApp message={{ maxCount: 3 }} notification={{ placement: 'topRight' }}>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </AntApp>
  </ConfigProvider>,
)
