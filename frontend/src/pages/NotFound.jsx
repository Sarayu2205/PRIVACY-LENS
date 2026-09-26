import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield } from 'lucide-react'

export default function NotFound() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center text-center px-4">
      <div>
        <Shield size={48} className="mx-auto text-gray-700 mb-4" />
        <h1 className="text-4xl font-bold text-white mb-2">404</h1>
        <p className="text-gray-400 mb-6">Page not found.</p>
        <button onClick={() => navigate('/dashboard')} className="btn-primary mx-auto">
          Go to Dashboard
        </button>
      </div>
    </div>
  )
}
