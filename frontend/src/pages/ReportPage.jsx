import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { FileText, Download, ArrowLeft, Shield } from 'lucide-react'
import { getScan, generateReport, downloadReport } from '../services/scanService.js'
import { formatDate, getErrorMessage } from '../utils/helpers.js'
import RiskBadge from '../components/RiskBadge.jsx'
import RiskMeter from '../components/RiskMeter.jsx'
import Spinner from '../components/Spinner.jsx'
import toast from 'react-hot-toast'

export default function ReportPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [scan, setScan]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    getScan(id).then(setScan).catch(() => toast.error('Scan not found.')).finally(() => setLoading(false))
  }, [id])

  const handleDownload = async () => {
    setGenerating(true)
    try {
      await generateReport(id)
      const blob = await downloadReport(id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a'); a.href = url
      a.download = `PrivacyLens_Report_${id}.pdf`
      a.click(); URL.revokeObjectURL(url)
      toast.success('PDF report downloaded!')
    } catch (e) { toast.error(getErrorMessage(e)) }
    finally { setGenerating(false) }
  }

  if (loading) return <Spinner text="Loading scan…" />
  if (!scan) return <div className="card text-center py-10 text-gray-400">Scan not found.</div>

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-white">
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-xl font-bold text-white">Security Report</h1>
          <p className="text-gray-400 text-sm">Scan #{id} · {formatDate(scan.scan_date)}</p>
        </div>
      </div>

      <div className="card">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary-600/20 flex items-center justify-center">
                <Shield size={20} className="text-primary-400" />
              </div>
              <div>
                <p className="font-semibold text-white">{scan.file_name}</p>
                <p className="text-sm text-gray-400">{scan.scan_type?.toUpperCase()} scan</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
              <div><span className="text-gray-500">Date:</span> <span className="text-gray-300">{formatDate(scan.scan_date)}</span></div>
              <div><span className="text-gray-500">Findings:</span> <span className="text-gray-300">{scan.finding_count}</span></div>
              <div><span className="text-gray-500">Score:</span> <span className="text-gray-300">{scan.risk_score?.toFixed(1)}/100</span></div>
              <div><span className="text-gray-500">Masked:</span> <span className={scan.is_masked ? 'text-green-400' : 'text-gray-500'}>{scan.is_masked ? 'Yes' : 'No'}</span></div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-400">Risk Level:</span>
              <RiskBadge level={scan.risk_level} />
            </div>
          </div>
          <RiskMeter score={scan.risk_score} level={scan.risk_level} />
        </div>
      </div>

      {/* Categories */}
      {scan.categories && Object.keys(scan.categories).length > 0 && (
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Detected Categories</h3>
          <div className="space-y-2">
            {Object.entries(scan.categories).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <span className="text-sm text-gray-300">{type.replace(/_/g, ' ')}</span>
                <span className="text-sm font-semibold text-white">{count} found</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Download */}
      <div className="card bg-primary-900/20 border-primary-700/50">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h3 className="font-semibold text-white flex items-center gap-2">
              <FileText size={18} className="text-primary-400" /> PDF Security Report
            </h3>
            <p className="text-sm text-gray-400 mt-1">
              Download a professional PDF report with all findings, risk analysis, and recommendations.
              Sensitive values are masked in the report.
            </p>
          </div>
          <button onClick={handleDownload} disabled={generating} className="btn-primary whitespace-nowrap">
            {generating
              ? <span className="animate-spin rounded-full h-4 w-4 border-t-2 border-white" />
              : <Download size={16} />}
            {generating ? 'Generating…' : 'Download PDF'}
          </button>
        </div>
      </div>
    </div>
  )
}
