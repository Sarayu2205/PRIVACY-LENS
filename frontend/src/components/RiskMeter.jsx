import React from 'react'

export default function RiskMeter({ score = 0, level = 'LOW' }) {
  const colorMap = {
    CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#eab308', LOW: '#22c55e'
  }
  const color = colorMap[level] || '#22c55e'
  const pct = Math.min(100, Math.max(0, score))
  const radius = 50
  const stroke = 8
  const normalizedRadius = radius - stroke / 2
  const circumference = 2 * Math.PI * normalizedRadius
  const dashOffset = circumference - (pct / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={normalizedRadius} fill="none" stroke="#1f2937" strokeWidth={stroke} />
        <circle
          cx="60" cy="60" r={normalizedRadius} fill="none"
          stroke={color} strokeWidth={stroke}
          strokeDasharray={circumference} strokeDashoffset={dashOffset}
          strokeLinecap="round"
          transform="rotate(-90 60 60)"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
        <text x="60" y="55" textAnchor="middle" fill="white" fontSize="18" fontWeight="bold" fontFamily="Inter">
          {pct.toFixed(0)}
        </text>
        <text x="60" y="70" textAnchor="middle" fill="#9ca3af" fontSize="9" fontFamily="Inter">
          / 100
        </text>
      </svg>
      <span
        className="text-xs font-bold px-3 py-1 rounded-full"
        style={{ color, background: color + '22', border: `1px solid ${color}44` }}
      >
        {level} RISK
      </span>
    </div>
  )
}
