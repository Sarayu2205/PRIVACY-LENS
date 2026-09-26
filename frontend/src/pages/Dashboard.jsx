import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, FileSearch, AlertTriangle, CheckCircle, TrendingUp, Files, Zap } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid, Legend
} from 'recharts'
import { getDashboardStats } from '../services/scanService.js'
import { useAuth } from '../context/AuthContext.jsx'
import { formatDate, getRiskBadge } from '../utils/helpers.js'
import StatCard from '../components/StatCard.jsx'
import RiskBadge from '../components/RiskBadge.jsx'
import Spinner from '../components/Spinner.jsx'
import toast from 'react-hot-toast'

const PIE_COLORS = ['#ef4444','#f97316','#eab308','#22c55e','#6366f1','#06b6d4','#ec4899','#8b5cf6']

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboardStats()
      .then(setStats)
      .catch(() => toast.error('Failed to load dashboard stats.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner text="Loading dashboard…" />

  const pieData = stats?.findings_by_category
    ? Object.entries(stats.findings_by_category).map(([name, value]) => ({ name: name.replace(/_/g,' '), value }))
    : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Welcome back, {user?.name?.split(' ')[0]} 👋</h1>
          <p className="text-gray-400 text-sm mt-0.5">Here's your privacy protection overview</p>
        </div>
        <button onClick={() => navigate('/scan/file')} className="btn-primary">
          <Zap size={16} /> New Scan
        </button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Scans" value={stats?.total_scans ?? 0} icon={Files}
          color="text-primary-400" bg="bg-primary-600/10" />
        <StatCard title="Findings Detected" value={stats?.total_findings ?? 0} icon={AlertTriangle}
          color="text-orange-400" bg="bg-orange-600/10" />
        <StatCard title="Critical / High" value={(stats?.critical_count ?? 0) + (stats?.high_risk_count ?? 0)} icon={Shield}
          color="text-red-400" bg="bg-red-600/10" />
        <StatCard title="Clean Scans" value={Math.max(0, (stats?.total_scans ?? 0) - (stats?.critical_count ?? 0) - (stats?.high_risk_count ?? 0))} icon={CheckCircle}
          color="text-green-400" bg="bg-green-600/10" />
      </div>

      {/* Charts row */}
      <div className="grid lg:grid-cols-2 gap-4">
        {/* Findings by category */}
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Findings by Category</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" outerRadius={80}
                  dataKey="value" label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}
                  labelLine={false} fontSize={10}>
                  {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500 text-sm">No findings yet</div>
          )}
        </div>

        {/* Scans over time */}
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Scans Over Time (30 days)</h3>
          {stats?.scans_over_time?.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={stats.scans_over_time} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} tickFormatter={d => d.slice(5)} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff', fontSize: 12 }} />
                <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} dot={false} name="Scans" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500 text-sm">No scan activity yet</div>
          )}
        </div>
      </div>

      {/* Risk breakdown bar chart */}
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-300 mb-4">Risk Level Breakdown</h3>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={[
            { name: 'Critical', count: stats?.critical_count ?? 0, fill: '#ef4444' },
            { name: 'High',     count: stats?.high_risk_count ?? 0, fill: '#f97316' },
            { name: 'Medium',   count: stats?.medium_risk_count ?? 0, fill: '#eab308' },
            { name: 'Low',      count: stats?.low_risk_count ?? 0, fill: '#22c55e' },
          ]} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} allowDecimals={false} />
            <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff', fontSize: 12 }} />
            <Bar dataKey="count" radius={[4,4,0,0]}>
              {[{ fill:'#ef4444' },{ fill:'#f97316' },{ fill:'#eab308' },{ fill:'#22c55e' }].map((e,i) => (
                <Cell key={i} fill={e.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent scans */}
      {stats?.recent_scans?.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-300">Recent Scans</h3>
            <button onClick={() => navigate('/history')} className="text-xs text-primary-400 hover:text-primary-300">
              View all →
            </button>
          </div>
          <div className="space-y-2">
            {stats.recent_scans.map(s => (
              <div key={s.id}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 cursor-pointer transition-colors"
                onClick={() => navigate(`/scan/result/${s.id}`)}>
                <div>
                  <p className="text-sm font-medium text-white">{s.file_name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{formatDate(s.scan_date)} · {s.finding_count} findings</p>
                </div>
                <RiskBadge level={s.risk_level} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
