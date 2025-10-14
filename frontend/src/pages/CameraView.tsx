import { useParams } from 'react-router-dom'

export default function CameraView() {
  const { id } = useParams()

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-2xl font-bold mb-6">Camera View - {id}</h1>
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="bg-gray-700 rounded aspect-video mb-4 flex items-center justify-center">
          <span className="text-gray-500">Live video player placeholder</span>
        </div>
        <p className="text-gray-400">Camera details and controls will appear here</p>
      </div>
    </div>
  )
}
