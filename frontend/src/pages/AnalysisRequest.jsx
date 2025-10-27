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

          {/* Premium Analysis Form */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="max-w-4xl mx-auto mb-12"
          >
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-2xl overflow-hidden">
              <div className="p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
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
                        placeholder="Ask me anything about your data... 

Try: 'Show me which products are trending upward this quarter' or 'What patterns do you see in customer behavior?'"
                        disabled={isLoading}
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
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      type="submit"
                      disabled={isLoading || !query.trim()}
                      className="px-12 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-lg font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3"
                    >
                      {isLoading ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin" />
                          Banta is analyzing...
                        </>
                      ) : (
                        <>
                          <Brain className="w-5 h-5" />
                          Ask Banta
                          <Send className="w-5 h-5" />
                        </>
                      )}
                    </motion.button>
                  </div>
                </form>
              </div>
            </div>
          </motion.div>

          {/* Example Queries Grid */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="max-w-6xl mx-auto mb-12"
          >
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Need inspiration? Try these questions
              </h3>
              <p className="text-gray-600">
                Click any example below to get started with your analysis
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {exampleQueries.map((example, index) => {
                const IconComponent = example.icon
                return (
                  <motion.button
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 + index * 0.1 }}
                    whileHover={{ y: -5, scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setQuery(example.text)}
                    disabled={isLoading}
                    className="group text-left p-6 bg-white/60 backdrop-blur-sm hover:bg-white/80 rounded-xl border border-gray-200/50 hover:border-indigo-300 transition-all duration-300 shadow-sm hover:shadow-xl disabled:opacity-50"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-indigo-100 to-purple-100 group-hover:from-indigo-200 group-hover:to-purple-200 rounded-xl flex items-center justify-center transition-all duration-300">
                        <IconComponent className="w-6 h-6 text-indigo-600" />
                      </div>
                      <div className="flex-1">
                        <div className="text-xs font-semibold text-indigo-600 uppercase tracking-wider mb-2">
                          {example.category}
                        </div>
                        <p className="text-gray-800 font-medium leading-relaxed group-hover:text-gray-900 transition-colors">
                          "{example.text}"
                        </p>
                      </div>
                    </div>
                  </motion.button>
                )
              })}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Premium Results Section */}
      {result && (
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
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      )}

      {/* Premium Loading State */}
      {isLoading && (
        <div className="px-6 pb-12">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 shadow-2xl overflow-hidden"
            >
              <div className="p-12 text-center">
                <motion.div
                  animate={{ 
                    scale: [1, 1.1, 1],
                    rotate: [0, 360] 
                  }}
                  transition={{ 
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut" 
                  }}
                  className="w-20 h-20 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6"
                >
                  <Brain className="w-10 h-10 text-white" />
                </motion.div>
                
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  Banta is analyzing your data...
                </h3>
                <p className="text-gray-600 text-lg mb-6">
                  Our AI is processing your request and finding the most valuable insights
                </p>
                
                {/* Loading Animation Dots */}
                <div className="flex items-center justify-center gap-2">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.3, 1, 0.3]
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.2
                      }}
                      className="w-3 h-3 bg-gradient-to-r from-indigo-400 to-purple-500 rounded-full"
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      )}
    </div>
  )
}
