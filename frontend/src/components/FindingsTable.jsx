import React from 'react'
import RiskBadge from './RiskBadge.jsx'
import { truncate } from '../utils/helpers.js'

const TYPE_COLORS = {
  EMAIL: 'text-blue-400', PHONE: 'text-cyan-400', PAN: 'text-orange-400',
  AADHAAR: 'text-orange-400', CREDIT_CARD: 'text-red-400', BANK_ACCOUNT: 'text-red-400',
  PASSWORD: 'text-red-500', API_KEY: 'text-purple-400', JWT_TOKEN: 'text-purple-400',
  PRIVATE_KEY: 'text-red-500', ADDRESS: 'text-yellow-400', DATE_OF_BIRTH: 'text-pink-400',
  PERSON_NAME: 'text-teal-400', IFSC_CODE: 'text-indigo-400', PINCODE: 'text-gray-400',
}

export default function FindingsTable({ findings = [] }) {
  if (!findings.length) {
    return (
      <div className="card text-center py-10">
        <p className="text-green-400 font-semibold text-lg">✅ No sensitive data found</p>
        <p className="text-gray-500 mt-1 text-sm">This document appears safe to share.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-800">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-800/80 text-gray-400 uppercase text-xs tracking-wider">
            <th className="px-4 py-3 text-left">#</th>
            <th className="px-4 py-3 text-left">Type</th>
            <th className="px-4 py-3 text-left">Masked Value</th>
            <th className="px-4 py-3 text-left">Location</th>
            <th className="px-4 py-3 text-left">Confidence</th>
            <th className="px-4 py-3 text-left">Severity</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f, i) => (
            <tr key={i} className="border-t border-gray-800 hover:bg-gray-800/40 transition-colors">
              <td className="px-4 py-3 text-gray-500">{i + 1}</td>
              <td className="px-4 py-3">
                <span className={`font-mono font-semibold text-xs ${TYPE_COLORS[f.type] || 'text-gray-300'}`}>
                  {f.type?.replace(/_/g, ' ')}
                </span>
              </td>
              <td className="px-4 py-3 font-mono text-gray-300 text-xs">{truncate(f.masked_value, 35)}</td>
              <td className="px-4 py-3 text-gray-400 text-xs">{f.location || 'N/A'}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full"
                      style={{ width: `${(f.confidence * 100).toFixed(0)}%` }}
                    />
                  </div>
                  <span className="text-gray-400 text-xs">{(f.confidence * 100).toFixed(0)}%</span>
                </div>
              </td>
              <td className="px-4 py-3"><RiskBadge level={f.severity} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
