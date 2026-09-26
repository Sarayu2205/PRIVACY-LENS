import React from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Mail, Calendar, LogOut, Shield } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { formatDate } from '../utils/helpers.js'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    toast.success('Logged out successfully.')
    navigate('/login')
  }

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <h1 className="text-xl font-bold text-white">Profile & Settings</h1>

      {/* Profile card */}
      <div className="card">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-primary-600 flex items-center justify-center text-white text-2xl font-bold">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">{user?.name}</h2>
            <p className="text-gray-400 text-sm">{user?.email}</p>
          </div>
        </div>

        <div className="space-y-3 border-t border-gray-800 pt-4">
          <div className="flex items-center gap-3 text-sm">
            <User size={16} className="text-gray-500" />
            <span className="text-gray-400 w-24">Name</span>
            <span className="text-gray-200">{user?.name}</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <Mail size={16} className="text-gray-500" />
            <span className="text-gray-400 w-24">Email</span>
            <span className="text-gray-200">{user?.email}</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <Calendar size={16} className="text-gray-500" />
            <span className="text-gray-400 w-24">Joined</span>
            <span className="text-gray-200">{formatDate(user?.created_at)}</span>
          </div>
        </div>
      </div>

      {/* Security info */}
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2 mb-3">
          <Shield size={15} className="text-primary-400" /> Security Information
        </h3>
        <ul className="space-y-2 text-sm text-gray-400">
          <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Password stored with bcrypt hashing</li>
          <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Session secured with JWT (24h expiry)</li>
          <li className="flex items-center gap-2"><span className="text-green-400">✓</span> Sensitive data never stored in plain text</li>
          <li className="flex items-center gap-2"><span className="text-green-400">✓</span> All API endpoints require authentication</li>
        </ul>
      </div>

      {/* Logout */}
      <button onClick={handleLogout} className="btn-danger w-full justify-center">
        <LogOut size={17} /> Sign Out
      </button>
    </div>
  )
}
