import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Type, Scan, AlertCircle, X } from 'lucide-react'
import { scanText } from '../services/scanService.js'
import { getErrorMessage } from '../utils/helpers.js'
import toast from 'react-hot-toast'

const PLACEHOLDER = `Paste your text here to scan for sensitive information...

Example:
Name: Arjun Kumar
Email: arjun.kumar@example.com
Phone: 9876543210
PAN: ABCDE1234F
API_KEY=my_test_api_key_1234567890abcdefghijklmn`

export default function ScanText() {
  const navigate = useNavigate()
  const [text, setText] = useState('')
  const [label, setLabel] = useState('Pasted Text')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const charCount = text.length
  const MAX = 500000

  const handleScan = async () => {
    if (!text.trim()) { setError('Please enter some text to scan.'); return }
    setLoading(true)
    setError('')
    try {
      const result = await scanText(text, label)
      toast.success(`Scan complete — ${result.finding_count} finding(s) detected.`)
      navigate(`/scan/result/${result.scan_id}`, { state: { result } })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Text Scanner</h1>
        <p className="text-gray-400 text-sm mt-1">Paste any text to detect sensitive information</p>
      </div>

      {/* Label input */}
      <div>
        <label className="block text-sm text-gray-400 mb-1.5">Scan Label (optional)</label>
        <input type="text" className="input-field max-w-xs"
          placeholder="e.g. Resume Draft, Config File"
          value={label} onChange={e => setLabel(e.target.value)} />
      </div>

      {/* Text area */}
      <div className="relative">
        <textarea
          className="input-field h-72 resize-none font-mono text-sm leading-relaxed"
          placeholder={PLACEHOLDER}
          value={text}
          onChange={e => { setText(e.target.value); setError('') }}
          maxLength={MAX}
        />
        {text && (
          <button onClick={() => setText('')}
            className="absolute top-3 right-3 text-gray-500 hover:text-gray-300">
            <X size={16} />
          </button>
        )}
        <div className={`text-right text-xs mt-1 ${charCount > MAX * 0.9 ? 'text-orange-400' : 'text-gray-600'}`}>
          {charCount.toLocaleString()} / {MAX.toLocaleString()} characters
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-3 p-4 rounded-lg bg-red-900/30 border border-red-700 text-red-300">
          <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      <div className="flex gap-3">
        <button onClick={handleScan} disabled={loading || !text.trim()} className="btn-primary">
          {loading ? <span className="animate-spin rounded-full h-4 w-4 border-t-2 border-white" /> : <Scan size={17} />}
          {loading ? 'Scanning…' : 'Scan Text'}
        </button>
        <button onClick={() => setText('')} className="btn-secondary">
          <X size={17} /> Clear
        </button>
      </div>

      {/* Quick test */}
      <div className="card bg-gray-800/50">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">Quick test — paste sample data</h4>
        <button
          onClick={() => setText(`Name: Priya Sharma\nEmail: priya.sharma@gmail.com\nPhone: +91 9876543210\nAadhaar: 2345 6789 0123\nPAN: ABCDE1234F\nPassword: MySecret@123\nAPI_KEY=my_test_api_key_1234567890abcdefghijklmn\nAccount No: 123456789012 (Bank: HDFC, IFSC: HDFC0001234)`)}
          className="text-xs text-primary-400 hover:text-primary-300 underline">
          Load sample sensitive data →
        </button>
      </div>
    </div>
  )
}
