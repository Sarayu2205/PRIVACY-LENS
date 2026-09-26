import api from './api.js'

export const scanText = (text, label = 'Pasted Text') =>
  api.post('/scan/text', { text, label }).then(r => r.data)

export const scanFile = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/scan/file', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)
}

export const getScan = (id) => api.get(`/scan/${id}`).then(r => r.data)

export const deleteScan = (id) => api.delete(`/scan/${id}`)

export const maskScan = (id) => api.post(`/scan/${id}/mask`).then(r => r.data)

export const getHistory = (skip = 0, limit = 20) =>
  api.get(`/scans?skip=${skip}&limit=${limit}`).then(r => r.data)

export const getDashboardStats = () =>
  api.get('/dashboard/stats').then(r => r.data)

export const generateReport = (scanId) =>
  api.get(`/report/${scanId}/generate`).then(r => r.data)

export const downloadReport = (scanId) =>
  api.get(`/report/${scanId}/download`, { responseType: 'blob' }).then(r => r.data)
