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
import WorkflowVisualization from './WorkflowVisualization'

// Agent descriptions mapping (defined as a constant to avoid hoisting issues)
const AGENT_DESCRIPTIONS = {
  'data_quality_audit': 'Analyzing data quality',
  'exploratory_data_analysis': 'Initial data exploration',
  'data_visualization': 'Creating charts and graphs',
  'statistical_analysis': 'Statistical computations',
  'churn_prediction': 'Predicting customer churn',
  'customer_segmentation': 'Segmenting customers',
  'sales_performance_analysis': 'Analyzing sales performance',
  'marketing_roi_analysis': 'Marketing ROI analysis',
  'time_series_analysis': 'Time series forecasting',
  'anomaly_detection': 'Detecting anomalies',
  'predictive_modeling': 'Building predictive models',
  'cohort_analysis': 'Cohort analysis',
  'profitability_analysis': 'Profitability analysis',
  'cash_flow_analysis': 'Cash flow analysis',
  'employee_performance_analysis': 'Employee performance analysis',
  'competitive_analysis': 'Competitive analysis',
  'seasonal_business_planning': 'Seasonal planning',
  'operational_bottleneck_detection': 'Detecting bottlenecks',
  'customer_acquisition_cost_analysis': 'CAC analysis',
  'ab_testing_analysis': 'A/B testing analysis'
}

// Helper function to get agent descriptions (function declaration for proper hoisting)
function getAgentDescription(agentName) {
  return AGENT_DESCRIPTIONS[agentName] || 'AI analysis agent'
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

  // Update agent statuses based on analysis progress (LangGraph enhanced)
  useEffect(() => {
    if (analysisProgress) {
      setAgentStatuses(prev => {
        const updated = { ...prev }
        
        // Update based on analysis progress - handle currentAgent properly
        if (analysisProgress.currentAgent) {
          const currentAgentName = analysisProgress.currentAgent
          if (updated[currentAgentName]) {
            updated[currentAgentName] = {
              ...updated[currentAgentName],
              status: 'running',
              progress: analysisProgress.progress || 0,
              startTime: analysisProgress.startTime || new Date().toISOString()
            }
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

  const renderAgentResult = (agentName) => {
    const status = agentStatuses[agentName]?.status || 'pending'
    const result = agentStatuses[agentName]?.result
    const error = agentStatuses[agentName]?.error

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
      const progress = agentStatuses[agentName]?.progress || 0
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-center max-w-md">
            <Loader className="w-12 h-12 mx-auto mb-4 text-blue-500 animate-spin" />
            <p className="text-lg font-medium text-blue-700 mb-2">Analyzing...</p>
            <p className="text-sm text-gray-600 mb-4">{(() => {
              try {
                return getAgentDescription(agentName) || 'AI analysis agent'
              } catch (error) {
                console.error('Error getting agent description:', error)
                return 'AI analysis agent'
              }
            })()}</p>
            
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
        <div className="p-6 space-y-4">
          {/* Agent Summary */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="font-semibold text-green-800">Analysis Complete</span>
            </div>
            <p className="text-sm text-green-700">{(() => {
              try {
                return getAgentDescription(agentName) || 'AI analysis agent'
              } catch (error) {
                console.error('Error getting agent description:', error)
                return 'AI analysis agent'
              }
            })()}</p>
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="w-full max-w-6xl max-h-[90vh] bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col"
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
                <p className="text-sm text-gray-600 truncate">
                  {isAnalyzing ? 'Analysis in progress...' : 'Analysis completed'}
                </p>
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

        {/* Workflow Visualization */}
        {analysisProgress && (
          <div className="border-b border-gray-200">
            <WorkflowVisualization 
              analysisProgress={analysisProgress}
              selectedAgents={selectedAgents}
              className="m-4"
            />
          </div>
        )}

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
              {selectedAgents.map((agentName, index) => {
                const status = agentStatuses[agentName]?.status || 'pending'
                return (
                  <button
                    key={agentName}
                    onClick={() => setActiveTab(index)}
                    className={clsx(
                      'flex items-center gap-2 px-6 py-4 text-sm font-medium whitespace-nowrap border-b-2 transition-colors',
                      activeTab === index
                        ? 'border-indigo-500 text-indigo-600 bg-indigo-50'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    )}
                  >
                    {getStatusIcon(status)}
                    {getAgentIcon(agentName)}
                    <span>{agentName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
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
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
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
            
            <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
              {/* Show results button if analysis is complete */}
              {!isAnalyzing && analysisProgress?.finalReport && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    // Navigate to results page with the final report
                    if (navigate) {
                      navigate('/analysis-results', {
                        state: {
                          analysisResult: analysisProgress.finalReport,
                          userQuestion: analysisProgress.userQuestion || 'Analysis Question'
                        }
                      })
                    } else {
                      // Fallback: store data in sessionStorage and navigate
                      sessionStorage.setItem('analysisResult', JSON.stringify(analysisProgress.finalReport))
                      sessionStorage.setItem('userQuestion', analysisProgress.userQuestion || 'Analysis Question')
                      window.location.href = '/analysis-results'
                    }
                  }}
                  className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center gap-2 relative overflow-hidden text-sm"
                >
                  {/* Animated background gradient */}
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
                  
                  {/* Content */}
                  <div className="relative z-10 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    <span className="hidden sm:inline">View Full Results</span>
                    <span className="sm:hidden">View Results</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </motion.button>
              )}
              
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-colors text-sm"
              >
                {isAnalyzing ? 'Close' : 'Close'}
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default AgentResultsTabs
