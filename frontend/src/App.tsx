import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Skills from './pages/Skills'
import Training from './pages/Training'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/skills" element={<Skills />} />
            <Route path="/training" element={<Training />} />
          </Routes>
        </Layout>
        <Toaster position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
