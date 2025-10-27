import axios from 'axios'
import toast from 'react-hot-toast'

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? 'https://your-api-service-name.onrender.com'  // 👈 UPDATE THIS WITH YOUR RENDER URL
    : '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    
    if (error.response?.status === 500) {
      toast.error('Server error. Please try again later.')
    }
    
    return Promise.reject(error)
  }
)

// API endpoints
export const apiEndpoints = {
  // Health check
  health: () => api.get('/health'),
  
  // File upload (CSV and Excel)
  uploadFile: (file, folder = null, onUploadProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    if (folder) {
      formData.append('folder', folder)
    }
    
    return api.post('/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    })
  },
  
  // Legacy CSV upload (for backward compatibility)
  uploadCSV: (file, folder = null, onUploadProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    if (folder) {
      formData.append('folder', folder)
    }
    
    return api.post('/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    })
  },
  
  // File management
  listFiles: (folder = null) => {
    const params = folder ? { folder } : {}
    return api.get('/list-files', { params })
  },
  
  // Future AI endpoints
  askQuestion: (question, fileId = null) => {
    return api.post('/ask-question', { question, file_id: fileId })
  },
  
  generateReport: (fileId, reportType = 'summary') => {
    return api.post('/generate-report', { file_id: fileId, report_type: reportType })
  },
}

// Helper functions
export const handleApiError = (error, customMessage = null) => {
  const message = customMessage || 
    error.response?.data?.detail || 
    error.message || 
    'An unexpected error occurred'
  
  toast.error(message)
  console.error('API Error:', error)
}

export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export default api
