import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  Upload,
  FileText,
  Users,
  Activity,
  BarChart3,
  PieChart,
  MessageSquare,
  Sparkles,
  Database,
  Zap
} from 'lucide-react'
import StatsCard from '../components/StatsCard'
import ChartCard from '../components/ChartCard'
import RecentActivity from '../components/RecentActivity'
import QuestionInterface from '../components/QuestionInterface'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalUploads: 0,
    totalFiles: 0,
    activeUsers: 0,
    dataProcessed: 0
  })

  useEffect(() => {
    // Fetch stats from API
    // For now, using mock data
    setStats({
      totalUploads: 1247,
      totalFiles: 89,
      activeUsers: 23,
      dataProcessed: 12.7
    })
  }, [])

  const statsData = [
    {
      title: 'Total Uploads',
      value: stats.totalUploads.toLocaleString(),
      change: '+12.5%',
      changeType: 'positive',
      icon: Upload,
    },
    {
      title: 'Files Processed',
      value: stats.totalFiles,
      change: '+8.2%',
      changeType: 'positive',
      icon: FileText,
    },
    {
      title: 'Active Users',
      value: stats.activeUsers,
      change: '+15.3%',
      changeType: 'positive',
      icon: Users,
    },
    {
      title: 'Data Processed',
      value: `${stats.dataProcessed}GB`,
      change: '+23.1%',
      changeType: 'positive',
      icon: Database,
    },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-primary-600" />
            Banta Dashboard
          </h1>
          <p className="text-gray-600 mt-1">
            Intelligent data analysis and insights at your fingertips
          </p>
        </div>
        
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl shadow-lg"
        >
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            <span className="font-medium">AI Powered</span>
          </div>
        </motion.div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {statsData.map((stat, index) => (
          <StatsCard key={stat.title} {...stat} index={index} />
        ))}
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Question Interface - Takes full width on large screens */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2"
        >
          <QuestionInterface />
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <RecentActivity />
        </motion.div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <ChartCard
            title="Upload Trends"
            description="File upload patterns over time"
            icon={BarChart3}
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <ChartCard
            title="Data Distribution"
            description="Analysis of data types and sizes"
            icon={PieChart}
          />
        </motion.div>
      </div>

      {/* Welcome Message for New Users */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.6 }}
        className="bg-gradient-to-r from-primary-50 to-indigo-50 rounded-2xl p-6 border border-primary-100"
      >
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <MessageSquare className="w-6 h-6 text-primary-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Welcome to Banta Intelligence Platform
            </h3>
            <p className="text-gray-600 mb-4">
              Upload your data and ask intelligent questions to get instant insights. 
              Our AI-powered analysis helps you understand your data like never before.
            </p>
            <div className="flex flex-wrap gap-3">
              <span className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 border border-gray-200">
                ✨ AI-Powered Analysis
              </span>
              <span className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 border border-gray-200">
                📊 Real-time Insights
              </span>
              <span className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 border border-gray-200">
                🔒 Secure Storage
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
