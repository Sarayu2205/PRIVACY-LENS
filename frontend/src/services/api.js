import axios from 'axios'

// In production (Vercel), API routes are served from the same domain /api
// In development, Vite proxies /api to localhost:8000
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pl_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401 globally — redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('pl_token')
      localStorage.removeItem('pl_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
