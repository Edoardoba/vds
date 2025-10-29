import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { 
  X, 
  CheckCircle, 
  AlertCircle, 
  Download, 
  FileText,
  BarChart3,
  Sparkles
} from 'lucide-react'

export default function AgentDetailsModal({ isOpen, onClose, agentResult, agentName, agentIcons }) {
  if (!isOpen || !agentResult) return null

  const IconComponent = agentIcons && agentIcons[agentName] ? agentIcons[agentName] : BarChart3
  const isSuccess = agentResult.execution_result?.success !== false

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <div
              className="bg-white rounded-3xl shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col pointer-events-auto border border-gray-200/50"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className={`p-6 border-b border-gray-200 flex-shrink-0 ${
                isSuccess ? 'bg-gradient-to-r from-green-50 to-emerald-50' : 'bg-gradient-to-r from-red-50 to-pink-50'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg ${
                      isSuccess
                        ? 'bg-gradient-to-br from-green-500 to-emerald-600 text-white'
                        : 'bg-gradient-to-br from-red-500 to-pink-600 text-white'
                    }`}>
                      <IconComponent className="w-7 h-7" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 capitalize mb-1">
                        {agentResult.agent_info?.display_name || agentName.replace(/_/g, ' ')}
                      </h2>
                      <p className="text-gray-600 text-sm">
                        {agentResult.agent_info?.description || 'AI Analysis Agent'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
                      isSuccess 
                        ? 'bg-green-100 text-green-800 border-2 border-green-200'
                        : 'bg-red-100 text-red-800 border-2 border-red-200'
                    }`}>
                      {isSuccess ? (
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-4 h-4" />
                          <span>Success</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <AlertCircle className="w-4 h-4" />
                          <span>Failed</span>
                        </div>
                      )}
                    </div>
                    
                    <motion.button
                      whileHover={{ scale: 1.1, rotate: 90 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={onClose}
                      className="w-10 h-10 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 flex items-center justify-center transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </motion.button>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {isSuccess ? (
                  <>
                    {/* Key Insights */}
                    {agentResult.code_result?.insights && (
                      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border-2 border-indigo-200 p-6">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-md">
                            <Sparkles className="w-5 h-5 text-white" />
                          </div>
                          <h3 className="text-xl font-bold text-gray-900">Key Insights</h3>
                        </div>
                        <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-indigo-200/50">
                          <div className="prose prose-gray max-w-none">
                            <ReactMarkdown
                              components={{
                                h1: ({children}) => <h1 className="text-xl font-bold text-gray-900 mb-3 mt-4">{children}</h1>,
                                h2: ({children}) => <h2 className="text-lg font-semibold text-gray-800 mb-2 mt-3">{children}</h2>,
                                h3: ({children}) => <h3 className="text-base font-semibold text-gray-800 mb-2 mt-3">{children}</h3>,
                                p: ({children}) => <p className="text-gray-700 mb-3 leading-relaxed">{children}</p>,
                                ul: ({children}) => <ul className="list-disc list-inside text-gray-700 mb-3 space-y-1 ml-4">{children}</ul>,
                                ol: ({children}) => <ol className="list-decimal list-inside text-gray-700 mb-3 space-y-1 ml-4">{children}</ol>,
                                li: ({children}) => <li className="text-gray-700 leading-relaxed">{children}</li>,
                                code: ({children}) => <code className="bg-gray-200 text-gray-800 px-2 py-1 rounded text-sm font-mono">{children}</code>,
                                strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>
                              }}
                            >
                              {agentResult.code_result.insights}
                            </ReactMarkdown>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Analysis Output */}
                    {agentResult.execution_result?.output && (
                      <div className="bg-gray-50 rounded-2xl border-2 border-gray-200 p-6">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-10 h-10 bg-gradient-to-br from-gray-500 to-gray-600 rounded-xl flex items-center justify-center shadow-md">
                            <FileText className="w-5 h-5 text-white" />
                          </div>
                          <h3 className="text-xl font-bold text-gray-900">Analysis Output</h3>
                        </div>
                        <div className="bg-white rounded-xl p-4 border border-gray-200">
                          <pre className="text-sm text-gray-700 whitespace-pre-wrap overflow-x-auto max-h-96 overflow-y-auto font-mono">
                            {agentResult.execution_result.output}
                          </pre>
                        </div>
                      </div>
                    )}

                    {/* Generated Files */}
                    {agentResult.execution_result?.output_files?.length > 0 && (
                      <div className="space-y-6">
                        {/* Images */}
                        {agentResult.execution_result.output_files
                          .filter(file => ['png', 'jpg', 'jpeg', 'svg'].includes(file.type))
                          .map((file, fileIndex) => (
                            <div key={fileIndex} className="bg-white rounded-2xl border-2 border-gray-200 shadow-lg overflow-hidden">
                              <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-gray-200">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-md">
                                      <BarChart3 className="w-5 h-5 text-white" />
                                    </div>
                                    <div>
                                      <h4 className="font-bold text-gray-900">{file.filename}</h4>
                                      <p className="text-sm text-gray-600">{file.size ? `${(file.size / 1024).toFixed(1)} KB` : ''}</p>
                                    </div>
                                  </div>
                                  <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => {
                                      const link = document.createElement('a')
                                      link.href = `data:image/${file.type};base64,${file.content}`
                                      link.download = file.filename
                                      link.click()
                                    }}
                                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all font-semibold shadow-md"
                                  >
                                    <Download className="w-4 h-4" />
                                    <span>Download</span>
                                  </motion.button>
                                </div>
                              </div>
                              {file.encoding === 'base64' && file.content && (
                                <div className="p-6 bg-gray-50">
                                  <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-inner">
                                    <img
                                      src={`data:image/${file.type};base64,${file.content}`}
                                      alt={file.filename}
                                      className="w-full max-w-full mx-auto rounded-lg shadow-lg"
                                      style={{ maxHeight: '600px', objectFit: 'contain' }}
                                    />
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}

                        {/* Text Files */}
                        {agentResult.execution_result.output_files
                          .filter(file => ['txt', 'md', 'csv'].includes(file.type))
                          .map((file, fileIndex) => (
                            <div key={fileIndex} className="bg-gray-50 rounded-2xl border-2 border-gray-200 p-6">
                              <div className="flex items-center gap-3 mb-4">
                                <FileText className="w-6 h-6 text-gray-600" />
                                <h4 className="font-bold text-gray-900">{file.filename}</h4>
                              </div>
                              {file.encoding === 'utf-8' && file.content && (
                                <div className="bg-white rounded-xl p-4 border border-gray-200">
                                  <pre className="text-sm text-gray-700 whitespace-pre-wrap max-h-64 overflow-y-auto font-mono">
                                    {file.content}
                                  </pre>
                                </div>
                              )}
                            </div>
                          ))}
                      </div>
                    )}
                  </>
                ) : (
                  <div className="bg-red-50 rounded-2xl border-2 border-red-200 p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <AlertCircle className="w-6 h-6 text-red-600" />
                      <h3 className="text-xl font-bold text-red-900">Analysis Failed</h3>
                    </div>
                    <div className="bg-white rounded-xl p-4 border border-red-200">
                      <p className="text-red-700">
                        {agentResult.error || agentResult.execution_result?.error || 'Unknown error occurred'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

