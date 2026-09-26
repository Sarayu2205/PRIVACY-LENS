import { format, parseISO } from 'date-fns'

export function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  try { return format(parseISO(dateStr), 'dd MMM yyyy, HH:mm') }
  catch { return dateStr }
}

export function getRiskColor(level) {
  const map = {
    CRITICAL: 'text-red-400',
    HIGH:     'text-orange-400',
    MEDIUM:   'text-yellow-400',
    LOW:      'text-green-400',
  }
  return map[level] || 'text-gray-400'
}

export function getRiskBadge(level) {
  const map = {
    CRITICAL: 'badge-critical',
    HIGH:     'badge-high',
    MEDIUM:   'badge-medium',
    LOW:      'badge-low',
  }
  return map[level] || 'badge-low'
}

export function getRiskBg(level) {
  const map = {
    CRITICAL: 'bg-red-900/30 border-red-700',
    HIGH:     'bg-orange-900/30 border-orange-700',
    MEDIUM:   'bg-yellow-900/30 border-yellow-700',
    LOW:      'bg-green-900/30 border-green-700',
  }
  return map[level] || 'bg-gray-800 border-gray-700'
}

export function getErrorMessage(error) {
  return (
    error?.response?.data?.detail ||
    error?.message ||
    'An unexpected error occurred.'
  )
}

export function truncate(str, n = 40) {
  if (!str) return ''
  return str.length > n ? str.slice(0, n) + '…' : str
}
