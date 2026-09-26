import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Trash2, Eye, ChevronLeft, ChevronRight, FileText } from 'lucide-react'
import { getHistory, deleteScan } from '../services/scanService.js'
import { formatDate } from '../utils/helpers.js'
import RiskBadge from '../components/RiskBadge.jsx'
import Spinner from '../components/Spinner.jsx'
import toast from 'react-hot-toast'

const PAGE_SIZE = 10

export default function History() {
  const navigate = useNavigate()
  const [scans, setScans]     = useState([])
  const [total, setTotal]     = useState(0)
  const [page, setPage]       = useState(0)
  const [search, setSearch]   = useState('')
  const [filter, setFilter]   = useState('ALL')
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)

  const load = async (p = 0) => {
    setLoading(true)
    try {
      const data = await getHistory(p * PAGE_SIZE, PAGE_SIZE)
      setScans(data.scans)
      setTotal(data.total)
    } catch { toast.error('Failed to load history.') }
    finally { setLoading(false) }
  }

  useEffect(() => { load(page) }, [page])

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (!confirm('Delete this scan and all its findings?')) return
    setDeleting(id)
    try {
      await deleteScan(id)
      toast.success('Scan deleted.')
      load(page)
    } catch { toast.error('Delete failed.') }
    finally { setDeleting(null) }
  }

  const filtered = scans.filter(s => {
    const matchSearch = s.file_name.toLowerCase().includes(search.toLowerCase())
    const matchFilter = filter === 'ALL' || s.risk_level === filter
    return matchSearch && matchFilter
  })

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Scan History</h1>
        <p className="text-gray-400 text-sm mt-0.5">All your previous scans — {total} total</p>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input className="input-field pl-9 py-2 text-sm" placeholder="Search by file name…"
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="input-field w-auto py-2 text-sm"
          value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="ALL">All Levels</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      {loading ? <Spinner text="Loading history…" /> : (
        <>
          {filtered.length === 0 ? (
            <div className="card text-center py-12">
              <FileText size={32} className="mx-auto text-gray-600 mb-3" />
              <p className="text-gray-400">No scans found.</p>
              <button onClick={() => navigate('/scan/file')} className="btn-primary mt-4 mx-auto">
                Start your first scan →
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-gray-800">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-800/80 text-gray-400 uppercase text-xs tracking-wider">
                    <th className="px-4 py-3 text-left">File</th>
                    <th className="px-4 py-3 text-left">Date</th>
                    <th className="px-4 py-3 text-left">Type</th>
                    <th className="px-4 py-3 text-left">Findings</th>
                    <th className="px-4 py-3 text-left">Risk</th>
                    <th className="px-4 py-3 text-left">Masked</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(s => (
                    <tr key={s.id}
                      className="border-t border-gray-800 hover:bg-gray-800/40 cursor-pointer transition-colors"
                      onClick={() => navigate(`/scan/result/${s.id}`)}>
                      <td className="px-4 py-3">
                        <p className="font-medium text-white truncate max-w-48">{s.file_name}</p>
                      </td>
                      <td className="px-4 py-3 text-gray-400 whitespace-nowrap">{formatDate(s.scan_date)}</td>
                      <td className="px-4 py-3">
                        <span className="text-xs px-2 py-0.5 rounded bg-gray-700 text-gray-300">
                          {s.scan_type?.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-300">{s.finding_count}</td>
                      <td className="px-4 py-3"><RiskBadge level={s.risk_level} /></td>
                      <td className="px-4 py-3">
                        {s.is_masked
                          ? <span className="text-green-400 text-xs">✓ Masked</span>
                          : <span className="text-gray-500 text-xs">—</span>}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2" onClick={e => e.stopPropagation()}>
                          <button onClick={() => navigate(`/scan/result/${s.id}`)}
                            className="text-gray-400 hover:text-primary-400 transition-colors">
                            <Eye size={16} />
                          </button>
                          <button onClick={(e) => handleDelete(s.id, e)} disabled={deleting === s.id}
                            className="text-gray-400 hover:text-red-400 transition-colors">
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, total)} of {total}
              </p>
              <div className="flex gap-2">
                <button onClick={() => setPage(p => p - 1)} disabled={page === 0} className="btn-secondary py-1.5 px-3">
                  <ChevronLeft size={16} />
                </button>
                <span className="text-sm text-gray-400 self-center px-2">{page + 1} / {totalPages}</span>
                <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages - 1} className="btn-secondary py-1.5 px-3">
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
