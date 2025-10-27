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
  
  // Get analysis results from navigation state
  const { analysisResult, userQuestion } = location.state || {}
  
  // Add safety checks and fallbacks
  const safeAnalysisResult = analysisResult || {}
  const safeUserQuestion = userQuestion || 'Analysis Question'
  
  // Agent icons mapping
  const agentIcons = {
    // Core Data Operations
    'data_quality_audit': CheckCircle,
    'exploratory_data_analysis': BarChart3,
    'business_intelligence_dashboard': PieChart,
    'data_cleaning': Sparkles,
    'data_visualization': BarChart3,
    
    // Customer & Marketing Analytics
    'churn_prediction': TrendingUp,
    'customer_segmentation': Users,
    'cohort_analysis': Users,
    'marketing_roi_analysis': TrendingUp,
    
    // Sales & Revenue Analytics
    'sales_performance_analysis': LineChart,
    
    // Financial Analytics
    'profitability_analysis': LineChart,
    
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
  if (!analysisResult || !userQuestion) {
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
                  <p className="text-gray-700 text-lg italic">"{userQuestion}"</p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Analysis Summary */}
          {analysisResult.success && (
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
                      Completed: {formatTimestamp(analysisResult.timestamp)}
                    </div>
                    <div className="flex items-center gap-2">
                      <Brain className="w-4 h-4" />
                      Agents: {analysisResult.selected_agents?.length || 0}
                    </div>
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Data: {analysisResult.data_sample?.total_rows?.toLocaleString()} rows
                    </div>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="grid md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-indigo-600 mb-2">
                        {analysisResult.selected_agents?.length || 0}
                      </div>
                      <p className="text-gray-600">AI Agents Used</p>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-600 mb-2">
                        {analysisResult.data_sample?.columns?.length || 0}
                      </div>
                      <p className="text-gray-600">Data Columns</p>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-pink-600 mb-2">
                        {analysisResult.agent_results?.filter(r => r.execution_result?.success).length || 0}
                      </div>
                      <p className="text-gray-600">Successful Analyses</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Selected Agents */}
          {analysisResult.selected_agents && (
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
                    {analysisResult.selected_agents.map((agentName, index) => {
                      const IconComponent = agentIcons[agentName] || Brain
                      const agentResult = analysisResult.agent_results?.find(r => r.agent_name === agentName)
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

          {/* Analysis Results */}
          {analysisResult.agent_results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="max-w-6xl mx-auto mb-8"
            >
              <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-xl overflow-hidden">
                <div className="p-6 border-b border-gray-100">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Detailed Analysis Results</h3>
                  <p className="text-gray-600">Results from each AI agent's analysis</p>
                </div>
                
                <div className="p-6 space-y-6">
                  {analysisResult.agent_results.map((result, index) => {
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
                                  <h5 className="font-semibold text-gray-900 mb-2">Generated Files:</h5>
                                  <div className="flex flex-wrap gap-2">
                                    {result.execution_result.output_files.map((file, fileIndex) => (
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
          {analysisResult.report && (
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
                      {analysisResult.report.content}
                    </ReactMarkdown>
                  </div>
                  
                  {analysisResult.report.summary && (
                    <div className="mt-6 p-4 bg-emerald-50 rounded-xl border border-emerald-200">
                      <h4 className="font-semibold text-emerald-900 mb-2">Key Summary:</h4>
                      <ul className="list-disc list-inside text-emerald-800 space-y-1">
                        {analysisResult.report.summary.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
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
