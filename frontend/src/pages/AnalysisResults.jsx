import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, useLocation } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import AgentDetailsModal from '../components/AgentDetailsModal'
import { 
  ArrowLeft,
  Brain,
  CheckCircle,
  TrendingUp,
  BarChart3,
  Users,
  LineChart,
  Activity,
  PieChart,
  Sparkles,
  Download,
  Eye,
  Clock,
  FileText,
  AlertCircle
} from 'lucide-react'

export default function AnalysisResults() {
  const navigate = useNavigate()
  const location = useLocation()
  
  // Get analysis results from navigation state or sessionStorage (fallback)
  const { analysisResult, userQuestion } = location.state || {}
  
  // Fallback: try to get data from sessionStorage if not in location.state
  const fallbackAnalysisResult = analysisResult || (() => {
    try {
      const stored = sessionStorage.getItem('analysisResult')
      return stored ? JSON.parse(stored) : null
    } catch (e) {
      return null
    }
  })()
  
  const fallbackUserQuestion = userQuestion || (() => {
    try {
      return sessionStorage.getItem('userQuestion') || 'Analysis Question'
    } catch (e) {
      return 'Analysis Question'
    }
  })()
  
  // Use fallback values if primary values are not available
  const finalAnalysisResult = analysisResult || fallbackAnalysisResult
  const finalUserQuestion = userQuestion || fallbackUserQuestion
  
  // Debug logging
  console.log('AnalysisResults - analysisResult:', finalAnalysisResult)
  console.log('AnalysisResults - userQuestion:', finalUserQuestion)
  console.log('AnalysisResults - location.state:', location.state)
  
  // Add safety checks and fallbacks
  const safeAnalysisResult = finalAnalysisResult || {}
  const safeUserQuestion = finalUserQuestion || 'Analysis Question'

  // Modal state for agent details
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleAgentClick = (agentName) => {
    const agentResult = Object.values(finalAnalysisResult.agent_results || {}).find(
      r => r.agent_name === agentName
    )
    if (agentResult) {
      setSelectedAgent({ name: agentName, result: agentResult })
      setIsModalOpen(true)
    }
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setSelectedAgent(null)
  }
  
  // Agent icons mapping
  const agentIcons = {
    // Core Data Operations
    'data_quality_audit': CheckCircle,
    'exploratory_data_analysis': BarChart3,
    'data_cleaning': Sparkles,
    'data_visualization': BarChart3,
    
    // Customer & Marketing Analytics
    'churn_prediction': TrendingUp,
    'customer_segmentation': Users,
    'cohort_analysis': Users,
    'marketing_roi_analysis': TrendingUp,
    'customer_acquisition_cost_analysis': TrendingUp,
    
    // Sales & Revenue Analytics
    'sales_performance_analysis': LineChart,
    
    // Financial Analytics
    'profitability_analysis': LineChart,
    'cash_flow_analysis': LineChart,
    
    // Small Business Focused Analytics
    'employee_performance_analysis': Users,
    'competitive_analysis': BarChart3,
    'seasonal_business_planning': Activity,
    'operational_bottleneck_detection': AlertCircle,
    
    // Risk & Fraud Analytics
    'anomaly_detection': AlertCircle,
    
    // Advanced Analytics
    'predictive_modeling': Brain,
    'ab_testing_analysis': Activity,
    
    // Legacy agents (backwards compatibility)
    'churn_analysis': TrendingUp,
    'regression_analysis': LineChart,
    'statistical_analysis': Activity,
    'time_series_analysis': PieChart
  }

  // If no analysis results, redirect back
  if (!finalAnalysisResult || !finalUserQuestion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="w-20 h-20 bg-gradient-to-r from-red-400 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <AlertCircle className="w-10 h-10 text-white" />
          </motion.div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">No Analysis Results</h2>
          <p className="text-gray-600 mb-6">Please start an analysis first.</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all duration-200"
          >
            Go to Upload
          </motion.button>
        </div>
      </div>
    )
  }

  // Check if analysis results are empty or invalid
  // Consider it valid if either agent_results exist OR a report exists
  const hasValidResults = (finalAnalysisResult.agent_results && Object.keys(finalAnalysisResult.agent_results).length > 0) || 
                          (finalAnalysisResult.report && finalAnalysisResult.report.content)
  const hasVisualizations = finalAnalysisResult.agent_results && Object.keys(finalAnalysisResult.agent_results).length > 0 && 
                            Object.values(finalAnalysisResult.agent_results || {}).some(result => 
    result.execution_result?.output_files?.length > 0
  )

  console.log('AnalysisResults - hasValidResults:', hasValidResults)
  console.log('AnalysisResults - hasVisualizations:', hasVisualizations)
  console.log('AnalysisResults - agent_results:', finalAnalysisResult.agent_results)

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50/30 to-purple-50/50">
      {/* Navigation - Enhanced */}
      <nav className="relative z-10 px-6 py-4 border-b border-gray-200/50 bg-white/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3"
          >
            <motion.button
              whileHover={{ scale: 1.05, x: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/')}
              className="p-2.5 text-gray-600 hover:bg-gradient-to-r hover:from-indigo-100 hover:to-purple-100 rounded-xl transition-all duration-200 group"
            >
              <ArrowLeft className="w-5 h-5 group-hover:text-indigo-600 transition-colors" />
            </motion.button>
            
            <div className="w-10 h-10 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Banta
            </span>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full text-white text-sm font-bold shadow-lg shadow-emerald-200"
          >
            <CheckCircle className="w-5 h-5" />
            <span>Analysis Complete</span>
          </motion.div>
        </div>
      </nav>

      <div className="px-6 pt-8 pb-12">
        <div className="max-w-7xl mx-auto">
          
          {/* Combined Header and Agents Section - Premium Version */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-6xl mx-auto mb-8"
          >
            <div className="bg-white rounded-3xl border border-gray-200/60 shadow-2xl overflow-hidden backdrop-blur-sm">
              
              {/* Header Section */}
              <div className="relative px-6 py-4 bg-white border-b border-gray-200/60">
                <div className="relative flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {/* Success Icon */}
                  <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                      className="flex-shrink-0"
                    >
                      <div className="relative w-12 h-12 bg-emerald-500 rounded-xl flex items-center justify-center shadow-sm">
                        <CheckCircle className="w-6 h-6 text-white" />
                      </div>
                  </motion.div>
                    
                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <h1 className="text-xl font-bold text-gray-900 mb-0.5">
                        Analysis Complete
                      </h1>
                      <p className="text-gray-600 text-sm">
                        Your data has been successfully analyzed by AI-powered agents
                      </p>
                    </div>
                  </div>
                  
                  {/* Metadata */}
                  <div className="hidden lg:flex items-center gap-2">
                    {finalAnalysisResult.timestamp && (
                      <motion.div 
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-200"
                      >
                        <Clock className="w-3.5 h-3.5 text-gray-500" />
                        <span className="text-xs font-medium text-gray-600">{new Date(finalAnalysisResult.timestamp).toLocaleDateString()}</span>
          </motion.div>
                    )}
                    {finalAnalysisResult.selected_agents?.length > 0 && (
          <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-200"
                      >
                        <Brain className="w-3.5 h-3.5 text-gray-500" />
                        <span className="text-xs font-medium text-gray-600">{finalAnalysisResult.selected_agents.length} agents</span>
                      </motion.div>
                    )}
                </div>
                </div>
              </div>

              {/* User Question */}
              {finalUserQuestion && (
                <div className="px-6 py-4 bg-gray-50/50 border-b border-gray-200/60">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Brain className="w-4 h-4 text-gray-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                        Analysis Question
                      </p>
                      <p className="text-gray-900 text-sm leading-relaxed">
                        {finalUserQuestion}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Agents Section */}
              {finalAnalysisResult.selected_agents && (
                <div className="px-6 py-5 bg-white">
                  <div className="mb-4">
                    <div className="flex items-center gap-3 mb-1">
                      <div className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center">
                        <Brain className="w-4 h-4 text-gray-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">Selected Analysis Agents</h3>
                        <p className="text-xs text-gray-600 mt-0.5">AI-selected agents based on your data and question</p>
                      </div>
                    </div>
                  </div>
                
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {finalAnalysisResult.selected_agents.map((agentName, index) => {
                      const IconComponent = agentIcons[agentName] || Brain
                      const agentResult = Object.values(finalAnalysisResult.agent_results || {}).find(r => r.agent_name === agentName)
                      const isSuccess = agentResult?.execution_result?.success
                      const hasResults = !!agentResult
                      
                      return (
                        <motion.button
                          key={agentName}
                          initial={{ opacity: 0, scale: 0.95, y: 10 }}
                          animate={{ opacity: 1, scale: 1, y: 0 }}
                          transition={{ delay: 0.3 + index * 0.04, type: "spring", stiffness: 200 }}
                          whileHover={{ scale: 1.02, y: -2 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => hasResults && handleAgentClick(agentName)}
                          disabled={!hasResults}
                          className={`group relative p-3 rounded-lg border transition-all duration-200 text-left w-full ${
                            hasResults
                              ? 'cursor-pointer'
                              : 'cursor-not-allowed opacity-40'
                          } ${
                            isSuccess 
                              ? 'border-green-200 bg-green-50/50 hover:border-green-300 hover:bg-green-50' 
                              : hasResults
                              ? 'border-red-200 bg-red-50/50 hover:border-red-300 hover:bg-red-50'
                              : 'border-gray-200 bg-gray-50/50'
                          }`}
                        >
                          <div className="relative flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-200 ${
                              isSuccess
                                ? 'bg-green-500 text-white'
                                : hasResults
                                ? 'bg-red-500 text-white'
                                : 'bg-gray-400 text-white'
                            }`}>
                              <IconComponent className="w-5 h-5" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="font-semibold text-gray-900 capitalize mb-1 text-sm leading-tight truncate">
                                {agentName.replace(/_/g, ' ')}
                              </h4>
                              <div className="flex items-center gap-1.5">
                                {isSuccess ? (
                                  <>
                                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                    <p className="text-xs text-green-700 font-medium">Completed</p>
                                  </>
                                ) : hasResults ? (
                                  <>
                                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                                    <p className="text-xs text-red-700 font-medium">Failed</p>
                                  </>
                                ) : (
                                  <>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                                    <p className="text-xs text-gray-500 font-medium">Pending</p>
                                  </>
                                )}
                              </div>
                            </div>
                            {hasResults && (
                              <div className="flex-shrink-0">
                                <div className="w-8 h-8 rounded-lg bg-gray-200 hover:bg-gray-300 flex items-center justify-center transition-colors">
                                  <Eye className="w-4 h-4 text-gray-700" />
                                </div>
                              </div>
                            )}
                          </div>
                        </motion.button>
                      )
                    })}
                  </div>
                </div>
              )}
              </div>
            </motion.div>

          {/* Agent Details Modal */}
          <AgentDetailsModal
            isOpen={isModalOpen}
            onClose={closeModal}
            agentResult={selectedAgent?.result}
            agentName={selectedAgent?.name}
            agentIcons={agentIcons}
          />

          {/* Empty Results Message */}
          {!hasValidResults && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="max-w-4xl mx-auto mb-8"
            >
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-xl overflow-hidden">
                <div className="p-8 text-center">
                  <AlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">Analysis Completed</h3>
                  <p className="text-gray-600 mb-6">
                    The analysis has finished, but no results were generated. This might be due to:
                  </p>
                  <ul className="text-left text-gray-600 space-y-2 max-w-md mx-auto mb-6">
                    <li>• Data format issues</li>
                    <li>• Agent execution errors</li>
                    <li>• Insufficient data for analysis</li>
                    <li>• Backend processing issues</li>
                  </ul>
                  <div className="flex gap-4 justify-center">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => navigate('/')}
                      className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all duration-200"
                    >
                      Try Again
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Visualizations Gallery */}
          {finalAnalysisResult.agent_results && (
            (() => {
              // Collect all visualizations from all agents
              const allVisualizations = Object.values(finalAnalysisResult.agent_results || {})
                .filter(result => result.execution_result?.success && result.execution_result?.output_files)
                .flatMap(result => 
                  result.execution_result.output_files
                    .filter(file => ['png', 'jpg', 'jpeg', 'svg'].includes(file.type))
                    .map(file => ({
                      ...file,
                      agentName: result.agent_info?.display_name || result.agent_name.replace(/_/g, ' '),
                      agentInsights: result.code_result?.insights || ''
                    }))
                )

              return allVisualizations.length > 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="max-w-6xl mx-auto mb-8"
                >
              <div className="bg-white rounded-3xl border border-gray-200/60 shadow-xl overflow-hidden">
                <div className="p-4 bg-gradient-to-r from-purple-600 via-pink-600 to-rose-600">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/30">
                          <BarChart3 className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h3 className="text-2xl font-bold text-white">Data Visualizations</h3>
                          <p className="text-white/90 text-xs">AI-generated charts and analysis insights</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-8">
                      <div className="grid gap-8">
                        {allVisualizations.map((viz, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.6 + index * 0.1 }}
                            className="bg-gradient-to-br from-white to-gray-50 rounded-2xl border-2 border-gray-200 shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
                          >
                            {/* Chart Header */}
                            <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-gray-200">
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-3 mb-2">
                                    <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-md">
                                      <BarChart3 className="w-5 h-5 text-white" />
                                    </div>
                              <div>
                                      <h4 className="text-xl font-bold text-gray-900 capitalize">
                                  {viz.agentName}
                                </h4>
                                <p className="text-sm text-gray-600">{viz.filename}</p>
                              </div>
                                  </div>
                                </div>
                                <motion.button
                                  whileHover={{ scale: 1.05 }}
                                  whileTap={{ scale: 0.95 }}
                                onClick={() => {
                                  const link = document.createElement('a')
                                  link.href = `data:image/${viz.type};base64,${viz.content}`
                                  link.download = viz.filename
                                  link.click()
                                }}
                                  className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all font-semibold shadow-lg"
                              >
                                <Download className="w-4 h-4" />
                                  <span>Download</span>
                                </motion.button>
                              </div>
                            </div>

                            {/* Chart Image */}
                            <div className="p-6 bg-white">
                              <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-6 border-2 border-gray-100 shadow-inner">
                              <img
                                src={`data:image/${viz.type};base64,${viz.content}`}
                                alt={viz.filename}
                                  className="w-full max-w-full mx-auto rounded-lg shadow-lg"
                                  style={{ maxHeight: '600px', objectFit: 'contain' }}
                              />
                              </div>
                            </div>

                            {/* Chart Explanation */}
                            {viz.agentInsights && (
                              <div className="p-6 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-t border-gray-200">
                                <div className="flex items-center gap-3 mb-4">
                                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                                    <Eye className="w-5 h-5 text-white" />
                                  </div>
                                  <h5 className="text-lg font-bold text-gray-900">Chart Insights & Explanation</h5>
                                </div>
                                <div className="bg-white/80 backdrop-blur-sm rounded-xl p-5 border border-blue-200/50 shadow-sm">
                                  <div className="text-gray-800 prose prose-sm max-w-none">
                                  <ReactMarkdown
                                    components={{
                                        p: ({children}) => <p className="text-gray-800 mb-3 leading-relaxed text-base">{children}</p>,
                                        ul: ({children}) => <ul className="list-disc list-inside text-gray-800 mb-3 space-y-2 ml-4">{children}</ul>,
                                        li: ({children}) => <li className="text-gray-800 text-base leading-relaxed">{children}</li>,
                                        strong: ({children}) => <strong className="font-bold text-gray-900">{children}</strong>
                                    }}
                                  >
                                    {viz.agentInsights}
                                  </ReactMarkdown>
                                  </div>
                                </div>
                              </div>
                            )}
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : null
            })()
          )}


          {/* Final Report - Premium Version */}
          {finalAnalysisResult.report && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="max-w-6xl mx-auto mb-8"
            >
              <div className="bg-white rounded-3xl border border-gray-200/60 shadow-2xl overflow-hidden backdrop-blur-sm">
                <div className="px-6 py-4 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 border-b border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center border border-white/30">
                      <FileText className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">Executive Report</h3>
                      <p className="text-white/90 text-xs">AI-generated comprehensive analysis summary</p>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 sm:p-8 bg-white">
                  <div className="prose prose-lg max-w-none text-gray-800 leading-relaxed">
                    <ReactMarkdown
                      components={{
                        h1: ({children}) => <h1 className="text-3xl font-bold text-gray-900 mb-6 mt-8 pb-3 border-b-2 border-indigo-200">{children}</h1>,
                        h2: ({children}) => <h2 className="text-2xl font-bold text-gray-800 mb-4 mt-8 pb-2 border-b border-gray-200">{children}</h2>,
                        h3: ({children}) => <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-6">{children}</h3>,
                        p: ({children}) => <p className="text-gray-700 mb-5 leading-relaxed text-lg">{children}</p>,
                        ul: ({children}) => <ul className="list-disc list-inside text-gray-700 mb-5 space-y-2 text-lg ml-4">{children}</ul>,
                        ol: ({children}) => <ol className="list-decimal list-inside text-gray-700 mb-5 space-y-2 text-lg ml-4">{children}</ol>,
                        li: ({children}) => <li className="text-gray-700 leading-relaxed">{children}</li>,
                        code: ({children}) => <code className="bg-indigo-100 text-indigo-800 px-2.5 py-1 rounded-lg text-sm font-mono border border-indigo-200">{children}</code>,
                        pre: ({children}) => <pre className="bg-gray-900 text-green-400 p-5 rounded-xl overflow-x-auto text-sm font-mono mb-6 border border-gray-700 shadow-lg">{children}</pre>,
                        blockquote: ({children}) => <blockquote className="border-l-4 border-indigo-500 pl-6 italic text-gray-700 mb-6 bg-indigo-50/50 py-3 rounded-r-lg">{children}</blockquote>,
                        strong: ({children}) => <strong className="font-bold text-gray-900">{children}</strong>,
                        em: ({children}) => <em className="italic text-gray-700">{children}</em>
                      }}
                    >
                      {finalAnalysisResult.report.content}
                    </ReactMarkdown>
                  </div>
                  
                  {finalAnalysisResult.report.summary && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-6 p-5 bg-gray-50 rounded-lg border border-gray-200"
                    >
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-8 h-8 bg-gray-700 rounded-lg flex items-center justify-center">
                          <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <h4 className="text-lg font-bold text-gray-900">Key Takeaways</h4>
                      </div>
                      {Array.isArray(finalAnalysisResult.report.summary) ? (
                        <ul className="list-disc list-inside text-gray-700 space-y-2 text-sm ml-2">
                          {finalAnalysisResult.report.summary.map((item, index) => (
                            <li key={index} className="leading-relaxed">
                              {item}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-700 text-sm leading-relaxed">{finalAnalysisResult.report.summary}</p>
                      )}
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            className="max-w-4xl mx-auto text-center"
          >
            <div className="flex gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/')}
                className="px-8 py-4 bg-white text-gray-700 border-2 border-gray-200 rounded-xl font-semibold hover:border-gray-300 transition-all duration-200 flex items-center gap-3"
              >
                <ArrowLeft className="w-5 h-5" />
                New Analysis
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  // Download functionality could be added here
                  console.log('Download results')
                }}
                className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 flex items-center gap-3"
              >
                <Download className="w-5 h-5" />
                Download Results
              </motion.button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
