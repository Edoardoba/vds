import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Send, 
  ArrowLeft,
  Loader,
  Lightbulb,
  BarChart3,
  Brain,
  Sparkles,
  TrendingUp,
  PieChart,
  Zap,
  MessageCircle,
  Star,
  CheckCircle
} from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

export default function AnalysisRequest() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) {
      toast.error('Please enter your analysis request')
      return
    }

    setIsLoading(true)
    try {
      const response = await axios.post('/api/analyze', {
        query: query.trim()
      })
      
      setResult(response.data)
      toast.success('Analysis completed!')
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Analysis failed'
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const exampleQueries = [
    {
      icon: TrendingUp,
      text: "Show me sales trends over the last 12 months",
      category: "Trends"
    },
    {
      icon: BarChart3,
      text: "Which products generate the highest profit margins?",
      category: "Performance"
    },
    {
      icon: PieChart,
      text: "Analyze customer segments by demographics",
      category: "Segmentation"
    },
    {
      icon: Zap,
      text: "Predict next quarter's revenue based on current trends",
      category: "Forecasting"
    },
    {
      icon: Star,
      text: "Identify top-performing sales regions",
      category: "Regional"
    },
    {
      icon: MessageCircle,
      text: "What factors drive customer satisfaction scores?",
      category: "Insights"
    }
  ]

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
        </div>
      </nav>

      {/* Hero Section */}
      <div className="px-6 pt-8 pb-12">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-100 to-teal-100 rounded-full text-emerald-700 text-sm font-medium mb-6"
            >
              <Brain className="w-4 h-4" />
              AI-Powered Data Analysis
            </motion.div>
            
            <h1 className="text-5xl md:text-6xl font-black mb-6">
              <span className="text-gray-900">Ask</span>{' '}
              <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Banta
              </span>
              <br />
              <span className="text-gray-900">Anything</span>
            </h1>
            
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
              Your data is uploaded and ready. Now chat with Banta using natural language to uncover
              <span className="font-semibold text-indigo-600"> deep insights, trends, and predictions</span> 
              from your business data.
            </p>
          </motion.div>

        {/* Analysis Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card mb-6"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                What would you like to analyze?
              </label>
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={4}
                className="input-field resize-none"
                placeholder="Enter your analysis request here... 
For example: 'Show me the top 10 products by sales' or 'What are the monthly revenue trends?'"
                disabled={isLoading}
              />
            </div>
            
            <div className="flex justify-end">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                disabled={isLoading || !query.trim()}
                className="btn-primary"
              >
                {isLoading ? (
                  <>
                    <Loader className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Analyze Data
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </motion.div>

        {/* Example Queries */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-blue-50 rounded-xl p-6 border border-blue-200 mb-6"
        >
          <div className="flex items-start gap-3">
            <Lightbulb className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium text-blue-900 mb-3">Example Analysis Requests</h3>
              <div className="grid grid-cols-1 gap-2">
                {exampleQueries.map((example, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setQuery(example)}
                    className="text-left p-3 text-sm text-blue-800 hover:bg-blue-100 rounded-lg transition-colors border border-blue-200"
                    disabled={isLoading}
                  >
                    "{example}"
                  </motion.button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Results */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900">Analysis Results</h3>
            </div>
            
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-lg text-sm">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </motion.div>
        )}

        {/* Loading State */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
          >
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
                <p className="text-gray-600">Analyzing your data...</p>
                <p className="text-sm text-gray-500 mt-1">This may take a few moments</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
