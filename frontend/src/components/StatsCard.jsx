import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { clsx } from 'clsx'

export default function StatsCard({ title, value, change, changeType, icon: Icon, index }) {
  const isPositive = changeType === 'positive'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -4 }}
      className="card group hover:shadow-lg transition-all duration-300"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mb-3">{value}</p>
          
          <div className="flex items-center gap-2">
            {isPositive ? (
              <TrendingUp className="w-4 h-4 text-emerald-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-500" />
            )}
            <span
              className={clsx(
                'text-sm font-medium',
                isPositive ? 'text-emerald-600' : 'text-red-600'
              )}
            >
              {change}
            </span>
            <span className="text-sm text-gray-500">vs last month</span>
          </div>
        </div>
        
        <div className={clsx(
          'w-12 h-12 rounded-lg flex items-center justify-center transition-all duration-300',
          'group-hover:scale-110 group-hover:rotate-3',
          isPositive 
            ? 'bg-primary-50 text-primary-600 group-hover:bg-primary-100' 
            : 'bg-gray-50 text-gray-600 group-hover:bg-gray-100'
        )}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      
      {/* Animated bottom border */}
      <motion.div
        initial={{ scaleX: 0 }}
        whileHover={{ scaleX: 1 }}
        transition={{ duration: 0.3 }}
        className={clsx(
          'absolute bottom-0 left-0 h-1 rounded-b-xl origin-left',
          isPositive ? 'bg-emerald-500' : 'bg-red-500'
        )}
        style={{ width: '100%' }}
      />
    </motion.div>
  )
}
