import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import AgentChat from './pages/AgentChat'
import BoardMeeting from './pages/BoardMeeting'
import Skills from './pages/Skills'
import Training from './pages/Training'
import Settings from './pages/Settings'
import Memory from './pages/Memory'
import Learning from './pages/Learning'
import Notifications from './pages/Notifications'
import Integrations from './pages/Integrations'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/chat" element={<AgentChat />} />
              <Route path="/board" element={<BoardMeeting />} />
              <Route path="/skills" element={<Skills />} />
              <Route path="/training" element={<Training />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/memory" element={<Memory />} />
              <Route path="/learning" element={<Learning />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/integrations" element={<Integrations />} />
            </Routes>
          </Layout>
          <Toaster position="top-right" />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
