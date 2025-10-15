import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Video, AlertTriangle, Activity } from 'lucide-react'

interface Camera {
  id: number
  name: string
  site: string
  status: string
  enabled: boolean
  last_seen: string | null
}

const Dashboard = () => {
  const [cameras, setCameras] = useState<Camera[]>([])

  const { data, isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token')
      const response = await axios.get('/api/cameras', {
        headers: { Authorization: `Bearer ${token}` },
      })
      return response.data
    },
  })

  useEffect(() => {
    if (data) {
      setCameras(data)
    }
  }, [data])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-500'
      case 'offline':
        return 'bg-red-500'
      case 'error':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Video className="h-8 w-8 text-primary-500 mr-3" />
              <h1 className="text-2xl font-bold text-white">
                Video Analytics Platform
              </h1>
            </div>
            <nav className="flex space-x-4">
              <Link
                to="/"
                className="text-white hover:text-primary-400 px-3 py-2 rounded-md text-sm font-medium"
              >
                Dashboard
              </Link>
              <Link
                to="/alerts"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Alerts
              </Link>
              <Link
                to="/rules"
                className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Rules
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center">
              <Video className="h-12 w-12 text-primary-500" />
              <div className="ml-4">
                <p className="text-gray-400 text-sm">Total Cameras</p>
                <p className="text-3xl font-bold text-white">{cameras.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center">
              <Activity className="h-12 w-12 text-green-500" />
              <div className="ml-4">
                <p className="text-gray-400 text-sm">Online</p>
                <p className="text-3xl font-bold text-white">
                  {cameras.filter((c) => c.status === 'online').length}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center">
              <AlertTriangle className="h-12 w-12 text-red-500" />
              <div className="ml-4">
                <p className="text-gray-400 text-sm">Alerts Today</p>
                <p className="text-3xl font-bold text-white">0</p>
              </div>
            </div>
          </div>
        </div>

        {/* Camera Grid */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-4">Live Cameras</h2>
          {isLoading ? (
            <div className="text-center py-12">
              <p className="text-gray-400">Loading cameras...</p>
            </div>
          ) : cameras.length === 0 ? (
            <div className="text-center py-12 bg-gray-800 rounded-lg">
              <Video className="mx-auto h-12 w-12 text-gray-600" />
              <p className="mt-4 text-gray-400">No cameras configured</p>
              <p className="text-sm text-gray-500 mt-2">
                Add cameras to start monitoring
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {cameras.map((camera) => (
                <Link
                  key={camera.id}
                  to={`/cameras/${camera.id}`}
                  className="bg-gray-800 rounded-lg overflow-hidden shadow-lg hover:shadow-xl transition-shadow"
                >
                  <div className="aspect-video bg-gray-700 flex items-center justify-center">
                    <Video className="h-16 w-16 text-gray-600" />
                  </div>
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white">
                        {camera.name}
                      </h3>
                      <span
                        className={`h-3 w-3 rounded-full ${getStatusColor(
                          camera.status
                        )}`}
                      />
                    </div>
                    <p className="text-sm text-gray-400">{camera.site}</p>
                    <p className="text-xs text-gray-500 mt-1 capitalize">
                      Status: {camera.status}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default Dashboard
