import React, { useState, useEffect } from 'react'
import { apiEndpoints, handleApiError, formatDate } from '../utils/api'
import toast from 'react-hot-toast'

const AnalysisHistory = () => {
  const [history, setHistory] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedAnalysis, setSelectedAnalysis] = useState(null)

  useEffect(() => {
    loadHistory()
    loadStatistics()
  }, [])

  const loadHistory = async () => {
    try {
      setLoading(true)
      const response = await apiEndpoints.getRecentHistory(20)
      setHistory(response.data.analyses || [])
    } catch (error) {
      handleApiError(error, 'Failed to load analysis history')
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const response = await apiEndpoints.getAnalyticsStatistics()
      setStatistics(response.data.statistics || {})
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const viewAnalysis = async (analysisId) => {
    try {
      const response = await apiEndpoints.getAnalysisById(analysisId)
      setSelectedAnalysis(response.data.analysis)
    } catch (error) {
      handleApiError(error, 'Failed to load analysis details')
    }
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      completed: { bg: 'bg-green-100', text: 'text-green-800', label: '✓ Completed' },
      cached: { bg: 'bg-blue-100', text: 'text-blue-800', label: '⚡ Cached' },
      running: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: '⏳ Running' },
      failed: { bg: 'bg-red-100', text: 'text-red-800', label: '✗ Failed' },
      pending: { bg: 'bg-gray-100', text: 'text-gray-800', label: '○ Pending' },
    }

    const config = statusConfig[status] || statusConfig.pending

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    )
  }

  const formatExecutionTime = (ms) => {
    if (!ms) return 'N/A'
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Analyses</div>
            <div className="text-2xl font-bold text-gray-900">{statistics.total_analyses || 0}</div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Success Rate</div>
            <div className="text-2xl font-bold text-green-600">
              {(statistics.success_rate || 0).toFixed(1)}%
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Cache Hit Rate</div>
            <div className="text-2xl font-bold text-blue-600">
              {(statistics.cache_hit_rate || 0).toFixed(1)}%
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Avg Execution Time</div>
            <div className="text-2xl font-bold text-purple-600">
              {formatExecutionTime(statistics.avg_execution_time_ms)}
            </div>
          </div>
        </div>
      )}

      {/* Analysis History Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Analyses</h2>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Loading history...</p>
          </div>
        ) : history.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>No analysis history yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    File
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Question
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Execution Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {history.map((analysis) => (
                  <tr key={analysis.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(analysis.created_at)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs truncate" title={analysis.filename}>
                        {analysis.filename}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-md truncate" title={analysis.user_question}>
                        {analysis.user_question}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(analysis.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatExecutionTime(analysis.execution_time_ms)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => viewAnalysis(analysis.id)}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Analysis Details Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">Analysis Details</h3>
              <button
                onClick={() => setSelectedAnalysis(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="px-6 py-4 space-y-4">
              <div>
                <span className="text-sm font-medium text-gray-600">File:</span>
                <p className="text-gray-900">{selectedAnalysis.filename}</p>
              </div>

              <div>
                <span className="text-sm font-medium text-gray-600">Question:</span>
                <p className="text-gray-900">{selectedAnalysis.user_question}</p>
              </div>

              <div>
                <span className="text-sm font-medium text-gray-600">Status:</span>
                <div className="mt-1">{getStatusBadge(selectedAnalysis.status)}</div>
              </div>

              {selectedAnalysis.selected_agents && selectedAnalysis.selected_agents.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-gray-600">Agents Used:</span>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {selectedAnalysis.selected_agents.map((agent, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-gray-100 text-gray-800 text-sm rounded-full"
                      >
                        {agent}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedAnalysis.is_cached && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <span className="text-blue-600 mr-2">⚡</span>
                    <span className="text-sm font-medium text-blue-900">
                      This result was served from cache
                    </span>
                  </div>
                </div>
              )}

              {selectedAnalysis.errors && selectedAnalysis.errors.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-red-600">Errors:</span>
                  <ul className="mt-2 space-y-1">
                    {selectedAnalysis.errors.map((error, idx) => (
                      <li key={idx} className="text-sm text-red-600">• {error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => setSelectedAnalysis(null)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnalysisHistory
