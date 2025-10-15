import { useParams } from 'react-router-dom'

const CameraView = () => {
  const { id } = useParams()

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <h1 className="text-2xl font-bold text-white mb-6">Camera View</h1>
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="aspect-video bg-gray-700 rounded-lg flex items-center justify-center">
          <p className="text-gray-400">Live Stream - Camera {id}</p>
        </div>
      </div>
    </div>
  )
}

export default CameraView
