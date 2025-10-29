import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, useLocation } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
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
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="relative z-10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-2"
          >
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/')}
              className="p-3 text-gray-600 hover:bg-white/50 rounded-xl transition-all duration-200 mr-2"
            >
              <ArrowLeft className="w-5 h-5" />
            </motion.button>
            
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
            className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-100 to-teal-100 rounded-full text-emerald-700 text-sm font-medium"
          >
            <CheckCircle className="w-4 h-4" />
            Analysis Complete
          </motion.div>
        </div>
      </nav>

      <div className="px-6 pt-8 pb-12">
        <div className="max-w-7xl mx-auto">
          
          {/* Success Header */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="max-w-4xl mx-auto mb-12"
          >
            <div className="bg-gradient-to-r from-green-400 via-emerald-500 to-teal-500 rounded-2xl shadow-2xl overflow-hidden">
              <div className="p-8 text-center">
                <div className="flex items-center justify-center gap-3 text-white mb-4">
                  <motion.div
                    animate={{ rotate: [0, 360] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  >
                    <CheckCircle className="w-12 h-12" />
                  </motion.div>
                  <div>
                    <h1 className="text-3xl font-bold">Analysis Complete!</h1>
                    <p className="text-emerald-50 text-lg">Banta has analyzed your data with AI-powered agents</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Your Question */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="max-w-4xl mx-auto mb-8"
          >
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-lg p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Your Question:</h3>
                  <p className="text-gray-700 text-lg italic">"{finalUserQuestion}"</p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Analysis Summary */}
          {finalAnalysisResult.success && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="max-w-6xl mx-auto mb-8"
            >
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-xl overflow-hidden">
                <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-indigo-50 to-purple-50">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Summary</h2>
                  <div className="flex items-center gap-6 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      Completed: {formatTimestamp(finalAnalysisResult.timestamp)}
                    </div>
                    <div className="flex items-center gap-2">
                      <Brain className="w-4 h-4" />
                      Agents: {finalAnalysisResult.selected_agents?.length || 0}
                    </div>
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Data: {finalAnalysisResult.data_sample?.total_rows?.toLocaleString()} rows
                    </div>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="grid md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-indigo-600 mb-2">
                        {finalAnalysisResult.selected_agents?.length || 0}
                      </div>
                      <p className="text-gray-600">AI Agents Used</p>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-600 mb-2">
                        {finalAnalysisResult.data_sample?.columns?.length || 0}
                      </div>
                      <p className="text-gray-600">Data Columns</p>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-pink-600 mb-2">
                        {Object.values(finalAnalysisResult.agent_results || {}).filter(r => r.execution_result?.success).length || 0}
                      </div>
                      <p className="text-gray-600">Successful Analyses</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Selected Agents */}
          {finalAnalysisResult.selected_agents && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="max-w-6xl mx-auto mb-8"
            >
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-xl overflow-hidden">
                <div className="p-6 border-b border-gray-100">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Agents Selected by AI</h3>
                  <p className="text-gray-600">Banta automatically chose these agents based on your data and question</p>
                </div>
                
                <div className="p-6">
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {finalAnalysisResult.selected_agents.map((agentName, index) => {
                      const IconComponent = agentIcons[agentName] || Brain
                      const agentResult = Object.values(finalAnalysisResult.agent_results || {}).find(r => r.agent_name === agentName)
                      const isSuccess = agentResult?.execution_result?.success
                      
                      return (
                        <motion.div
                          key={agentName}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.5 + index * 0.1 }}
                          className={`p-4 rounded-xl border-2 ${
                            isSuccess 
                              ? 'border-green-200 bg-green-50' 
                              : 'border-red-200 bg-red-50'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                              isSuccess
                                ? 'bg-green-500 text-white'
                                : 'bg-red-500 text-white'
                            }`}>
                              <IconComponent className="w-5 h-5" />
                            </div>
                            <div className="flex-1">
                              <h4 className="font-semibold text-gray-900 capitalize">
                                {agentName.replace(/_/g, ' ')}
                              </h4>
                              <p className={`text-sm ${
                                isSuccess ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {isSuccess ? 'Completed Successfully' : 'Analysis Failed'}
                              </p>
                            </div>
                          </div>
                        </motion.div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

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
                  <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-xl overflow-hidden">
                    <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-pink-50">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                          <BarChart3 className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h3 className="text-2xl font-bold text-gray-900">Data Visualizations</h3>
                          <p className="text-gray-600">AI-generated charts and analysis insights</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-6">
                      <div className="grid gap-8">
                        {allVisualizations.map((viz, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.6 + index * 0.1 }}
                            className="bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-200 p-6 shadow-sm"
                          >
                            {/* Chart Header */}
                            <div className="flex items-center justify-between mb-4">
                              <div>
                                <h4 className="text-lg font-semibold text-gray-900 capitalize mb-1">
                                  {viz.agentName}
                                </h4>
                                <p className="text-sm text-gray-600">{viz.filename}</p>
                              </div>
                              <button
                                onClick={() => {
                                  const link = document.createElement('a')
                                  link.href = `data:image/${viz.type};base64,${viz.content}`
                                  link.download = viz.filename
                                  link.click()
                                }}
                                className="flex items-center gap-2 px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors text-sm"
                              >
                                <Download className="w-4 h-4" />
                                Download
                              </button>
                            </div>

                            {/* Chart Image */}
                            <div className="bg-white rounded-lg p-4 border border-gray-100 mb-4">
                              <img
                                src={`data:image/${viz.type};base64,${viz.content}`}
                                alt={viz.filename}
                                className="w-full max-w-5xl mx-auto rounded-lg shadow-sm"
                                style={{ maxHeight: '500px', objectFit: 'contain' }}
                              />
                            </div>

                            {/* Chart Explanation */}
                            {viz.agentInsights && (
                              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                                <h5 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                                  <Eye className="w-4 h-4" />
                                  Chart Insights & Explanation
                                </h5>
                                <div className="text-blue-800 prose prose-blue max-w-none">
                                  <ReactMarkdown
                                    components={{
                                      p: ({children}) => <p className="text-blue-800 mb-2 leading-relaxed">{children}</p>,
                                      ul: ({children}) => <ul className="list-disc list-inside text-blue-800 mb-2 space-y-1">{children}</ul>,
                                      li: ({children}) => <li className="text-blue-800 text-sm">{children}</li>,
                                      strong: ({children}) => <strong className="font-semibold text-blue-900">{children}</strong>
                                    }}
                                  >
                                    {viz.agentInsights}
                                  </ReactMarkdown>
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

          {/* Analysis Results */}
          {finalAnalysisResult.agent_results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              className="max-w-6xl mx-auto mb-8"
            >
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-xl overflow-hidden">
                <div className="p-6 border-b border-gray-100">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Detailed Analysis Results</h3>
                  <p className="text-gray-600">Results from each AI agent's analysis</p>
                </div>
                
                <div className="p-6 space-y-6">
                  {Object.values(finalAnalysisResult.agent_results || {}).map((result, index) => {
                    const IconComponent = agentIcons[result.agent_name] || Brain
                    const isSuccess = result.execution_result?.success
                    
                    return (
                      <motion.div
                        key={result.agent_name}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.7 + index * 0.1 }}
                        className="border border-gray-200 rounded-xl overflow-hidden"
                      >
                        <div className={`p-4 ${
                          isSuccess ? 'bg-green-50' : 'bg-red-50'
                        }`}>
                          <div className="flex items-center gap-3">
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                              isSuccess
                                ? 'bg-green-500 text-white'
                                : 'bg-red-500 text-white'
                            }`}>
                              <IconComponent className="w-6 h-6" />
                            </div>
                            <div className="flex-1">
                              <h4 className="text-lg font-bold text-gray-900 capitalize">
                                {result.agent_info?.display_name || result.agent_name.replace(/_/g, ' ')}
                              </h4>
                              <p className="text-gray-600">
                                {result.agent_info?.description || 'AI Analysis Agent'}
                              </p>
                            </div>
                            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                              isSuccess 
                                ? 'bg-green-200 text-green-800'
                                : 'bg-red-200 text-red-800'
                            }`}>
                              {isSuccess ? 'Success' : 'Failed'}
                            </div>
                          </div>
                        </div>
                        
                        <div className="p-6">
                          {isSuccess ? (
                            <div className="space-y-4">
                              {result.code_result?.insights && (
                                <div>
                                  <h5 className="font-semibold text-gray-900 mb-2">Key Insights:</h5>
                                  <div className="text-gray-700 bg-gray-50 p-4 rounded-lg prose prose-gray max-w-none">
                                    <ReactMarkdown
                                      components={{
                                        h1: ({children}) => <h1 className="text-lg font-bold text-gray-900 mb-2">{children}</h1>,
                                        h2: ({children}) => <h2 className="text-base font-semibold text-gray-800 mb-2">{children}</h2>,
                                        h3: ({children}) => <h3 className="text-sm font-semibold text-gray-800 mb-1">{children}</h3>,
                                        p: ({children}) => <p className="text-gray-700 mb-2">{children}</p>,
                                        ul: ({children}) => <ul className="list-disc list-inside text-gray-700 mb-2 space-y-1">{children}</ul>,
                                        ol: ({children}) => <ol className="list-decimal list-inside text-gray-700 mb-2 space-y-1">{children}</ol>,
                                        li: ({children}) => <li className="text-gray-700 text-sm">{children}</li>,
                                        code: ({children}) => <code className="bg-gray-200 text-gray-800 px-1 py-0.5 rounded text-xs font-mono">{children}</code>,
                                        strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>
                                      }}
                                    >
                                      {result.code_result.insights}
                                    </ReactMarkdown>
                                  </div>
                                </div>
                              )}
                              
                              {result.execution_result?.output && (
                                <div>
                                  <h5 className="font-semibold text-gray-900 mb-2">Analysis Output:</h5>
                                  <pre className="text-sm text-gray-700 bg-gray-50 p-4 rounded-lg overflow-x-auto max-h-64 overflow-y-auto">
                                    {result.execution_result.output}
                                  </pre>
                                </div>
                              )}
                              
                              {result.execution_result?.output_files?.length > 0 && (
                                <div>
                                  <h5 className="font-semibold text-gray-900 mb-4">Generated Visualizations & Reports:</h5>
                                  
                                  {/* Display Images */}
                                  <div className="space-y-6 mb-6">
                                    {result.execution_result.output_files
                                      .filter(file => ['png', 'jpg', 'jpeg', 'svg'].includes(file.type))
                                      .map((file, fileIndex) => (
                                        <div key={fileIndex} className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                                          <div className="flex items-center gap-2 mb-3">
                                            <BarChart3 className="w-5 h-5 text-indigo-600" />
                                            <h6 className="font-medium text-gray-900">{file.filename}</h6>
                                            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                              {(file.size / 1024).toFixed(1)} KB
                                            </span>
                                          </div>
                                          
                                          {file.encoding === 'base64' && file.content && (
                                            <div className="relative group">
                                              <img
                                                src={`data:image/${file.type};base64,${file.content}`}
                                                alt={file.filename}
                                                className="w-full max-w-4xl mx-auto rounded-lg shadow-lg border border-gray-200 bg-white"
                                                style={{ maxHeight: '600px', objectFit: 'contain' }}
                                              />
                                              
                                              {/* Download overlay on hover */}
                                              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button
                                                  onClick={() => {
                                                    const link = document.createElement('a')
                                                    link.href = `data:image/${file.type};base64,${file.content}`
                                                    link.download = file.filename
                                                    link.click()
                                                  }}
                                                  className="bg-white/90 backdrop-blur-sm text-gray-700 p-2 rounded-lg shadow-lg hover:bg-white transition-colors"
                                                  title="Download chart"
                                                >
                                                  <Download className="w-4 h-4" />
                                                </button>
                                              </div>
                                            </div>
                                          )}
                                        </div>
                                      ))
                                    }
                                  </div>

                                  {/* Display Text Files */}
                                  <div className="space-y-4">
                                    {result.execution_result.output_files
                                      .filter(file => ['txt', 'md', 'csv'].includes(file.type))
                                      .map((file, fileIndex) => (
                                        <div key={fileIndex} className="bg-gray-50 rounded-lg border border-gray-200 p-4">
                                          <div className="flex items-center gap-2 mb-2">
                                            <FileText className="w-5 h-5 text-gray-600" />
                                            <h6 className="font-medium text-gray-900">{file.filename}</h6>
                                          </div>
                                          
                                          {file.encoding === 'utf-8' && file.content && (
                                            <div className="bg-white rounded p-3 text-sm text-gray-700 max-h-48 overflow-y-auto">
                                              <pre className="whitespace-pre-wrap font-mono text-xs">
                                                {file.content}
                                              </pre>
                                            </div>
                                          )}
                                        </div>
                                      ))
                                    }
                                  </div>

                                  {/* Other Files */}
                                  {result.execution_result.output_files
                                    .filter(file => !['png', 'jpg', 'jpeg', 'svg', 'txt', 'md', 'csv'].includes(file.type))
                                    .length > 0 && (
                                    <div className="mt-4">
                                      <h6 className="font-medium text-gray-900 mb-2">Other Files:</h6>
                                      <div className="flex flex-wrap gap-2">
                                        {result.execution_result.output_files
                                          .filter(file => !['png', 'jpg', 'jpeg', 'svg', 'txt', 'md', 'csv'].includes(file.type))
                                          .map((file, fileIndex) => (
                                            <span 
                                              key={fileIndex}
                                              className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm"
                                            >
                                              {file.filename}
                                            </span>
                                          ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          ) : (
                            <div className="text-red-600">
                              <p className="font-medium mb-2">Analysis Failed:</p>
                              <p className="text-sm bg-red-50 p-4 rounded-lg">
                                {result.error || result.execution_result?.error || 'Unknown error occurred'}
                              </p>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              </div>
            </motion.div>
          )}

          {/* Final Report */}
          {finalAnalysisResult.report && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="max-w-6xl mx-auto mb-8"
            >
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-xl overflow-hidden">
                <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-teal-50">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900">Executive Report</h3>
                      <p className="text-gray-600">AI-generated comprehensive analysis summary</p>
                    </div>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="prose prose-gray prose-lg max-w-none text-gray-800 leading-relaxed">
                    <ReactMarkdown
                      components={{
                        h1: ({children}) => <h1 className="text-3xl font-bold text-gray-900 mb-4">{children}</h1>,
                        h2: ({children}) => <h2 className="text-2xl font-semibold text-gray-800 mb-3 mt-6">{children}</h2>,
                        h3: ({children}) => <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">{children}</h3>,
                        p: ({children}) => <p className="text-gray-700 mb-4 leading-relaxed">{children}</p>,
                        ul: ({children}) => <ul className="list-disc list-inside text-gray-700 mb-4 space-y-2">{children}</ul>,
                        ol: ({children}) => <ol className="list-decimal list-inside text-gray-700 mb-4 space-y-2">{children}</ol>,
                        li: ({children}) => <li className="text-gray-700">{children}</li>,
                        code: ({children}) => <code className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm font-mono">{children}</code>,
                        pre: ({children}) => <pre className="bg-gray-100 text-gray-800 p-4 rounded-lg overflow-x-auto text-sm font-mono mb-4">{children}</pre>,
                        blockquote: ({children}) => <blockquote className="border-l-4 border-indigo-500 pl-4 italic text-gray-600 mb-4">{children}</blockquote>,
                        strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                        em: ({children}) => <em className="italic text-gray-700">{children}</em>
                      }}
                    >
                      {finalAnalysisResult.report.content}
                    </ReactMarkdown>
                  </div>
                  
                  {finalAnalysisResult.report.summary && (
                    <div className="mt-6 p-4 bg-emerald-50 rounded-xl border border-emerald-200">
                      <h4 className="font-semibold text-emerald-900 mb-2">Key Summary:</h4>
                      {Array.isArray(finalAnalysisResult.report.summary) ? (
                        <ul className="list-disc list-inside text-emerald-800 space-y-1">
                          {finalAnalysisResult.report.summary.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-emerald-800">{finalAnalysisResult.report.summary}</p>
                      )}
                    </div>
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
