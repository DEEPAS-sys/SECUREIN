import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import CameraView from './pages/CameraView'
import Alerts from './pages/Alerts'
import Rules from './pages/Rules'

function App() {
  const isAuthenticated = !!localStorage.getItem('access_token')

  return (
    <div className="min-h-screen bg-gray-900">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
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
      </Routes>
    </div>
  )
}

export default App
