// Axios instance configuration
// In mock mode, this is not actively used - see mock modules instead

import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      const redirect = encodeURIComponent(window.location.href)
      window.location.href = `https://app.akm-advisor.com/auth/login?redirect=${redirect}`
    }
    return Promise.reject(error)
  }
)

export default apiClient
