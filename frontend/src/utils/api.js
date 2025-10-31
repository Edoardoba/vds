import axios from 'axios'
import toast from 'react-hot-toast'

// Get API base URL from environment variables or fallback
const getApiBaseUrl = () => {
  // For Vite, environment variables must be prefixed with VITE_
  const envApiUrl = import.meta.env.VITE_API_BASE_URL
  
  if (envApiUrl) {
    return envApiUrl
  }
  
  // Fallback logic
  if (import.meta.env.PROD) {
    // Production environment - This should be set via VITE_API_BASE_URL in Vercel
    // Fallback to your actual Render URL if env var is not set
    return 'https://vds-1.onrender.com'
  }
  
  // Development environment
  return '/api'
}

// Create axios instance with default config
const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: import.meta.env.VITE_API_TIMEOUT || 120000, // Increased to 2 minutes for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Temporarily disabled for CORS debugging
})

// Log API URL for debugging (remove in production)
console.log('🔗 API Base URL:', getApiBaseUrl())

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
  
  // AI Analysis endpoints
  analyzeData: (file, question, onUploadProgress, selectedAgents = null, signal = null) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('question', question)
    if (selectedAgents && Array.isArray(selectedAgents) && selectedAgents.length > 0) {
      formData.append('selected_agents', JSON.stringify(selectedAgents))
    }
    
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
      timeout: 600000, // 10 minutes for analysis
    }
    
    if (signal) {
      config.signal = signal
    }
    
    return api.post('/analyze-data', formData, config)
  },
  
  planAnalysis: (file, question, onUploadProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('question', question)
    
    return api.post('/plan-analysis', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
      timeout: 180000, // 3 minutes should be enough for planning
    })
  },
  
  previewData: (file, onUploadProgress, signal = null) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    }
    
    if (signal) {
      config.signal = signal
    }
    
    return api.post('/preview-data', formData, config)
  },
  
  getAvailableAgents: () => {
    return api.get('/agents/available')
  },

  // Cancel ongoing analysis
  cancelAnalysis: (analysisId) => {
    return api.post('/cancel-analysis', { analysis_id: analysisId })
  },

  // ========== NEW: History & Analytics Endpoints ==========

  // Get recent analysis history
  getRecentHistory: (limit = 10) => {
    return api.get('/history/recent', { params: { limit } })
  },

  // Get specific analysis by ID
  getAnalysisById: (analysisId) => {
    return api.get(`/history/${analysisId}`)
  },

  // Get analytics statistics
  getAnalyticsStatistics: () => {
    return api.get('/analytics/statistics')
  },

  // Get agent performance metrics
  getAgentPerformance: () => {
    return api.get('/analytics/agent-performance')
  },

  // Clear expired cache
  clearExpiredCache: () => {
    return api.delete('/cache/clear-expired')
  },

  // Legacy endpoints (maintained for backward compatibility)
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
