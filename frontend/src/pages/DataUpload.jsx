import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Loader,
  Trash2,
  ArrowRight,
  Sparkles,
  Brain,
  Zap,
  TrendingUp,
  BarChart3,
  PieChart
} from 'lucide-react'
import { clsx } from 'clsx'
import axios from 'axios'
import toast from 'react-hot-toast'

export default function DataUpload() {
  const navigate = useNavigate()
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: file.size,
      status: 'pending', // pending, uploading, success, error
      progress: 0,
      error: null
    }))
    
    setFiles(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv'],
      'text/plain': ['.csv']
    },
    multiple: true,
    maxFiles: 10,
    maxSize: 50 * 1024 * 1024 // 50MB
  })

  const uploadFile = async (fileItem) => {
    const formData = new FormData()
    formData.append('file', fileItem.file)
    formData.append('folder', 'uploads')

    try {
      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      ))

      const response = await axios.post('/api/upload-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          setFiles(prev => prev.map(f => 
            f.id === fileItem.id 
              ? { ...f, progress }
              : f
          ))
        }
      })

      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'success', progress: 100 }
          : f
      ))

      setUploadedFiles(prev => [...prev, {
        ...response.data.file_details,
        id: fileItem.id,
        uploadedAt: new Date().toISOString()
      }])

      toast.success(`${fileItem.name} uploaded successfully!`)

    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Upload failed'
      
      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'error', error: errorMessage }
          : f
      ))

      toast.error(`Failed to upload ${fileItem.name}: ${errorMessage}`)
    }
  }

  const uploadAllFiles = async () => {
    setUploading(true)
    const pendingFiles = files.filter(f => f.status === 'pending')
    
    for (const file of pendingFiles) {
      await uploadFile(file)
    }
    
    setUploading(false)
  }

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const clearAllFiles = () => {
    setFiles([])
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="relative z-10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-2"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Banta
            </span>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="px-6 pt-12 pb-20">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-full text-indigo-700 text-sm font-medium mb-6"
            >
              <Sparkles className="w-4 h-4" />
              Your Deeply Skilled Data Assistant
            </motion.div>
            
            <h1 className="text-6xl md:text-7xl font-black mb-6">
              <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Transform Data
              </span>
              <br />
              <span className="text-gray-900">Into Intelligence</span>
            </h1>
            
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
              Upload your CSV files and ask natural language questions. Banta's AI-powered engine 
              will analyze your data and provide <span className="font-semibold text-indigo-600">instant, actionable insights</span> 
              that drive real business decisions.
            </p>

            {/* Feature Highlights */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex flex-wrap justify-center gap-8 mb-12"
            >
              <div className="flex items-center gap-2 text-gray-700">
                <Zap className="w-5 h-5 text-yellow-500" />
                <span className="font-medium">Instant Analysis</span>
              </div>
              <div className="flex items-center gap-2 text-gray-700">
                <TrendingUp className="w-5 h-5 text-green-500" />
                <span className="font-medium">Predictive Insights</span>
              </div>
              <div className="flex items-center gap-2 text-gray-700">
                <BarChart3 className="w-5 h-5 text-blue-500" />
                <span className="font-medium">Beautiful Visualizations</span>
              </div>
            </motion.div>
          </motion.div>
          {/* Upload Controls */}
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex justify-center gap-4 mb-8"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={clearAllFiles}
                className="px-6 py-3 bg-white text-gray-700 border-2 border-gray-200 rounded-xl font-semibold hover:border-gray-300 transition-all duration-200 shadow-sm"
                disabled={uploading}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Clear All
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={uploadAllFiles}
                className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                disabled={uploading || files.every(f => f.status !== 'pending')}
              >
                {uploading ? (
                  <>
                    <Loader className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Upload & Analyze
                  </>
                )}
              </motion.button>
            </motion.div>
          )}

          {/* Premium Upload Area */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="max-w-4xl mx-auto"
          >
            <motion.div
              {...getRootProps()}
              className={clsx(
                'relative overflow-hidden rounded-2xl border-2 border-dashed transition-all duration-500 cursor-pointer group',
                isDragActive
                  ? 'border-indigo-400 bg-gradient-to-br from-indigo-50 to-purple-50 scale-105'
                  : 'border-gray-300 hover:border-indigo-300 hover:bg-gradient-to-br hover:from-indigo-25 hover:to-purple-25'
              )}
            >
              <input {...getInputProps()} />
              
              {/* Animated Background */}
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-600/5 via-purple-600/5 to-pink-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              
              {/* Floating Icons Animation */}
              <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                  animate={{ 
                    y: [0, -10, 0],
                    rotate: [0, 5, -5, 0] 
                  }}
                  transition={{ 
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut" 
                  }}
                  className="absolute top-8 left-8 text-indigo-200"
                >
                  <BarChart3 className="w-6 h-6" />
                </motion.div>
                <motion.div
                  animate={{ 
                    y: [0, 15, 0],
                    rotate: [0, -5, 5, 0] 
                  }}
                  transition={{ 
                    duration: 5,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 1 
                  }}
                  className="absolute top-12 right-12 text-purple-200"
                >
                  <PieChart className="w-8 h-8" />
                </motion.div>
                <motion.div
                  animate={{ 
                    y: [0, -20, 0],
                    rotate: [0, 10, -10, 0] 
                  }}
                  transition={{ 
                    duration: 6,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 2 
                  }}
                  className="absolute bottom-8 left-16 text-pink-200"
                >
                  <TrendingUp className="w-7 h-7" />
                </motion.div>
              </div>

              <div className="relative z-10 p-16 text-center">
                <motion.div
                  animate={isDragActive ? { scale: 1.2, rotateY: 180 } : { scale: 1, rotateY: 0 }}
                  transition={{ duration: 0.3, type: "spring" }}
                  className="relative"
                >
                  <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-2xl">
                    <Upload className="w-10 h-10 text-white" />
                  </div>
                  
                  {/* Pulse animation around upload icon */}
                  <div className="absolute inset-0 w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-indigo-400 to-purple-500 animate-ping opacity-20" />
                </motion.div>

                {isDragActive ? (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <h3 className="text-2xl font-bold text-indigo-700 mb-2">
                      Perfect! Drop your files now
                    </h3>
                    <p className="text-indigo-600 text-lg">
                      Release to begin the magic ✨
                    </p>
                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">
                      Ready to unlock your data's potential?
                    </h3>
                    <p className="text-gray-600 text-lg mb-6">
                      Drop your CSV files here or click to browse
                    </p>
                    
                    <div className="inline-flex items-center gap-3 px-6 py-3 bg-white/80 backdrop-blur-sm rounded-xl text-gray-600 text-sm font-medium border border-gray-200">
                      <FileText className="w-5 h-5 text-indigo-500" />
                      <span>Supports CSV files up to 50MB each</span>
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Premium File List */}
      <AnimatePresence>
        {files.length > 0 && (
          <div className="px-6 pb-12">
            <div className="max-w-4xl mx-auto">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-2xl overflow-hidden"
              >
                <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-indigo-50 to-purple-50">
                  <h3 className="text-xl font-bold text-gray-900 flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center">
                      <FileText className="w-4 h-4 text-white" />
                    </div>
                    Your Files ({files.length})
                  </h3>
                </div>
                
                <div className="p-6 space-y-4">
                  {files.map((fileItem, index) => (
                    <motion.div
                      key={fileItem.id}
                      initial={{ opacity: 0, x: -30, scale: 0.95 }}
                      animate={{ opacity: 1, x: 0, scale: 1 }}
                      exit={{ opacity: 0, x: 30, scale: 0.95 }}
                      transition={{ delay: index * 0.1 }}
                      className="group relative overflow-hidden bg-gradient-to-r from-gray-50 to-gray-50/50 hover:from-indigo-50 hover:to-purple-50 rounded-xl border border-gray-200 hover:border-indigo-200 transition-all duration-300"
                    >
                      <div className="flex items-center gap-4 p-4">
                        <motion.div 
                          whileHover={{ rotate: 360 }}
                          transition={{ duration: 0.5 }}
                          className={clsx(
                            'w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm',
                            fileItem.status === 'success' && 'bg-gradient-to-r from-green-400 to-emerald-500 text-white',
                            fileItem.status === 'error' && 'bg-gradient-to-r from-red-400 to-pink-500 text-white',
                            fileItem.status === 'uploading' && 'bg-gradient-to-r from-blue-400 to-indigo-500 text-white',
                            fileItem.status === 'pending' && 'bg-gradient-to-r from-gray-400 to-gray-500 text-white'
                          )}
                        >
                          {fileItem.status === 'success' && <CheckCircle className="w-6 h-6" />}
                          {fileItem.status === 'error' && <XCircle className="w-6 h-6" />}
                          {fileItem.status === 'uploading' && <Loader className="w-6 h-6 animate-spin" />}
                          {fileItem.status === 'pending' && <FileText className="w-6 h-6" />}
                        </motion.div>

                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-gray-900 truncate text-lg">
                            {fileItem.name}
                          </p>
                          <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                            <span className="font-medium">{formatFileSize(fileItem.size)}</span>
                            {fileItem.status === 'uploading' && (
                              <span className="text-blue-600 font-semibold">{fileItem.progress}%</span>
                            )}
                            {fileItem.status === 'success' && (
                              <span className="flex items-center gap-1 text-green-600 font-semibold">
                                <Sparkles className="w-3 h-3" />
                                Ready for Analysis
                              </span>
                            )}
                            {fileItem.error && (
                              <span className="text-red-600 font-medium">{fileItem.error}</span>
                            )}
                          </div>
                          
                          {fileItem.status === 'uploading' && (
                            <div className="mt-3">
                              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${fileItem.progress}%` }}
                                  className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full"
                                  transition={{ duration: 0.3 }}
                                />
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                          {fileItem.status === 'pending' && (
                            <motion.button
                              whileHover={{ scale: 1.1 }}
                              whileTap={{ scale: 0.9 }}
                              onClick={() => uploadFile(fileItem)}
                              className="p-3 text-blue-600 hover:bg-blue-100 rounded-xl transition-colors"
                              title="Upload file"
                            >
                              <Upload className="w-5 h-5" />
                            </motion.button>
                          )}
                          
                          <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => removeFile(fileItem.id)}
                            className="p-3 text-red-600 hover:bg-red-100 rounded-xl transition-colors"
                            title="Remove file"
                          >
                            <Trash2 className="w-5 h-5" />
                          </motion.button>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </div>
          </div>
        )}
      </AnimatePresence>

      {/* Success State - Ready for Analysis */}
      {uploadedFiles.length > 0 && (
        <div className="px-6 pb-12">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
              className="relative overflow-hidden bg-gradient-to-r from-green-400 via-emerald-500 to-teal-500 rounded-2xl shadow-2xl"
            >
              {/* Animated Background Pattern */}
              <div className="absolute inset-0 bg-white/10">
                <motion.div
                  animate={{ 
                    backgroundPosition: ['0% 0%', '100% 100%'],
                  }}
                  transition={{ 
                    duration: 20,
                    repeat: Infinity,
                    ease: "linear" 
                  }}
                  className="w-full h-full opacity-30"
                  style={{
                    backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)',
                    backgroundSize: '20px 20px'
                  }}
                />
              </div>
              
              <div className="relative z-10 p-8">
                <div className="flex items-center justify-between">
                  <div className="flex items-start gap-4">
                    <motion.div
                      animate={{ rotate: [0, 360] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center"
                    >
                      <Sparkles className="w-8 h-8 text-white" />
                    </motion.div>
                    <div>
                      <h3 className="text-2xl font-bold text-white mb-2">
                        🎉 Perfect! Your data is ready
                      </h3>
                      <p className="text-green-50 text-lg">
                        Now let's unlock insights with Banta's AI-powered analysis engine
                      </p>
                    </div>
                  </div>
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => navigate('/analysis')}
                    className="px-8 py-4 bg-white text-green-600 rounded-xl font-bold hover:bg-green-50 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center gap-3"
                  >
                    <Brain className="w-5 h-5" />
                    Ask Banta Anything
                    <ArrowRight className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      )}

      {/* Premium Guidelines & Features */}
      {uploadedFiles.length === 0 && (
        <div className="px-6 pb-12">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="grid md:grid-cols-2 gap-8"
            >
              {/* Guidelines */}
              <motion.div
                whileHover={{ y: -5 }}
                className="bg-white/80 backdrop-blur-xl rounded-2xl p-8 border border-gray-200/50 shadow-xl"
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                    <AlertCircle className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">Upload Guidelines</h3>
                </div>
                <ul className="space-y-3 text-gray-700">
                  <li className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <span>CSV files up to 50MB each</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <span>Proper column headers required</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <span>UTF-8 encoding recommended</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <span>Multiple file support</span>
                  </li>
                </ul>
              </motion.div>

              {/* What You Can Ask */}
              <motion.div
                whileHover={{ y: -5 }}
                className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-8 border border-indigo-200/50 shadow-xl"
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <Brain className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">What You Can Ask Banta</h3>
                </div>
                <ul className="space-y-3 text-gray-700">
                  <li className="flex items-start gap-3">
                    <TrendingUp className="w-5 h-5 text-indigo-500 flex-shrink-0 mt-0.5" />
                    <span>"Show me sales trends over time"</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <BarChart3 className="w-5 h-5 text-purple-500 flex-shrink-0 mt-0.5" />
                    <span>"Which products generate most profit?"</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <PieChart className="w-5 h-5 text-pink-500 flex-shrink-0 mt-0.5" />
                    <span>"Analyze customer segments by region"</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <Zap className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                    <span>"Predict next quarter's performance"</span>
                  </li>
                </ul>
              </motion.div>
            </motion.div>
          </div>
        </div>
      )}
    </div>
  )
}
