import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Loader, 
  Brain,
  BarChart3,
  TrendingUp,
  FileText,
  Sparkles,
  XCircle,
  ChevronLeft,
  ChevronRight,
  ArrowRight
} from 'lucide-react'
import { clsx } from 'clsx'
import toast from 'react-hot-toast'
import WorkflowVisualization from './WorkflowVisualization'

// Agent descriptions mapping with fun, engaging messages
const AGENT_DESCRIPTIONS = {
  'data_quality_audit': '🔍 Inspecting data quality and finding hidden issues...',
  'data_cleaning': '🧹 Cleaning up messy data and fixing inconsistencies...',
  'exploratory_data_analysis': '🔬 Exploring patterns and uncovering insights...',
  'data_visualization': '📊 Creating stunning charts and visualizations...',
  'statistical_analysis': '📈 Crunching numbers and running statistical tests...',
  'churn_prediction': '🎯 Predicting which customers might leave...',
  'customer_segmentation': '👥 Grouping customers into meaningful segments...',
  'sales_performance_analysis': '💰 Analyzing sales trends and performance metrics...',
  'marketing_roi_analysis': '📣 Calculating marketing ROI and effectiveness...',
  'time_series_analysis': '⏰ Forecasting future trends from time series data...',
  'anomaly_detection': '🚨 Hunting for unusual patterns and outliers...',
  'predictive_modeling': '🤖 Building AI models to predict outcomes...',
  'cohort_analysis': '📅 Analyzing customer cohorts over time...',
  'profitability_analysis': '💵 Diving deep into profit margins and costs...',
  'cash_flow_analysis': '💸 Tracking money flows and liquidity...',
  'employee_performance_analysis': '👔 Evaluating team performance and productivity...',
  'competitive_analysis': '⚔️ Benchmarking against competitors...',
  'seasonal_business_planning': '🌦️ Planning for seasonal business patterns...',
  'operational_bottleneck_detection': '🔧 Identifying process bottlenecks...',
  'customer_acquisition_cost_analysis': '💳 Calculating customer acquisition costs...',
  'ab_testing_analysis': '🧪 Analyzing A/B test results and winners...'
}

// Helper function to get agent descriptions (function declaration for proper hoisting)
function getAgentDescription(agentName) {
  return AGENT_DESCRIPTIONS[agentName] || '🤖 Running AI-powered analysis...'
}

