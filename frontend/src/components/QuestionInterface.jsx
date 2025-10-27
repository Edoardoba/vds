import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, Sparkles, Upload, FileText, Brain, MessageSquare } from 'lucide-react'
import { clsx } from 'clsx'

export default function QuestionInterface() {
  const [question, setQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [hasUploadedData, setHasUploadedData] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim()) return

    setIsLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false)
      setQuestion('')
      // Handle response here
    }, 2000)
  }

  const sampleQuestions = [
    "What are the key trends in this data?",
    "Show me the correlation between different variables",
    "What anomalies can you detect?",
    "Generate a summary report of the uploaded data"
  ]

  return (
    <div className="card h-fit">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-indigo-500 rounded-lg flex items-center justify-center">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">AI Assistant</h2>
          <p className="text-gray-600 text-sm">Ask questions about your data</p>
        </div>
      </div>

      {!hasUploadedData ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center py-12 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50"
        >
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Upload Data First
          </h3>
          <p className="text-gray-600 mb-6">
            Upload your file to start asking intelligent questions about your data.
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => window.location.href = '/upload'}
            className="btn-primary"
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload Data
          </motion.button>
        </motion.div>
      ) : (
        <div>
          {/* Question Input */}
          <form onSubmit={handleSubmit} className="mb-6">
            <div className="relative">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask me anything about your data..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                rows={3}
                disabled={isLoading}
              />
              <motion.button
                type="submit"
                disabled={!question.trim() || isLoading}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={clsx(
                  'absolute bottom-3 right-3 p-2 rounded-lg transition-all duration-200',
                  question.trim() && !isLoading
                    ? 'bg-primary-600 text-white hover:bg-primary-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                )}
              >
                {isLoading ? (
                  <div className="loading-spinner w-4 h-4" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </motion.button>
            </div>
          </form>

          {/* Sample Questions */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">
              Sample Questions:
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {sampleQuestions.map((sample, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setQuestion(sample)}
                  className="text-left p-3 text-sm text-gray-600 bg-gray-50 hover:bg-primary-50 hover:text-primary-700 rounded-lg border border-gray-200 hover:border-primary-200 transition-all duration-200"
                >
                  <MessageSquare className="w-4 h-4 inline mr-2" />
                  {sample}
                </motion.button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* AI Capabilities */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-primary-600" />
          <span className="text-sm font-medium text-gray-700">AI Capabilities</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {[
            'Statistical Analysis',
            'Pattern Recognition',
            'Trend Detection',
            'Data Visualization',
            'Anomaly Detection'
          ].map((capability) => (
            <span
              key={capability}
              className="px-2 py-1 bg-primary-50 text-primary-700 text-xs rounded-full border border-primary-200"
            >
              {capability}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
