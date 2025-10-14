import { useQuery } from 'react-query'
import api from '../services/api'

interface Alert {
  id: number
  camera_id: number
  event_type: string
  timestamp: string
  snapshot_path: string | null
  acknowledged: boolean
}

export default function Alerts() {
  const { data: alerts, isLoading } = useQuery<Alert[]>('alerts', async () => {
    const response = await api.get('/api/alerts')
    return response.data
  })

  const handleAcknowledge = async (alertId: number) => {
    await api.post(`/api/alerts/${alertId}/acknowledge`)
    window.location.reload()
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-2xl font-bold mb-6">Alerts</h1>
      
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <div className="space-y-4">
          {alerts?.map((alert) => (
            <div key={alert.id} className="bg-gray-800 rounded-lg p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{alert.event_type}</h3>
                  <p className="text-sm text-gray-400">
                    Camera {alert.camera_id} • {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
                {!alert.acknowledged && (
                  <button
                    onClick={() => handleAcknowledge(alert.id)}
                    className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm"
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            </div>
          ))}
          
          {!isLoading && alerts?.length === 0 && (
            <p className="text-gray-400 text-center">No alerts found</p>
          )}
        </div>
      )}
    </div>
  )
}
