import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './styles/index.css'

// IMPORTANT:
// <App/> already calls createBrowserRouter + <RouterProvider> (data-router API in v7).
// Do NOT wrap it with <BrowserRouter> here — it would nest a <Router> inside another
// and crash with: "You cannot render a <Router> inside another <Router>".

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)
