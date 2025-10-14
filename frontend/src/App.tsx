import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import CameraView from './pages/CameraView'
import Alerts from './pages/Alerts'
import Rules from './pages/Rules'

const queryClient = new QueryClient()

function App() {
  const isAuthenticated = !!localStorage.getItem('access_token')

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route 
            path="/dashboard" 
            element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/cameras/:id" 
            element={isAuthenticated ? <CameraView /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/alerts" 
            element={isAuthenticated ? <Alerts /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/rules" 
            element={isAuthenticated ? <Rules /> : <Navigate to="/login" />} 
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App
