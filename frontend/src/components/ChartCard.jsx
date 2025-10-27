import { motion } from 'framer-motion'
import { MoreHorizontal } from 'lucide-react'

export default function ChartCard({ title, description, icon: Icon }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
            <Icon className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-600">{description}</p>
          </div>
        </div>
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <MoreHorizontal className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Placeholder Chart */}
      <div className="h-48 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
        <div className="text-center">
          <Icon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-500">Chart will appear here</p>
          <p className="text-xs text-gray-400">Upload data to see visualizations</p>
        </div>
      </div>

      {/* Chart Footer */}
      <div className="mt-4 flex items-center justify-between text-sm">
        <span className="text-gray-600">Last updated: Just now</span>
        <motion.button
          whileHover={{ scale: 1.05 }}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          View Details
        </motion.button>
      </div>
    </div>
  )
}
