import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext.jsx'

import Layout from './components/Layout.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import ScanFile from './pages/ScanFile.jsx'
import ScanText from './pages/ScanText.jsx'
import ScanResult from './pages/ScanResult.jsx'
import History from './pages/History.jsx'
import ReportPage from './pages/ReportPage.jsx'
import Profile from './pages/Profile.jsx'
import NotFound from './pages/NotFound.jsx'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen"><div className="animate-spin rounded-full h-10 w-10 border-t-2 border-primary-500" /></div>
  return user ? children : <Navigate to="/login" replace />
}

function GuestRoute({ children }) {
  const { user } = useAuth()
  return user ? <Navigate to="/dashboard" replace /> : children
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login"    element={<GuestRoute><Login /></GuestRoute>} />
      <Route path="/register" element={<Navigate to="/login" replace />} />

      {/* Protected */}
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/dashboard"       element={<Dashboard />} />
        <Route path="/scan/file"       element={<ScanFile />} />
        <Route path="/scan/text"       element={<ScanText />} />
        <Route path="/scan/result/:id" element={<ScanResult />} />
        <Route path="/history"         element={<History />} />
        <Route path="/report/:id"      element={<ReportPage />} />
        <Route path="/profile"         element={<Profile />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
