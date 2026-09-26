import React from 'react'

export default function Spinner({ size = 8, text = '' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-10">
      <div className={`animate-spin rounded-full h-${size} w-${size} border-t-2 border-primary-500`} />
      {text && <p className="text-gray-400 text-sm">{text}</p>}
    </div>
  )
}