const AgentResultsTabs = ({ 
  selectedAgents = [], 
  analysisProgress, 
  onClose,
  isAnalyzing,
  navigate
}) => {
  const [activeTab, setActiveTab] = useState(0)
  const [agentStatuses, setAgentStatuses] = useState({})

  // Debug logging
  console.log('AgentResultsTabs rendering with:', {
    selectedAgents: selectedAgents?.length,
    hasAnalysisProgress: !!analysisProgress,
    isAnalyzing,
    hasNavigate: !!navigate
  })

  // Safety check
  if (!selectedAgents || selectedAgents.length === 0) {
    return (
      <div className="fixed inset-0 bg-white flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Agents Selected</h2>
          <p className="text-gray-600 mb-4">Please select at least one agent to run analysis.</p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  // Additional safety check for analysisProgress
  if (!analysisProgress) {
    return (
      <div className="fixed inset-0 bg-white flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 text-blue-500 mx-auto mb-4 animate-spin" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Initializing Analysis...</h2>
          <p className="text-gray-600 mb-4">Setting up the analysis workflow.</p>
        </div>
      </div>
    )
  }

  // Navigation functions
  const goToPreviousTab = () => {
    setActiveTab(prev => prev > 0 ? prev - 1 : selectedAgents.length - 1)
  }

  const goToNextTab = () => {
    setActiveTab(prev => prev < selectedAgents.length - 1 ? prev + 1 : 0)
  }

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'ArrowLeft') {
        event.preventDefault()
        goToPreviousTab()
      } else if (event.key === 'ArrowRight') {
        event.preventDefault()
        goToNextTab()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedAgents.length])

  // Initialize agent statuses
  useEffect(() => {
    const initialStatuses = {}
    selectedAgents.forEach((agentName, index) => {
      initialStatuses[agentName] = {
        status: 'pending', // pending, running, completed, error
        progress: 0,
        result: null,
        error: null,
        startTime: null,
        endTime: null
      }
    })
    setAgentStatuses(initialStatuses)
  }, [selectedAgents])

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  // Update agent statuses based on analysis progress (LangGraph enhanced)
  useEffect(() => {
    console.log('AgentResultsTabs - Updating agent statuses:', {
      hasProgress: !!analysisProgress,
      currentAgent: analysisProgress?.currentAgent,
      completedCount: analysisProgress?.completedAgents?.length || 0,
      progress: analysisProgress?.progress
    })
    
    if (analysisProgress) {
      setAgentStatuses(prev => {
        const updated = { ...prev }
        console.log('Previous statuses:', prev)
        
        // First, ensure all selected agents have initial status
        selectedAgents.forEach(agentName => {
          if (!updated[agentName]) {
            updated[agentName] = {
              status: 'pending',
              progress: 0,
              result: null,
              error: null,
              startTime: null,
              endTime: null
            }
          }
        })
        
        // Update running agents - set status to 'running' for all agents in runningAgents list
        const runningAgents = analysisProgress.runningAgents || []
        const currentAgent = analysisProgress.currentAgent

        // Mark all agents in runningAgents as running
        runningAgents.forEach(runningAgentName => {
          const matchingAgent = selectedAgents.find(a =>
            a === runningAgentName ||
            a.replace(/[_-]/g, '') === runningAgentName.replace(/[_-]/g, '') ||
            a.toLowerCase() === runningAgentName.toLowerCase()
          )

          if (matchingAgent && updated[matchingAgent]) {
            const wasNotRunning = updated[matchingAgent].status !== 'running'

            updated[matchingAgent] = {
              ...updated[matchingAgent],
              status: 'running',
              progress: Math.min(analysisProgress.progress || 0, 99), // Don't set to 100 until completed
              startTime: analysisProgress.agentStartTimes?.[runningAgentName] ||
                        analysisProgress.startTime ||
                        updated[matchingAgent].startTime ||
                        new Date().toISOString()
            }

            // Show toast notification when agent starts
            if (wasNotRunning) {
              toast.success(
                `Started: ${matchingAgent.replace(/_/g, ' ')}`,
                { icon: '🚀', duration: 2000 }
              )
            }
          }
        })

        // Also check currentAgent for backwards compatibility
        if (currentAgent && !runningAgents.includes(currentAgent)) {
          const matchingAgent = selectedAgents.find(a =>
            a === currentAgent ||
            a.replace(/[_-]/g, '') === currentAgent.replace(/[_-]/g, '') ||
            a.toLowerCase() === currentAgent.toLowerCase()
          )

          if (matchingAgent && updated[matchingAgent]) {
            const wasNotRunning = updated[matchingAgent].status !== 'running'

            updated[matchingAgent] = {
              ...updated[matchingAgent],
              status: 'running',
              progress: Math.min(analysisProgress.progress || 0, 99),
              startTime: analysisProgress.agentStartTimes?.[currentAgent] ||
                        analysisProgress.startTime ||
                        updated[matchingAgent].startTime ||
                        new Date().toISOString()
            }

            if (wasNotRunning) {
              toast.success(
                `Started: ${matchingAgent.replace(/_/g, ' ')}`,
                { icon: '🚀', duration: 2000 }
              )
            }
          }
        }

        // Update completed agents (handle both success and error cases)
        if (analysisProgress.completedAgents && Array.isArray(analysisProgress.completedAgents)) {
          const seenAgents = new Set()
          analysisProgress.completedAgents.forEach(agentResult => {
            if (agentResult.agent_name) {
              const agentName = agentResult.agent_name
              // Normalize agent name for matching
              const matchingAgent = selectedAgents.find(a => 
                a === agentName || 
                a.replace(/[_-]/g, '') === agentName.replace(/[_-]/g, '') ||
                a.toLowerCase() === agentName.toLowerCase()
              )
              
              if (matchingAgent && !seenAgents.has(agentName)) {
                seenAgents.add(agentName)
                const isSuccess = agentResult.success !== false && 
                                 (!agentResult.execution_result || agentResult.execution_result.success !== false)
                
                const wasNotCompleted = updated[matchingAgent]?.status !== 'completed' && 
                                       updated[matchingAgent]?.status !== 'error'
                
                updated[matchingAgent] = {
                  ...updated[matchingAgent],
                  status: isSuccess ? 'completed' : 'error',
                  progress: 100,
                  result: agentResult,
                  error: agentResult.error || (isSuccess ? null : agentResult.execution_result?.error || 'Execution failed'),
                  endTime: analysisProgress.agentEndTimes?.[agentName] || 
                          new Date().toISOString(),
                  startTime: updated[matchingAgent].startTime || 
                            analysisProgress.agentStartTimes?.[agentName] ||
                            analysisProgress.startTime || 
                            new Date().toISOString()
                }
                
                // Show toast notification when agent completes
                if (wasNotCompleted) {
                  if (isSuccess) {
                    toast.success(
                      `Completed: ${matchingAgent.replace(/_/g, ' ')}`,
                      { icon: '✅', duration: 2000 }
                    )
                  } else {
                    toast.error(
                      `Failed: ${matchingAgent.replace(/_/g, ' ')}`,
                      { duration: 3000 }
                    )
                  }
                }
                
                console.log(`Updated agent status: ${matchingAgent} -> ${isSuccess ? 'completed' : 'error'}`)
              }
            }
          })
        }

        console.log('Updated statuses:', updated)
        return updated
      })
    } else {
      console.log('AgentResultsTabs - No analysisProgress provided')
    }
  }, [analysisProgress, selectedAgents])

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'running':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'border-green-200 bg-green-50'
      case 'running':
        return 'border-blue-200 bg-blue-50'
      case 'error':
        return 'border-red-200 bg-red-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  const getAgentIcon = (agentName) => {
    if (agentName.includes('visualization') || agentName.includes('chart')) {
      return <BarChart3 className="w-4 h-4" />
    } else if (agentName.includes('statistical') || agentName.includes('analysis')) {
      return <TrendingUp className="w-4 h-4" />
    } else if (agentName.includes('quality') || agentName.includes('audit')) {
      return <FileText className="w-4 h-4" />
    } else {
      return <Brain className="w-4 h-4" />
    }
  }

  const renderAgentResult = (agentName) => {
    const status = agentStatuses[agentName]?.status || 'pending'
    const result = agentStatuses[agentName]?.result
    const error = agentStatuses[agentName]?.error
    const startTime = agentStatuses[agentName]?.startTime
    const endTime = agentStatuses[agentName]?.endTime

    if (status === 'pending') {
      return (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-center h-64 text-gray-500"
        >
          <div className="text-center">
            <motion.div
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            </motion.div>
            <p className="text-lg font-medium">Waiting to start...</p>
            <p className="text-sm">This agent will begin analysis shortly</p>
          </div>
        </motion.div>
      )
    }

    if (status === 'running') {
      const progress = agentStatuses[agentName]?.progress || 0
      const duration = startTime ? Math.floor((Date.now() - new Date(startTime).getTime()) / 1000) : 0
      
      return (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center justify-center h-64"
        >
          <div className="text-center max-w-md">
            <div className="relative mb-4">
              <motion.div
                animate={{ 
                  scale: [1, 1.1, 1],
                  opacity: [1, 0.8, 1]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Loader className="w-12 h-12 mx-auto text-blue-500 animate-spin" />
              </motion.div>
              {/* Pulsing ring around spinner */}
              <motion.div
                className="absolute inset-0 w-12 h-12 mx-auto border-2 border-blue-300 rounded-full"
                animate={{ 
                  scale: [1, 1.5, 1],
                  opacity: [0.5, 0, 0.5]
                }}
                transition={{ 
                  duration: 1.5, 
                  repeat: Infinity,
                  ease: "easeOut"
                }}
              />
            </div>
            
            <motion.p
              key={agentName}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-lg font-semibold text-blue-800 mb-3"
            >
              {agentName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </motion.p>

            <motion.p
              className="text-base text-blue-600 mb-2 font-medium"
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {(() => {
                try {
                  return getAgentDescription(agentName) || '🤖 Running AI-powered analysis...'
                } catch (error) {
                  console.error('Error getting agent description:', error)
                  return '🤖 Running AI-powered analysis...'
                }
              })()}
            </motion.p>
            
            {duration > 0 && (
              <p className="text-xs text-gray-500 mb-4">Running for {duration}s</p>
            )}
            
            <div className="w-full bg-gray-200 rounded-full h-3 mb-2 overflow-hidden">
              <motion.div
                className="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 h-3 rounded-full relative"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              >
                {/* Animated shimmer effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ 
                    duration: 1.5, 
                    repeat: Infinity,
                    ease: "linear"
                  }}
                />
              </motion.div>
            </div>
            <p className="text-xs text-gray-500 font-medium">{progress}% complete</p>
          </div>
        </motion.div>
      )
    }

    if (status === 'error') {
      const errorMessage = agentStatuses[agentName]?.error || 'An error occurred during analysis'
      return (
        <div className="flex items-center justify-center h-64 text-red-600">
          <div className="text-center">
            <XCircle className="w-12 h-12 mx-auto mb-4" />
            <p className="text-lg font-medium">Analysis Failed</p>
            <p className="text-sm text-gray-600 mt-2">{errorMessage}</p>
          </div>
        </div>
      )
    }

    if (status === 'completed' && result) {
      return (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="p-6 space-y-4"
        >
          {/* Results */}
          {result.execution_result?.success && (
            <div className="space-y-4">
              {/* Insights */}
              {result.code_result?.insights && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 mb-2 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Key Insights
                  </h4>
                  <p className="text-sm text-blue-700">{result.code_result.insights}</p>
                </div>
              )}

              {/* Output Files */}
              {result.execution_result?.output_files?.length > 0 && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-2">Generated Files</h4>
                  <div className="space-y-2">
                    {result.execution_result.output_files.map((file, index) => (
                      <div key={index} className="flex items-center gap-2 text-sm text-gray-600">
                        <FileText className="w-4 h-4" />
                        <span>{file.filename}</span>
                        <span className="text-xs text-gray-400">({file.size} bytes)</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Raw Output */}
              {result.execution_result?.output && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-2">Analysis Output</h4>
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto">
                    {result.execution_result.output}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* Error in execution */}
          {!result.execution_result?.success && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="font-semibold text-red-800 mb-2">Execution Error</h4>
              <p className="text-sm text-red-700">{result.execution_result?.error || 'Unknown error occurred'}</p>
            </div>
          )}
        </motion.div>
      )
    }

    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p className="text-lg font-medium">Unknown Status</p>
        </div>
      </div>
    )
  }

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={(e) => {
        /* Close on backdrop click */
        if (e.target === e.currentTarget) {
          onClose()
        }
      }}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-6xl h-[calc(100vh-2rem)] bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col relative"
      >
        {/* Header */}
        <div className="p-4 sm:p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div className="min-w-0 flex-1">
                <h2 className="text-lg sm:text-xl font-bold text-gray-900 truncate">Agent Analysis Progress</h2>
                <div className="flex items-center gap-2">
                  <p className="text-sm text-gray-600 truncate">
                    {isAnalyzing ? 'Analysis in progress...' : 'Analysis completed'}
                  </p>
                  {analysisProgress?.currentAgent && (
                    <motion.span
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium flex items-center gap-1"
                    >
                      <Loader className="w-3 h-3 animate-spin" />
                      {analysisProgress.currentAgent.replace(/_/g, ' ')}
                    </motion.span>
                  )}
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0 ml-2"
              title="Close"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Workflow Visualization - Horizontal chart with all agents and flow */}
        {analysisProgress && (
          <div className="border-b border-gray-200 flex-shrink-0">
            <WorkflowVisualization 
              analysisProgress={analysisProgress}
              selectedAgents={selectedAgents}
              className="m-4"
            />
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200 bg-white flex-shrink-0">
          <div className="flex items-center">
            {/* Previous Arrow */}
            <button
              onClick={goToPreviousTab}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0"
              disabled={selectedAgents.length <= 1}
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            {/* Tab List - Scrollable */}
            <div className="flex overflow-x-auto flex-1 scrollbar-hide">
              {selectedAgents.map((agentName, index) => {
                const status = agentStatuses[agentName]?.status || 'pending'
                const isCurrent = analysisProgress?.currentAgent === agentName
                
                return (
                  <motion.button
                    key={agentName}
                    onClick={() => setActiveTab(index)}
                    initial={false}
                    animate={{
                      scale: isCurrent && status === 'running' ? [1, 1.02, 1] : 1,
                    }}
                    transition={{
                      duration: 1,
                      repeat: isCurrent && status === 'running' ? Infinity : 0,
                      ease: "easeInOut"
                    }}
                    className={clsx(
                      'flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-200 flex-shrink-0 relative',
                      activeTab === index
                        ? 'border-indigo-500 text-indigo-600 bg-indigo-50'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50',
                      status === 'running' && isCurrent && 'bg-blue-50 border-blue-300',
                      status === 'completed' && 'bg-green-50',
                      status === 'error' && 'bg-red-50'
                    )}
                  >
                    {/* Animated indicator for running agents */}
                    {status === 'running' && isCurrent && (
                      <motion.div
                        className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500"
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 1, repeat: Infinity }}
                      />
                    )}
                    
                    {getStatusIcon(status)}
                    {getAgentIcon(agentName)}
                    <span className="whitespace-nowrap">{agentName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                    
                    <span className="text-xs text-gray-400">({index + 1}/{selectedAgents.length})</span>
                  </motion.button>
                )
              })}
            </div>

            {/* Next Arrow */}
            <button
              onClick={goToNextTab}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors flex-shrink-0"
              disabled={selectedAgents.length <= 1}
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Content - Scrollable, with padding bottom for footer */}
        <div className="flex-1 overflow-y-auto min-h-0 pb-24">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="min-h-full"
            >
              {selectedAgents[activeTab] && renderAgentResult(selectedAgents[activeTab])}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Footer - Always visible at bottom, fixed */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50 shadow-lg z-20">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            {/* Close Button - Left Side */}
            <button
              onClick={onClose}
              className="px-6 py-2.5 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors flex items-center gap-2 flex-shrink-0"
            >
              <XCircle className="w-4 h-4" />
              <span>Close</span>
            </button>
            
            {/* Status and View Full Results Button - Right Side */}
            <div className="flex items-center gap-4 flex-shrink-0 min-w-0">
              {/* Status Indicator */}
              <div className="text-sm text-gray-600 hidden sm:flex items-center gap-2">
                {isAnalyzing ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin text-blue-500" />
                    <span>Analysis in progress...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Analysis completed</span>
                  </>
                )}
              </div>
              
              {/* View Full Report Button - Right Side, enabled when report is ready */}
              <motion.button
                whileHover={analysisProgress?.finalReport ? { scale: 1.02 } : {}}
                whileTap={analysisProgress?.finalReport ? { scale: 0.98 } : {}}
                onClick={() => {
                  if (!analysisProgress?.finalReport) return
                  
                  // Convert completedAgents array to agent_results object
                  const agentResultsObj = {}
                  const seenAgents = new Set() // Track seen agents to prevent duplicates
                  
                  if (analysisProgress.completedAgents && Array.isArray(analysisProgress.completedAgents)) {
                    analysisProgress.completedAgents.forEach(agentResult => {
                      if (agentResult.agent_name && !seenAgents.has(agentResult.agent_name)) {
                        seenAgents.add(agentResult.agent_name)
                        
                        // Determine if agent succeeded
                        const isSuccess = agentResult.success !== false && 
                                         (!agentResult.execution_result || agentResult.execution_result.success !== false)
                        
                        agentResultsObj[agentResult.agent_name] = {
                          ...agentResult,
                          // Ensure proper structure for AnalysisResults page
                          execution_result: agentResult.execution_result || {
                            success: isSuccess,
                            error: agentResult.error || (isSuccess ? null : 'Agent execution failed'),
                            output: agentResult.execution_result?.output || '',
                            output_files: agentResult.execution_result?.output_files || []
                          },
                          // Ensure success flag is set correctly
                          success: isSuccess
                        }
                        
                        // If there's an error but no execution_result.error, set it
                        if (!isSuccess && !agentResult.execution_result?.error && agentResult.error) {
                          agentResultsObj[agentResult.agent_name].execution_result.error = agentResult.error
                        }
                      }
                    })
                  }
                  
                  // Also check if finalReport contains agent_results
                  if (analysisProgress.finalReport?.agent_results && 
                      Object.keys(analysisProgress.finalReport.agent_results).length > 0) {
                    // Merge with finalReport's agent_results (prefer finalReport's data)
                    Object.keys(analysisProgress.finalReport.agent_results).forEach(agentName => {
                      if (!seenAgents.has(agentName)) {
                        agentResultsObj[agentName] = analysisProgress.finalReport.agent_results[agentName]
                        seenAgents.add(agentName)
                      }
                    })
                  }
                  
                  // Remove duplicates from selected_agents array
                  const uniqueSelectedAgents = [...new Set(selectedAgents || analysisProgress.finalReport?.agents_executed || [])]
                  
                  // Prepare the data structure for the results page
                  const wrapped = {
                    report: analysisProgress.finalReport,
                    selected_agents: uniqueSelectedAgents,
                    agent_results: agentResultsObj,
                    success: analysisProgress.success ?? true,
                    timestamp: analysisProgress.finalReport?.timestamp || new Date().toISOString(),
                    data_sample: analysisProgress.dataSample || analysisProgress.finalReport?.data_overview || {}
                  }
                  
                  // Close the modal first
                  onClose()
                  
                  // Small delay to ensure modal closes before navigation
                  setTimeout(() => {
                    // Derive user question from multiple possible sources
                    const derivedUserQuestion = (
                      analysisProgress?.userQuestion ||
                      analysisProgress?.finalReport?.user_question ||
                      analysisProgress?.finalReport?.question ||
                      null
                    )
                    const questionForState = derivedUserQuestion || 'Analysis Question'
                    
                    if (navigate) {
                      navigate('/analysis-results', {
                        state: {
                          analysisResult: wrapped,
                          userQuestion: questionForState
                        }
                      })
                    } else {
                      sessionStorage.setItem('analysisResult', JSON.stringify(wrapped))
                      sessionStorage.setItem('userQuestion', questionForState)
                      window.location.href = '/analysis-results'
                    }
                  }, 100)
                }}
                disabled={!analysisProgress?.finalReport}
                className={`px-6 py-2.5 rounded-lg font-semibold transition-all duration-200 flex items-center gap-2 relative overflow-hidden flex-shrink-0 ${
                  analysisProgress?.finalReport
                    ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700 shadow-lg hover:shadow-xl cursor-pointer'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed opacity-60'
                }`}
                title={analysisProgress?.finalReport ? 'View the complete analysis report' : 'Report is being generated...'}
              >
                {analysisProgress?.finalReport && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-green-400 via-emerald-500 to-teal-500"
                    animate={{
                      backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                    style={{
                      backgroundSize: '200% 200%'
                    }}
                  />
                )}
                
                {/* Content */}
                <div className="relative z-10 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  {analysisProgress?.finalReport ? (
                    <>
                      <span className="hidden sm:inline">View Full Report</span>
                      <span className="sm:hidden">View Report</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  ) : (
                    <>
                      <span className="hidden sm:inline">Report Not Ready</span>
                      <span className="sm:hidden">Not Ready</span>
                    </>
                  )}
                </div>
              </motion.button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default AgentResultsTabs
