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
  ChevronRight
} from 'lucide-react'
import { clsx } from 'clsx'

const AgentResultsTabs = ({ 
  selectedAgents, 
  analysisProgress, 
  onClose,
  isAnalyzing 
}) => {
  const [activeTab, setActiveTab] = useState(0)
  const [agentStatuses, setAgentStatuses] = useState({})

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
    selectedAgents.forEach((agent, index) => {
      initialStatuses[agent.name] = {
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

  // Update agent statuses based on analysis progress
  useEffect(() => {
    if (analysisProgress) {
      setAgentStatuses(prev => {
        const updated = { ...prev }
        
        // Update based on analysis progress
        if (analysisProgress.currentAgent) {
          updated[analysisProgress.currentAgent] = {
            ...updated[analysisProgress.currentAgent],
            status: 'running',
            progress: analysisProgress.progress || 0,
            startTime: analysisProgress.startTime
          }
        }

        // Update completed agents
        if (analysisProgress.completedAgents) {
          analysisProgress.completedAgents.forEach(agentResult => {
            if (agentResult.agent_name) {
              updated[agentResult.agent_name] = {
                ...updated[agentResult.agent_name],
                status: agentResult.success !== false ? 'completed' : 'error',
                progress: 100,
                result: agentResult,
                error: agentResult.error || null,
                endTime: new Date().toISOString()
              }
            }
          })
        }

        return updated
      })
    }
  }, [analysisProgress])

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

  const renderAgentResult = (agent) => {
    const status = agentStatuses[agent.name]?.status || 'pending'
    const result = agentStatuses[agent.name]?.result
    const error = agentStatuses[agent.name]?.error

    if (status === 'pending') {
      return (
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">Waiting to start...</p>
            <p className="text-sm">This agent will begin analysis shortly</p>
          </div>
        </div>
      )
    }

    if (status === 'running') {
      const progress = agentStatuses[agent.name]?.progress || 0
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-center max-w-md">
            <Loader className="w-12 h-12 mx-auto mb-4 text-blue-500 animate-spin" />
            <p className="text-lg font-medium text-blue-700 mb-2">Analyzing...</p>
            <p className="text-sm text-gray-600 mb-4">{agent.description}</p>
            
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <motion.div
                className="bg-blue-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <p className="text-xs text-gray-500">{progress}% complete</p>
          </div>
        </div>
      )
    }

    if (status === 'error') {
      const errorMessage = agentStatuses[agent.name]?.error || 'An error occurred during analysis'
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
        <div className="p-6 space-y-4">
          {/* Agent Summary */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="font-semibold text-green-800">Analysis Complete</span>
            </div>
            <p className="text-sm text-green-700">{agent.description}</p>
          </div>

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
        </div>
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="w-full max-w-6xl h-5/6 bg-white rounded-2xl shadow-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Agent Analysis Progress</h2>
                <p className="text-sm text-gray-600">
                  {isAnalyzing ? 'Analysis in progress...' : 'Analysis completed'}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 bg-white">
          <div className="flex items-center">
            {/* Previous Arrow */}
            <button
              onClick={goToPreviousTab}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={selectedAgents.length <= 1}
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            {/* Tab List */}
            <div className="flex overflow-x-auto flex-1">
              {selectedAgents.map((agent, index) => {
                const status = agentStatuses[agent.name]?.status || 'pending'
                return (
                  <button
                    key={agent.name}
                    onClick={() => setActiveTab(index)}
                    className={clsx(
                      'flex items-center gap-2 px-6 py-4 text-sm font-medium whitespace-nowrap border-b-2 transition-colors',
                      activeTab === index
                        ? 'border-indigo-500 text-indigo-600 bg-indigo-50'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    )}
                  >
                    {getStatusIcon(status)}
                    {getAgentIcon(agent.name)}
                    <span>{agent.display_name || agent.name}</span>
                    <span className="text-xs text-gray-400">({index + 1}/{selectedAgents.length})</span>
                  </button>
                )
              })}
            </div>

            {/* Next Arrow */}
            <button
              onClick={goToNextTab}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={selectedAgents.length <= 1}
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="h-full overflow-y-auto"
            >
              {selectedAgents[activeTab] && renderAgentResult(selectedAgents[activeTab])}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {isAnalyzing ? (
                <span className="flex items-center gap-2">
                  <Loader className="w-4 h-4 animate-spin text-blue-500" />
                  Analysis in progress...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Analysis completed
                </span>
              )}
            </div>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-colors"
            >
              {isAnalyzing ? 'Close (Analysis Running)' : 'Close'}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default AgentResultsTabs
