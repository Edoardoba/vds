import { motion } from 'framer-motion'
import { Activity, Upload, FileText, BarChart3, Clock } from 'lucide-react'

export default function RecentActivity() {
  const activities = [
    {
      id: 1,
      type: 'upload',
      message: 'Sales_data_2024.csv uploaded',
      time: '2 minutes ago',
      icon: Upload,
      color: 'text-blue-600 bg-blue-50'
    },
    {
      id: 2,
      type: 'analysis',
      message: 'Generated trend analysis report',
      time: '5 minutes ago',
      icon: BarChart3,
      color: 'text-green-600 bg-green-50'
    },
    {
      id: 3,
      type: 'question',
      message: 'Asked about revenue patterns',
      time: '12 minutes ago',
      icon: FileText,
      color: 'text-purple-600 bg-purple-50'
    },
    {
      id: 4,
      type: 'upload',
      message: 'Customer_data.csv processed',
      time: '1 hour ago',
      icon: Upload,
      color: 'text-blue-600 bg-blue-50'
    },
    {
      id: 5,
      type: 'analysis',
      message: 'Detected data anomalies',
      time: '2 hours ago',
      icon: Activity,
      color: 'text-orange-600 bg-orange-50'
    }
  ]

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-gray-50 rounded-lg flex items-center justify-center">
          <Clock className="w-5 h-5 text-gray-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
          <p className="text-sm text-gray-600">Latest system activities</p>
        </div>
      </div>

      <div className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = activity.icon
          return (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200"
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${activity.color}`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {activity.message}
                </p>
                <p className="text-xs text-gray-500">{activity.time}</p>
              </div>
            </motion.div>
          )
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <motion.button
          whileHover={{ scale: 1.02 }}
          className="w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium py-2 hover:bg-primary-50 rounded-lg transition-all duration-200"
        >
          View All Activity
        </motion.button>
      </div>
    </div>
  )
}
