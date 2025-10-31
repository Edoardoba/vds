import { useState, useCallback, useEffect, useMemo } from 'react'
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
  PieChart,
  Send,
  MessageCircle,
  Star
} from 'lucide-react'
import { clsx } from 'clsx'
import toast from 'react-hot-toast'
import { apiEndpoints } from '../utils/api'
import AgentResultsTabs from '../components/AgentResultsTabs'
import useWebSocket from '../hooks/useWebSocket'

export default function DataUpload() {
  const navigate = useNavigate()
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [showPrompt, setShowPrompt] = useState(false)
  const [query, setQuery] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isPlanning, setIsPlanning] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [showPlanModal, setShowPlanModal] = useState(false)
  const [plannedAgents, setPlannedAgents] = useState([]) // array of {name, display_name, description, ...}
  const [selectedAgentNames, setSelectedAgentNames] = useState([]) // array of names
  const [showAgentTabs, setShowAgentTabs] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(null)

  // WebSocket connection for real-time progress
  const wsUrl = useMemo(() => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
    const url = baseUrl.replace('http', 'ws') + '/ws/progress'
    console.log('WebSocket URL:', url)
    return url
  }, [])
  
  const { isConnected, lastMessage } = useWebSocket(wsUrl)
  
  // Debug WebSocket connection
  useEffect(() => {
    console.log('WebSocket connection status:', { isConnected, lastMessage })
  }, [isConnected, lastMessage])

  // Handle WebSocket progress updates (LangGraph enhanced)
  useEffect(() => {
    console.log('WebSocket effect triggered:', { lastMessage, showAgentTabs, isConnected })
    
    if (lastMessage && showAgentTabs) {
      console.log('Processing WebSocket message:', lastMessage)
      try {
        setAnalysisProgress(prev => {
          const newProgress = { ...prev }
        
        switch (lastMessage.type) {
          case 'workflow_started':
            newProgress.workflowId = lastMessage.workflow_id
            newProgress.filename = lastMessage.filename
            newProgress.userQuestion = lastMessage.user_question
            newProgress.progress = 0
            newProgress.completedSteps = []
            break
            
          case 'workflow_progress':
            newProgress.progress = lastMessage.progress
            newProgress.completedSteps = lastMessage.completed_steps || []
            newProgress.currentAgent = lastMessage.current_agent
            newProgress.message = lastMessage.message
            break
            
          case 'agent_started':
            newProgress.currentAgent = lastMessage.agent_name
            newProgress.progress = lastMessage.progress
            break
            
          case 'code_generated':
            newProgress.progress = lastMessage.progress
            break
            
          case 'agent_completed':
            // Add the result with success status
            const result = {
              ...lastMessage.result,
              success: lastMessage.success !== false // Default to true if not specified
            }
            newProgress.completedAgents = [...(newProgress.completedAgents || []), result]
            newProgress.currentAgent = null
            newProgress.progress = lastMessage.progress
            break
            
          case 'agent_error':
            newProgress.completedAgents = [...(newProgress.completedAgents || []), {
              agent_name: lastMessage.agent_name,
              success: false,
              error: lastMessage.error
            }]
            newProgress.currentAgent = null
            newProgress.progress = lastMessage.progress
            break
            
          case 'workflow_error':
            newProgress.errors = [...(newProgress.errors || []), {
              step: lastMessage.step,
              error: lastMessage.error
            }]
            newProgress.progress = lastMessage.progress
            break
            
          case 'workflow_completed':
            newProgress.progress = 100
            newProgress.currentAgent = null
            newProgress.success = lastMessage.success
            newProgress.finalReport = lastMessage.final_report
            
            // Set analyzing to false so the "View Full Results" button appears
            setIsAnalyzing(false)
            
            console.log('Workflow completed via WebSocket, final report available')
            console.log('Final report:', lastMessage.final_report)
            break
        }
        
        return newProgress
      })
      } catch (error) {
        console.error('Error processing WebSocket message:', error)
        // Don't crash the app, just log the error
      }
    }
  }, [lastMessage, showAgentTabs])

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
      'application/vnd.ms-excel': ['.csv', '.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/plain': ['.csv']
    },
    multiple: true,
    maxFiles: 10,
    maxSize: 50 * 1024 * 1024 // 50MB (reduced for better reliability)
  })

  const uploadFile = async (fileItem) => {
    try {
      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      ))

      const response = await apiEndpoints.uploadFile(
        fileItem.file,
        'uploads', // folder
        (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          setFiles(prev => prev.map(f => 
            f.id === fileItem.id 
              ? { ...f, progress }
              : f
          ))
        }
      )

      setFiles(prev => prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'success', progress: 100 }
          : f
      ))

      setUploadedFiles(prev => {
        const newUploadedFiles = [...prev, {
          ...response.data.file_details,
          id: fileItem.id,
          uploadedAt: new Date().toISOString()
        }]
        
        // If this is the first successful upload, show prompt interface
        if (newUploadedFiles.length === 1) {
          setShowPrompt(true)
        }
        
        return newUploadedFiles
      })

      toast.success(`${fileItem.name} uploaded successfully!`)

    } catch (error) {
      let errorMessage = 'Upload failed'
      
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage = 'Upload timeout - try a smaller file or check your connection'
      } else if (error.response?.status === 502) {
        errorMessage = 'Server temporarily unavailable - please try again in a moment'
      } else if (error.response?.status === 0 || error.message.includes('Network Error')) {
        errorMessage = 'Network error - check if the server is running'
      } else {
        errorMessage = error.response?.data?.detail || error.message || 'Upload failed'
      }
      
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

  const handleAnalysis = async (e) => {
    e.preventDefault()
    if (!query.trim()) {
      toast.error('Please enter your analysis request')
      return
    }

    if (uploadedFiles.length === 0) {
      toast.error('Please upload at least one file first')
      return
    }

    // Get the first uploaded file for analysis
    const fileToAnalyze = files.find(f => f.status === 'success')?.file
    
    if (!fileToAnalyze) {
      toast.error('No successfully uploaded files found')
      return
    }

    // Step 1: Plan analysis to show agents modal
    setIsPlanning(true)
    setIsAnalyzing(true) // Show spinner immediately when user clicks "Ask Banta"
    try {
      const planResponse = await apiEndpoints.planAnalysis(
        fileToAnalyze,
        query.trim(),
        (progressEvent) => {
          console.log('Planning progress:', progressEvent)
        }
      )

      const agentInfos = planResponse?.data?.selected_agent_infos || []
      const agentNames = agentInfos.map(a => a.name)
      if (agentNames.length === 0) {
        toast.error('No agents were selected during planning')
        setIsPlanning(false)
        setIsAnalyzing(false)
        return
      }
      setPlannedAgents(agentInfos)
      setSelectedAgentNames(agentNames)
      setShowPlanModal(true)
      setIsAnalyzing(false) // Stop spinner when modal is shown so user can interact
    } catch (error) {
      const errorMessage = error?.response?.data?.detail || error.message || 'Failed to plan analysis'
      toast.error(errorMessage)
      setIsAnalyzing(false)
    } finally {
      setIsPlanning(false)
    }
  }

  const toggleAgentSelection = (name) => {
    setSelectedAgentNames(prev => {
      if (prev.includes(name)) {
        return prev.filter(n => n !== name)
      }
      return [...prev, name]
    })
  }

  const confirmRunWithSelection = async () => {
    console.log('Starting analysis with selected agents:', selectedAgentNames)
    console.log('Current state:', { showPlanModal, showAgentTabs, isAnalyzing })
    
    if (selectedAgentNames.length === 0) {
      toast.error('Please keep at least one agent selected')
      return
    }
    const fileToAnalyze = files.find(f => f.status === 'success')?.file
    if (!fileToAnalyze) {
      toast.error('No successfully uploaded files found')
      return
    }
    
    console.log('About to set showAgentTabs to true')

    try {
      // Close plan modal and show agent tabs
      setShowPlanModal(false)
      setShowAgentTabs(true)
      setIsAnalyzing(true)

      // Initialize progress tracking
      setAnalysisProgress({
        currentAgent: null,
        progress: 0,
        completedAgents: [],
        startTime: new Date().toISOString(),
        // Ensure user question is available even if WS event lacks it
        userQuestion: (query || '').trim()
      })

      console.log('Calling analyzeData API...')
      console.log('Selected agents:', selectedAgentNames)
      console.log('WebSocket connected:', isConnected)
      
      // Call the actual API - progress will come via WebSocket
      const response = await apiEndpoints.analyzeData(
        fileToAnalyze,
        query.trim(),
        (progressEvent) => {
          console.log('Analysis progress:', progressEvent)
        },
        selectedAgentNames
      )

      console.log('Analysis API response:', response)
      
      // Always keep the tabs open to show progress, regardless of initial response
      // The WebSocket will handle the real-time updates
      console.log('Analysis API called successfully, keeping tabs open for WebSocket updates')
      
      // Don't set isAnalyzing to false here - let WebSocket handle the completion
      
      // Add a fallback timeout in case WebSocket doesn't work
      setTimeout(() => {
        if (isAnalyzing && analysisProgress && analysisProgress.progress === 0) {
          console.log('WebSocket fallback: No progress received, simulating progress')
          setAnalysisProgress(prev => ({
            ...prev,
            progress: 25,
            message: 'Analysis in progress...',
            currentAgent: selectedAgentNames[0] || 'data_quality_audit'
          }))
        }
      }, 5000) // Wait 5 seconds before fallback

    } catch (error) {
      console.error('Analysis error:', error)
      const errorMessage = error.response?.data?.detail || 'Analysis failed'
      toast.error(errorMessage)
      
      // Update progress to show error
      setAnalysisProgress(prev => ({
        ...prev,
        currentAgent: null,
        completedAgents: [...prev.completedAgents, {
          agent_name: 'error',
          success: false,
          error: errorMessage
        }]
      }))
    } finally {
      setIsAnalyzing(false)
    }
  }

  const resetToUpload = () => {
    setShowPrompt(false)
    setFiles([])
    setUploadedFiles([])
    setQuery('')
    setAnalysisResult(null)
  }

  const closeAgentTabs = () => {
    setShowAgentTabs(false)
    setAnalysisProgress(null)
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
          
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-full text-indigo-700 text-sm font-medium"
          >
            <Sparkles className="w-4 h-4" />
            Your Deeply Skilled Data Assistant
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="px-6 pt-4 pb-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-8"
          >
            <h1 className="text-6xl md:text-7xl font-black mb-6">
              <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Transform Data
              </span>
              <br />
              <span className="text-gray-900">Into Intelligence</span>
            </h1>
            
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
              Upload your CSV and Excel files and ask natural language questions.<br /> Banta's AI-powered engine 
              will analyze your data and provide <span className="font-semibold text-indigo-600">instant, actionable insights </span>  
               that drive real business decisions.
            </p>

          </motion.div>
          {/* Upload Controls - Only show when not in prompt mode */}
          {files.length > 0 && !showPrompt && (
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
                    Upload Data
                  </>
                )}
              </motion.button>
            </motion.div>
          )}

          {/* Conditional Content: Upload or Prompt Interface */}
          {!showPrompt ? (
            /* Premium Upload Area */
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
                      Drop your files here or click to browse
                    </p>
                    
                    <div className="inline-flex items-center gap-3 px-6 py-3 bg-white/80 backdrop-blur-sm rounded-xl text-gray-600 text-sm font-medium border border-gray-200">
                      <FileText className="w-5 h-5 text-indigo-500" />
                      <span>Supports files up to 50MB each</span>
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
            </motion.div>
          ) : (
            /* Premium Prompt Interface */
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
              className="max-w-4xl mx-auto"
            >
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-2xl overflow-hidden">
                <div className="p-8">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                        <Brain className="w-6 h-6 text-white" />
                      </div>
                      <h2 className="text-2xl font-bold text-gray-900">Ask Banta!</h2>
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={resetToUpload}
                      className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors text-sm"
                    >
                      Upload New Files
                    </motion.button>
                  </div>

                  <form onSubmit={handleAnalysis} className="space-y-6">
                    <div>
                      <label htmlFor="query" className="block text-lg font-semibold text-gray-900 mb-3">
                        What insights do you need from your data?
                      </label>
                      <div className="relative">
                        <textarea
                          id="query"
                          value={query}
                          onChange={(e) => setQuery(e.target.value)}
                          rows={4}
                          className="w-full px-6 py-4 text-lg border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 placeholder:text-gray-400 resize-none bg-gray-50/50"
                          placeholder="Ask me anything about your uploaded data... 

Try: 'Show me which products are trending upward this quarter' or 'What patterns do you see in customer behavior?'"
                          disabled={isAnalyzing}
                        />
                        <div className="absolute bottom-4 right-4">
                          <motion.div
                            animate={{ rotate: [0, 360] }}
                            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                            className="w-6 h-6 text-indigo-300"
                          >
                            <Sparkles className="w-6 h-6" />
                          </motion.div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex justify-center">
                      <motion.button
                        whileHover={{ scale: isAnalyzing ? 1 : 1.05 }}
                        whileTap={{ scale: isAnalyzing ? 1 : 0.95 }}
                        type="submit"
                        disabled={isAnalyzing || !query.trim()}
                        className={`px-12 py-4 text-white text-lg font-bold rounded-xl transition-all duration-200 shadow-lg hover:shadow-2xl disabled:cursor-not-allowed flex items-center gap-3 relative overflow-hidden ${
                          isAnalyzing 
                            ? 'bg-gradient-to-r from-indigo-500 to-purple-500' 
                            : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700'
                        }`}
                      >
                        {/* Animated background gradient */}
                        {isAnalyzing && (
                          <motion.div
                            className="absolute inset-0 bg-gradient-to-r from-indigo-400 via-purple-500 to-pink-500"
                            animate={{
                              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                            }}
                            transition={{
                              duration: 2,
                              repeat: Infinity,
                              ease: "easeInOut"
                            }}
                            style={{
                              backgroundSize: '200% 200%'
                            }}
                          />
                        )}
                        
                        {/* Pulsing ring animation */}
                        {isAnalyzing && (
                          <motion.div
                            className="absolute inset-0 rounded-xl border-2 border-white/30"
                            animate={{
                              scale: [1, 1.1, 1],
                              opacity: [0.3, 0.6, 0.3]
                            }}
                            transition={{
                              duration: 1.5,
                              repeat: Infinity,
                              ease: "easeInOut"
                            }}
                          />
                        )}
                        
                        {/* Content */}
                        <div className="relative z-10 flex items-center gap-3">
                          {isAnalyzing ? (
                            <>
                              {/* Sexy multi-layer spinner */}
                              <div className="relative">
                                <motion.div
                                  animate={{ rotate: 360 }}
                                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                  className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full"
                                />
                                <motion.div
                                  animate={{ rotate: -360 }}
                                  transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                                  className="absolute inset-0 w-6 h-6 border-2 border-transparent border-r-white/50 rounded-full"
                                />
                                <motion.div
                                  animate={{ rotate: 360 }}
                                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                  className="absolute inset-1 w-4 h-4 border border-white/20 border-b-white rounded-full"
                                />
                              </div>
                              
                              {/* Animated text */}
                              <motion.span
                                animate={{ opacity: [0.7, 1, 0.7] }}
                                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                              >
                                Banta is analyzing...
                              </motion.span>
                              
                              {/* Floating dots */}
                              <div className="flex gap-1">
                                {[0, 1, 2].map((i) => (
                                  <motion.div
                                    key={i}
                                    className="w-1 h-1 bg-white rounded-full"
                                    animate={{
                                      scale: [0.5, 1, 0.5],
                                      opacity: [0.3, 1, 0.3]
                                    }}
                                    transition={{
                                      duration: 1,
                                      repeat: Infinity,
                                      delay: i * 0.2,
                                      ease: "easeInOut"
                                    }}
                                  />
                                ))}
                              </div>
                            </>
                          ) : (
                            <>
                              <motion.div
                                whileHover={{ rotate: 360 }}
                                transition={{ duration: 0.5 }}
                              >
                                <Brain className="w-5 h-5" />
                              </motion.div>
                              Ask Banta
                              <motion.div
                                whileHover={{ x: 5 }}
                                transition={{ duration: 0.2 }}
                              >
                                <Send className="w-5 h-5" />
                              </motion.div>
                            </>
                          )}
                        </div>
                      </motion.button>
                    </div>
                  </form>
                </div>
              </div>
            </motion.div>
          )}
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

      {/* Agent Results Tabs */}
      <AnimatePresence>
        {showAgentTabs && (
          <div className="fixed inset-0 z-50">
            <AgentResultsTabs
              selectedAgents={selectedAgentNames}
              analysisProgress={analysisProgress}
              onClose={closeAgentTabs}
              isAnalyzing={isAnalyzing}
              navigate={navigate}
            />
          </div>
        )}
      </AnimatePresence>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="px-6 pb-12">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
              className="bg-gradient-to-r from-green-400 via-emerald-500 to-teal-500 rounded-2xl shadow-2xl overflow-hidden mb-6"
            >
              <div className="p-6 text-center">
                <div className="flex items-center justify-center gap-3 text-white">
                  <motion.div
                    animate={{ rotate: [0, 360] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  >
                    <CheckCircle className="w-8 h-8" />
                  </motion.div>
                  <h3 className="text-2xl font-bold">
                    Banta has analyzed your data!
                  </h3>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-2xl overflow-hidden"
            >
              <div className="p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <BarChart3 className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900">Analysis Results</h3>
                </div>
                
                <div className="bg-gray-50 rounded-xl p-6 border-2 border-gray-100">
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 leading-relaxed overflow-x-auto">
                    {JSON.stringify(analysisResult, null, 2)}
                  </pre>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      )}
      
      {/* Plan Modal - Redesigned */}
      <AnimatePresence>
        {showPlanModal && (
          <motion.div 
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* Backdrop with blur */}
            <motion.div 
              className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 via-purple-900/20 to-pink-900/20 backdrop-blur-sm"
              onClick={() => !isAnalyzing && !isPlanning && setShowPlanModal(false)}
            />
            
            {/* Modal Container */}
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="relative z-10 w-full max-w-3xl bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 overflow-hidden"
            >
              {/* Header with gradient - Smaller */}
              <div className="relative p-4 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
                <div className="relative flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <motion.div
                      animate={isPlanning ? { rotate: [0, 360] } : {}}
                      transition={{ duration: 2, repeat: isPlanning ? Infinity : 0, ease: "linear" }}
                      className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/30 shadow-lg"
                    >
                      <Brain className="w-5 h-5 text-white" />
                    </motion.div>
                    <div>
                      <h3 className="text-xl font-bold text-white">
                        {isPlanning ? 'Analyzing Request...' : 'AI Agent Selection'}
                      </h3>
                      <p className="text-white/90 text-xs">
                        {isPlanning 
                          ? 'Selecting the best agents for your analysis' 
                          : `${selectedAgentNames.length} selected`
                        }
                      </p>
                    </div>
                  </div>
                  {!isPlanning && (
                    <button
                      onClick={() => setShowPlanModal(false)}
                      className="p-1.5 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-all"
                    >
                      <XCircle className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Content Area */}
              <div className="p-4">
                {isPlanning ? (
                  <div className="flex flex-col items-center justify-center py-12">
                    <div className="relative mb-4">
                      {/* Outer spinning ring */}
                      <motion.div
                        className="w-20 h-20 border-4 border-indigo-200 border-t-indigo-600 rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                      />
                      {/* Inner pulsing brain */}
                      <motion.div
                        className="absolute inset-0 flex items-center justify-center"
                        animate={{ 
                          scale: [1, 1.15, 1],
                          opacity: [0.8, 1, 0.8]
                        }}
                        transition={{ 
                          duration: 1.5,
                          repeat: Infinity,
                          ease: "easeInOut"
                        }}
                      >
                        <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-xl">
                          <Brain className="w-7 h-7 text-white" />
                        </div>
                      </motion.div>
                    </div>
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-center space-y-2"
                    >
                      <p className="text-lg font-bold text-gray-900">Analyzing Your Request</p>
                      <p className="text-sm text-gray-600">Selecting the most relevant AI agents...</p>
                    </motion.div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Quick Stats Bar - Smaller */}
                    <div className="grid grid-cols-3 gap-3 mb-3">
                      <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-200">
                        <div className="text-xl font-bold text-indigo-700">{plannedAgents.length}</div>
                        <div className="text-xs text-indigo-600 font-medium">Total</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                        <div className="text-xl font-bold text-green-700">{selectedAgentNames.length}</div>
                        <div className="text-xs text-green-600 font-medium">Selected</div>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                        <div className="text-xl font-bold text-purple-700">
                          {plannedAgents.length - selectedAgentNames.length}
                        </div>
                        <div className="text-xs text-purple-600 font-medium">Deselected</div>
                      </div>
                    </div>

                    {/* Agent Cards - Grid Layout with max 3 columns */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[calc(100vh-350px)] overflow-y-auto">
                      {plannedAgents.map((agent, index) => {
                        const isSelected = selectedAgentNames.includes(agent.name)
                        const IconComponent = agent.name.includes('visualization') ? BarChart3 :
                                          agent.name.includes('statistical') ? TrendingUp :
                                          agent.name.includes('quality') ? CheckCircle :
                                          agent.name.includes('churn') ? TrendingUp :
                                          agent.name.includes('customer') ? Star :
                                          agent.name.includes('sales') ? Zap :
                                          Brain
                        
                        return (
                          <motion.label
                            key={agent.name}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.03 }}
                            className={`group relative flex flex-col p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                              isSelected
                                ? 'bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-400 shadow-md'
                                : 'bg-white border-gray-200 hover:border-indigo-300 hover:shadow-sm'
                            }`}
                          >
                            {/* Top Row: Checkbox and Icon */}
                            <div className="flex items-center justify-between mb-2">
                              {/* Custom Checkbox */}
                              <div className="relative">
                                <input
                                  type="checkbox"
                                  className="sr-only"
                                  checked={isSelected}
                                  onChange={() => toggleAgentSelection(agent.name)}
                                />
                                <motion.div
                                  className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                                    isSelected
                                      ? 'bg-gradient-to-br from-indigo-600 to-purple-600 border-indigo-600'
                                      : 'bg-white border-gray-300 group-hover:border-indigo-400'
                                  }`}
                                  whileTap={{ scale: 0.9 }}
                                >
                                  {isSelected && (
                                    <CheckCircle className="w-3.5 h-3.5 text-white" />
                                  )}
                                </motion.div>
                              </div>

                              {/* Icon */}
                              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                                isSelected
                                  ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md'
                                  : 'bg-gray-100 text-gray-600 group-hover:bg-indigo-100 group-hover:text-indigo-600'
                              } transition-all`}>
                                <IconComponent className="w-5 h-5" />
                              </div>
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                              <h4 className="font-bold text-gray-900 text-sm mb-1 line-clamp-1">
                                {agent.display_name || agent.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </h4>
                              {agent.description && (
                                <p className="text-xs text-gray-600 line-clamp-2 leading-snug">
                                  {agent.description}
                                </p>
                              )}
                            </div>

                            {/* Selected Indicator */}
                            {isSelected && (
                              <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="mt-2 flex items-center gap-1 text-xs text-green-700 font-medium"
                              >
                                <CheckCircle className="w-3.5 h-3.5" />
                                <span>Selected</span>
                              </motion.div>
                            )}
                          </motion.label>
                        )
                      })}
                    </div>
                  </div>
                )}
              </div>

              {/* Footer with Actions */}
              <div className="p-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between gap-4">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setShowPlanModal(false)}
                  className="px-6 py-3 rounded-xl text-gray-700 font-semibold hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all border border-gray-300 bg-white"
                  disabled={isAnalyzing || isPlanning}
                >
                  Cancel
                </motion.button>
                
                <div className="flex items-center gap-3 flex-1 justify-end">
                  {!isPlanning && (
                    <div className="text-sm text-gray-600 hidden sm:block">
                      <span className="font-semibold text-indigo-600">{selectedAgentNames.length}</span> of {plannedAgents.length} agents selected
                    </div>
                  )}
                  
                  <motion.button
                    whileHover={{ scale: isAnalyzing ? 1 : 1.02 }}
                    whileTap={{ scale: isAnalyzing ? 1 : 0.98 }}
                    onClick={confirmRunWithSelection}
                    disabled={isAnalyzing || isPlanning || selectedAgentNames.length === 0}
                    className={`relative px-8 py-3 text-white rounded-xl font-bold disabled:cursor-not-allowed flex items-center gap-3 overflow-hidden transition-all duration-200 shadow-lg ${
                      selectedAgentNames.length === 0
                        ? 'bg-gray-300 cursor-not-allowed'
                        : 'bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700'
                    }`}
                  >
                    {/* Animated gradient background */}
                    {isAnalyzing && (
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-indigo-400 via-purple-500 via-pink-500 to-indigo-400"
                        animate={{
                          backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                        }}
                        transition={{
                          duration: 3,
                          repeat: Infinity,
                          ease: "linear"
                        }}
                        style={{
                          backgroundSize: '200% 200%'
                        }}
                      />
                    )}
                    
                    <div className="relative z-10 flex items-center gap-3">
                      {isAnalyzing ? (
                        <>
                          <div className="relative">
                            <motion.div
                              animate={{ rotate: 360 }}
                              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                              className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                            />
                          </div>
                          <span>Analyzing...</span>
                        </>
                      ) : (
                        <>
                          <Zap className="w-5 h-5" />
                          <span>Start Analysis</span>
                          <ArrowRight className="w-4 h-4" />
                        </>
                      )}
                    </div>
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Feature Highlights - Only show in upload mode */}
      {!showPrompt && files.length === 0 && (
        <div className="px-6 pb-8">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="text-center"
            >
              <h3 className="text-xl font-semibold text-gray-800 mb-6">
                Why choose Banta for your data analysis?
              </h3>
              <div className="flex flex-wrap justify-center gap-8">
                <div className="flex items-center gap-3 text-gray-700">
                  <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-semibold">Instant Analysis</span>
                </div>
                <div className="flex items-center gap-3 text-gray-700">
                  <div className="w-10 h-10 bg-gradient-to-r from-green-400 to-emerald-500 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-semibold">Predictive Insights</span>
                </div>
                <div className="flex items-center gap-3 text-gray-700">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-lg flex items-center justify-center">
                    <BarChart3 className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-semibold">Beautiful Visualizations</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      )}

      {/* Success State - Ready for Analysis - Only show in upload mode */}
      {!showPrompt && uploadedFiles.length > 0 && (
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
                    onClick={() => setShowPrompt(true)}
                    className="px-8 py-4 bg-white text-green-600 rounded-xl font-bold hover:bg-green-50 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center gap-3"
                  >
                    <Brain className="w-5 h-5" />
                    Ask Me Anything
                    <ArrowRight className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      )}

      {/* Premium Guidelines & Features - Only show in upload mode */}
      {!showPrompt && uploadedFiles.length === 0 && (
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
