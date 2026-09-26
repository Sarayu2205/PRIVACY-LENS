import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, Scan, AlertCircle } from 'lucide-react'
import { scanFile } from '../services/scanService.js'
import { getErrorMessage } from '../utils/helpers.js'
import toast from 'react-hot-toast'

const ACCEPTED = { 'text/plain': ['.txt'], 'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'image/png': ['.png'], 'image/jpeg': ['.jpg', '.jpeg'] }

const MAX_SIZE = 10 * 1024 * 1024 // 10 MB

export default function ScanFile() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [progress, setProgress] = useState(0)

  const onDrop = useCallback((accepted, rejected) => {
    setError('')
    if (rejected.length > 0) {
      const msg = rejected[0].errors?.[0]?.message || 'Invalid file.'
      setError(msg)
      return
    }
    if (accepted.length > 0) setFile(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, maxFiles: 1, maxSize: MAX_SIZE, accept: ACCEPTED,
  })

  const handleScan = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    setProgress(0)

    // Simulate progress
    const interval = setInterval(() => setProgress(p => Math.min(p + 8, 85)), 300)

    try {
      const result = await scanFile(file)
      clearInterval(interval)
      setProgress(100)
      toast.success(`Scan complete — ${result.finding_count} finding(s) detected.`)
      navigate(`/scan/result/${result.scan_id}`, { state: { result } })
    } catch (err) {
      clearInterval(interval)
      setProgress(0)
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">Scan Document</h1>
        <p className="text-gray-400 text-sm mt-1">Upload a file to scan for sensitive information</p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200 ${
          isDragActive ? 'border-primary-500 bg-primary-600/10' : 'border-gray-700 hover:border-gray-600 bg-gray-900'
        }`}
      >
        <input {...getInputProps()} />
        <Upload size={36} className={`mx-auto mb-3 ${isDragActive ? 'text-primary-400' : 'text-gray-500'}`} />
        {isDragActive ? (
          <p className="text-primary-400 font-semibold">Drop it here!</p>
        ) : (
          <>
            <p className="text-gray-300 font-semibold">Drag & drop a file here, or click to select</p>
            <p className="text-gray-500 text-sm mt-1">Supports: TXT, PDF, DOCX, PNG, JPG · Max 10 MB</p>
          </>
        )}
      </div>

      {/* Selected file */}
      {file && (
        <div className="card flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-primary-600/20 flex items-center justify-center">
              <File size={18} className="text-primary-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-white">{file.name}</p>
              <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
          <button onClick={() => setFile(null)} className="text-gray-500 hover:text-gray-300">
            <X size={18} />
          </button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 p-4 rounded-lg bg-red-900/30 border border-red-700 text-red-300">
          <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Progress */}
      {loading && (
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Scanning for sensitive data…</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3">
        <button onClick={handleScan} disabled={!file || loading} className="btn-primary flex-1 justify-center">
          {loading ? <span className="animate-spin rounded-full h-4 w-4 border-t-2 border-white" /> : <Scan size={17} />}
          {loading ? 'Scanning…' : 'Start Scan'}
        </button>
      </div>

      {/* Info */}
      <div className="card bg-gray-800/50">
        <h4 className="text-sm font-semibold text-gray-300 mb-2">What we detect</h4>
        <div className="grid grid-cols-2 gap-1 text-xs text-gray-500">
          {['Emails', 'Phone numbers', 'PAN-like IDs', 'Aadhaar-like IDs',
            'Credit/Debit cards', 'Bank accounts', 'Passwords', 'API keys',
            'JWT tokens', 'Private keys', 'Addresses', 'Dates of birth'].map(item => (
            <span key={item} className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />{item}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
