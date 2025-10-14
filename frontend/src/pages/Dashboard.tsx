import { useEffect, useState } from 'react'
import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'

interface Camera {
  id: number
  name: string
  status: string
  site: string
}

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([])
  
  const { data, isLoading } = useQuery('cameras', async () => {
    const response = await api.get('/api/cameras')
    return response.data
  })

  useEffect(() => {
    if (data) {
      setCameras(data)
    }
  }, [data])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-white">Video Analytics Platform</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/dashboard" className="text-gray-300 hover:text-white px-3 py-2">Dashboard</Link>
              <Link to="/alerts" className="text-gray-300 hover:text-white px-3 py-2">Alerts</Link>
              <Link to="/rules" className="text-gray-300 hover:text-white px-3 py-2">Rules</Link>
              <button onClick={handleLogout} className="text-gray-300 hover:text-white px-3 py-2">
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">Cameras</h2>
          <Link
            to="/cameras/new"
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Add Camera
          </Link>
        </div>

        {isLoading ? (
          <div className="text-white">Loading...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cameras.map((camera) => (
              <Link
                key={camera.id}
                to={`/cameras/${camera.id}`}
                className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-white">{camera.name}</h3>
                  <span className={`px-2 py-1 rounded text-xs ${
                    camera.status === 'online' ? 'bg-green-500/20 text-green-400' :
                    camera.status === 'offline' ? 'bg-red-500/20 text-red-400' :
                    'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {camera.status}
                  </span>
                </div>
                
                {/* Placeholder for video thumbnail */}
                <div className="bg-gray-700 rounded aspect-video mb-4 flex items-center justify-center">
                  <span className="text-gray-500">No preview</span>
                </div>
                
                {camera.site && (
                  <p className="text-gray-400 text-sm">Site: {camera.site}</p>
                )}
              </Link>
            ))}
          </div>
        )}

        {!isLoading && cameras.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400 mb-4">No cameras configured</p>
            <Link to="/cameras/new" className="text-blue-500 hover:text-blue-400">
              Add your first camera
            </Link>
          </div>
        )}
      </main>
    </div>
  )
}
