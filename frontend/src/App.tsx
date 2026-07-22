import { Routes, Route, Navigate } from 'react-router-dom'
import { getToken } from './services/api'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import Templates from './pages/Templates'
import TemplateDetail from './pages/TemplateDetail'
import DocumentGenerate from './pages/DocumentGenerate'
import BatchTasks from './pages/BatchTasks'
import Layout from './components/Layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = getToken()
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/*" element={
        <ProtectedRoute>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/templates" element={<Templates />} />
              <Route path="/templates/:id" element={<TemplateDetail />} />
              <Route path="/generate/:templateId?" element={<DocumentGenerate />} />
              <Route path="/tasks" element={<BatchTasks />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Layout>
        </ProtectedRoute>
      } />
    </Routes>
  )
}

export default App
