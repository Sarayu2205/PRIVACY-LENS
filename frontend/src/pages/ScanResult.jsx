import React, { useEffect, useState } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { Download, FileText, Shield, CheckCircle, AlertTriangle, Copy, Eye, EyeOff } from 'lucide-react'
import { getScan, maskScan, generateReport, downloadReport } from '../services/scanService.js'
import { formatDate, getErrorMessage } from '../utils/helpers.js'
import FindingsTable from '../components/FindingsTable.jsx'
import RiskMeter from '../components/RiskMeter.jsx'
import RiskBadge from '../components/RiskBadge.jsx'
import Spinner from '../components/Spinner.jsx'
import toast from 'react-hot-toast'

export default function ScanResult() {
  const { id } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()
  const [result, setResult]   = useState(state?.result || null)
  const [scan, setScan]       = useState(null)
  const [loading, setLoading] = useState(!state?.result)
  const [showMasked, setShowMasked] = useState(false)
  const [masking, setMasking] = useState(false)
  const [reporting, setReporting] = useState(false)

  useEffect(() => {
    if (!state?.result) {
      getScan(id).then(setScan).catch(() => toast.error('Scan not found.')).finally(() => setLoading(false))
    }
  }, [id])

  const scanData = result || scan
  if (loading) return <Spinner text="Loading scan results…" />
  if (!scanData) return <div className="card text-center py-10 text-gray-400">Scan not found.</div>

  const findings   = result?.findings || scan?.findings || []
  const masked     = result?.masked_text
  const recs       = result?.recommendations || []
  const summary    = result?.risk_summary || ''

  const handleMask = async () => {
    setMasking(true)
    try {
      await maskScan(id)
      toast.success('Scan marked as masked.')
      if (masked) {
        const blob = new Blob([masked], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a'); a.href = url
        a.download = `masked_${scanData.file_name || 'document'}.txt`
        a.click(); URL.revokeObjectURL(url)
      }
    } catch { toast.error('Masking failed.') }
    finally { setMasking(false) }
  }

  const handleReport = async () => {
    setReporting(true)
    try {
      await generateReport(id)
      const blob = await downloadReport(id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a'); a.href = url
      a.download = `privacylens_report_scan_${id}.pdf`
      a.click(); URL.revokeObjectURL(url)
      toast.success('Report downloaded!')
    } catch (e) { toast.error(getErrorMessage(e)) }
    finally { setReporting(false) }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-xl font-bold text-white">Scan Results</h1>
          <p className="text-gray-400 text-sm mt-0.5">
            {scanData.file_name || 'Document'} · {formatDate(scanData.scan_date)}
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button onClick={handleMask} disabled={masking} className="btn-secondary">
            <Download size={16} /> {masking ? 'Downloading…' : 'Download Masked'}
          </button>
          <button onClick={handleReport} disabled={reporting} className="btn-primary">
            <FileText size={16} /> {reporting ? 'Generating…' : 'Get PDF Report'}
          </button>
        </div>
      </div>

      {/* Summary row */}
      <div className="grid lg:grid-cols-3 gap-4">
        {/* Risk meter */}
        <div className="card flex items-center justify-center col-span-1">
          <RiskMeter score={scanData.risk_score} level={scanData.risk_level} />
        </div>

        {/* Stats */}
        <div className="card col-span-2 grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Total Findings</p>
            <p className="text-3xl font-bold text-white mt-1">{scanData.finding_count}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Risk Level</p>
            <div className="mt-2"><RiskBadge level={scanData.risk_level} /></div>
          </div>
          <div className="col-span-2">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Categories Detected</p>
            <div className="flex flex-wrap gap-2">
              {scanData.categories
                ? Object.entries(scanData.categories).map(([k, v]) => (
                  <span key={k} className="text-xs px-2.5 py-1 rounded-full bg-gray-800 text-gray-300 border border-gray-700">
                    {k.replace(/_/g, ' ')}: {v}
                  </span>
                ))
                : <span className="text-gray-500 text-sm">No categories</span>
              }
            </div>
          </div>
        </div>
      </div>

      {/* Risk summary */}
      {summary && (
        <div className={`p-4 rounded-xl border ${
          scanData.risk_level === 'CRITICAL' ? 'bg-red-900/20 border-red-700' :
          scanData.risk_level === 'HIGH'     ? 'bg-orange-900/20 border-orange-700' :
          scanData.risk_level === 'MEDIUM'   ? 'bg-yellow-900/20 border-yellow-700' :
          'bg-green-900/20 border-green-700'
        }`}>
          <div className="flex items-start gap-2">
            <Shield size={16} className="mt-0.5 flex-shrink-0 text-gray-400" />
            <p className="text-sm text-gray-300">{summary}</p>
          </div>
        </div>
      )}

      {/* Findings table */}
      <div>
        <h2 className="text-sm font-semibold text-gray-300 mb-3">Detailed Findings</h2>
        <FindingsTable findings={findings} />
      </div>

      {/* Recommendations */}
      {recs.length > 0 && (
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <AlertTriangle size={15} className="text-yellow-400" /> Recommended Actions
          </h2>
          <ul className="space-y-2">
            {recs.map((r, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-green-400 mt-0.5">•</span>{r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Masked text preview */}
      {masked && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-300">Sanitized (Masked) Version</h2>
            <button onClick={() => setShowMasked(p => !p)} className="text-xs text-primary-400 flex items-center gap-1">
              {showMasked ? <EyeOff size={13} /> : <Eye size={13} />}
              {showMasked ? 'Hide' : 'Preview'}
            </button>
          </div>
          {showMasked && (
            <pre className="font-mono text-xs text-gray-400 bg-gray-800 rounded-lg p-4 overflow-auto max-h-60 whitespace-pre-wrap">
              {masked}
            </pre>
          )}
          {!showMasked && (
            <p className="text-xs text-gray-500">Sensitive values replaced with asterisks. Click Preview to view.</p>
          )}
        </div>
      )}
    </div>
  )
}
