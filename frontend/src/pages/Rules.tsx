import { useQuery } from 'react-query'
import api from '../services/api'

interface Rule {
  id: number
  camera_id: number
  name: string
  type: string
  enabled: boolean
}

export default function Rules() {
  const { data: rules, isLoading } = useQuery<Rule[]>('rules', async () => {
    const response = await api.get('/api/rules')
    return response.data
  })

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Rules</h1>
        <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">
          Create Rule
        </button>
      </div>
      
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <div className="space-y-4">
          {rules?.map((rule) => (
            <div key={rule.id} className="bg-gray-800 rounded-lg p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{rule.name}</h3>
                  <p className="text-sm text-gray-400">
                    Type: {rule.type} • Camera {rule.camera_id}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  rule.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                }`}>
                  {rule.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </div>
          ))}
          
          {!isLoading && rules?.length === 0 && (
            <p className="text-gray-400 text-center">No rules configured</p>
          )}
        </div>
      )}
    </div>
  )
}
