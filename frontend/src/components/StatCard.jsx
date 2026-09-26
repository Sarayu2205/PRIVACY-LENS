import React from 'react'

export default function StatCard({ title, value, icon: Icon, color = 'text-primary-400', bg = 'bg-primary-600/10', subtitle }) {
  return (
    <div className="card flex items-start gap-4">
      <div className={`${bg} p-3 rounded-lg`}>
        <Icon size={22} className={color} />
      </div>
      <div>
        <p className="text-gray-400 text-sm">{title}</p>
        <p className="text-2xl font-bold text-white mt-0.5">{value ?? '—'}</p>
        {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
      </div>
    </div>
  )
}
