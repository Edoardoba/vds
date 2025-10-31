import React from 'react'
import { motion } from 'framer-motion'
import { 
  CheckCircle, 
  Clock, 
  Loader, 
  XCircle, 
  ArrowRight,
  Database,
  Brain,
  BarChart3,
  TrendingUp,
  FileText,
  AlertCircle,
  Users
} from 'lucide-react'

// Agent descriptions mapping (defined outside component to avoid hoisting issues)
const AGENT_DESCRIPTIONS = {
  'data_quality_audit': 'Analyzing data quality',
  'exploratory_data_analysis': 'Initial data exploration',
  'data_visualization': 'Creating charts and graphs',
  'statistical_analysis': 'Statistical computations',
  'churn_prediction': 'Predicting customer churn',
  'customer_segmentation': 'Segmenting customers',
  'sales_performance_analysis': 'Analyzing sales performance',
  'marketing_roi_analysis': 'Marketing ROI analysis',
  'time_series_analysis': 'Time series forecasting',
  'anomaly_detection': 'Detecting anomalies',
  'predictive_modeling': 'Building predictive models',
  'cohort_analysis': 'Cohort analysis',
  'profitability_analysis': 'Profitability analysis',
  'cash_flow_analysis': 'Cash flow analysis',
  'employee_performance_analysis': 'Employee performance analysis',
  'competitive_analysis': 'Competitive analysis',
  'seasonal_business_planning': 'Seasonal planning',
  'operational_bottleneck_detection': 'Detecting bottlenecks',
  'customer_acquisition_cost_analysis': 'CAC analysis',
  'ab_testing_analysis': 'A/B testing analysis'
}

// Agent icons mapping (defined outside component to avoid hoisting issues)
const AGENT_ICONS = {
  'data_quality_audit': CheckCircle,
  'exploratory_data_analysis': BarChart3,
  'data_visualization': BarChart3,
  'statistical_analysis': TrendingUp,
  'churn_prediction': TrendingUp,
  'customer_segmentation': Users,
  'sales_performance_analysis': TrendingUp,
  'marketing_roi_analysis': TrendingUp,
  'time_series_analysis': TrendingUp,
  'anomaly_detection': AlertCircle,
  'predictive_modeling': Brain,
  'cohort_analysis': Users,
  'profitability_analysis': TrendingUp,
  'cash_flow_analysis': TrendingUp,
  'employee_performance_analysis': Users,
  'competitive_analysis': BarChart3,
  'seasonal_business_planning': TrendingUp,
  'operational_bottleneck_detection': AlertCircle,
  'customer_acquisition_cost_analysis': TrendingUp,
  'ab_testing_analysis': TrendingUp
}

// Helper function to get agent descriptions (function declaration for proper hoisting)
function getAgentDescription(agentName) {
  return AGENT_DESCRIPTIONS[agentName] || 'AI analysis agent'
}

// Helper function to get agent icons (function declaration for proper hoisting)
function getAgentIcon(agentName) {
  return AGENT_ICONS[agentName] || Brain
}

const WorkflowVisualization = ({ analysisProgress, selectedAgents = [], className = "", onStepClick = null }) => {
  // Create dynamic workflow steps based on selected agents and actual execution order
  const createDynamicWorkflowSteps = () => {
    const steps = []
    
    // Add data processing step
    steps.push({
      id: 'data_processing',
      name: 'Data Processing',
      description: 'Processing  data',
      icon: Database,
      progress: 10
    })
    
    // Add Interactive Charts tab (shown while agents work)
    steps.push({
      id: 'interactive_charts',
      name: 'Interactive Charts',
      description: 'Explore data with interactive charts',
      icon: BarChart3,
      progress: 15
    })
    
    // Add user-selected agents as workflow steps
    if (selectedAgents && selectedAgents.length > 0) {
      selectedAgents.forEach((agent, index) => {
        const agentStep = {
          id: agent,
          name: agent.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          description: getAgentDescription(agent),
          icon: getAgentIcon(agent),
          progress: 20 + (index * (70 / selectedAgents.length)) // Use 70% for agents (20% to 90%)
        }
        steps.push(agentStep)
      })
    } else {
      // Fallback to default workflow if no agents selected
      steps.push(
        {
          id: 'data_quality_audit',
          name: 'Data Quality Audit',
          description: 'Analyzing data quality',
          icon: CheckCircle,
          progress: 30
        },
        {
          id: 'exploratory_analysis',
          name: 'Exploratory Analysis',
          description: 'Initial data exploration',
          icon: BarChart3,
          progress: 50
        },
        {
          id: 'data_visualization',
          name: 'Data Visualization',
          description: 'Creating charts and graphs',
          icon: BarChart3,
          progress: 70
        }
      )
    }
    
    // Always add report generation at the end
    steps.push({
      id: 'report_generator',
      name: 'Report Generation',
      description: 'Generating final report',
      icon: FileText,
      progress: 100
    })
    
    return steps
  }

  const workflowSteps = createDynamicWorkflowSteps()


  // Determine step status based on progress and current agent
  const getStepStatus = (step) => {
    if (!analysisProgress) return 'pending'
    
    const currentProgress = analysisProgress.progress || 0
    const completedSteps = analysisProgress.completedSteps || []
    const completedAgents = analysisProgress.completedAgents || []
    const currentAgent = analysisProgress.currentAgent
    const finalReport = analysisProgress.finalReport
    
    // If we already have a final report (e.g., cache hit), treat all steps as completed
    // so the UI reflects a fully completed workflow even without granular progress events
    if (finalReport && step.id !== 'report_generator') {
      return 'completed'
    }

    // Special handling for interactive charts - mark as completed immediately
    if (step.id === 'interactive_charts') {
      // Mark as completed once data processing starts (charts are ready to view)
      if (currentProgress > 0) {
        return 'completed'
      }
      return 'pending'
    }
    
    // Special handling for report generation step
    if (step.id === 'report_generator') {
      if (finalReport) {
        return 'completed'
      }
      // Check if all agents are completed and we're at 100% progress
      if (completedAgents.length > 0 && 
          selectedAgents && 
          completedAgents.length === selectedAgents.length &&
          currentProgress >= 95) {
        return 'active'
      }
      return 'pending'
    }
    
    // Check if step is completed (either in completedSteps or completedAgents)
    if (completedSteps.includes(step.id) || 
        completedAgents.some(agent => agent.agent_name === step.id)) {
      return 'completed'
    }
    
    // Check for errors in the analysis progress
    if (analysisProgress.errors && analysisProgress.errors.some(error => 
      error.toLowerCase().includes(step.id) || step.id.includes(error.toLowerCase())
    )) {
      return 'error'
    }
    
    // Check if step is currently running
    if (currentAgent === step.id) {
      return 'running'
    }
    
    // Check if step should be active based on progress
    if (currentProgress >= step.progress - 10) {
      return 'active'
    }
    
    return 'pending'
  }

  // Get step status
  const getStepStatusInfo = (status) => {
    switch (status) {
      case 'completed':
        return {
          icon: CheckCircle,
          color: 'text-green-500',
          bgColor: 'bg-green-100',
          borderColor: 'border-green-300',
          pulse: false
        }
      case 'running':
        return {
          icon: Loader,
          color: 'text-blue-500',
          bgColor: 'bg-blue-100',
          borderColor: 'border-blue-300',
          pulse: true
        }
      case 'active':
        return {
          icon: Clock,
          color: 'text-indigo-500',
          bgColor: 'bg-indigo-100',
          borderColor: 'border-indigo-300',
          pulse: false
        }
      case 'error':
        return {
          icon: XCircle,
          color: 'text-red-500',
          bgColor: 'bg-red-100',
          borderColor: 'border-red-300',
          pulse: false
        }
      default:
        return {
          icon: Clock,
          color: 'text-gray-400',
          bgColor: 'bg-gray-100',
          borderColor: 'border-gray-200',
          pulse: false
        }
    }
  }

  if (!analysisProgress) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
        <div className="p-6 text-center text-gray-500">
          <Clock className="w-8 h-8 mx-auto mb-2" />
          <p>Waiting for analysis to start...</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm ${className}`}>
      <div className="p-3">
        {/* Horizontal Workflow Tree */}
        <div className="relative">
          <div className="flex items-center gap-4 overflow-x-auto pb-4">
            {workflowSteps.map((step, index) => {
              const status = getStepStatus(step)
              const statusInfo = getStepStatusInfo(status)
              const IconComponent = statusInfo.icon
              const isLast = index === workflowSteps.length - 1
              
              return (
                <React.Fragment key={step.id}>
                  {/* Step Node */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className={`relative flex flex-col items-center group ${statusInfo.pulse ? 'animate-pulse' : ''} ${onStepClick && step.id === 'interactive_charts' ? 'cursor-pointer' : ''}`}
                    onClick={() => {
                      if (onStepClick && step.id === 'interactive_charts') {
                        onStepClick(step.id)
                      }
                    }}
                  >
                    {/* Step Circle */}
                    <motion.div
                      className={`
                        w-10 h-10 rounded-full border-2 flex items-center justify-center
                        ${statusInfo.bgColor} ${statusInfo.borderColor}
                        transition-all duration-300
                        ${status === 'running' ? 'shadow-lg shadow-blue-200' : ''}
                        ${status === 'completed' ? 'shadow-md shadow-green-200' : ''}
                        ${status === 'active' ? 'shadow-md shadow-indigo-200' : ''}
                        ${onStepClick && step.id === 'interactive_charts' ? 'hover:shadow-lg hover:scale-110' : ''}
                      `}
                      whileHover={onStepClick && step.id === 'interactive_charts' ? { scale: 1.15 } : { scale: 1.05 }}
                      animate={
                        status === 'running' 
                          ? { 
                              scale: [1, 1.05, 1],
                              boxShadow: [
                                '0 0 0 0 rgba(59, 130, 246, 0.4)',
                                '0 0 0 10px rgba(59, 130, 246, 0)',
                                '0 0 0 0 rgba(59, 130, 246, 0)'
                              ]
                            }
                          : status === 'completed'
                          ? { scale: 1 }
                          : {}
                      }
                      transition={
                        status === 'running' 
                          ? { duration: 2, repeat: Infinity, ease: "easeInOut" }
                          : { duration: 0.3 }
                      }
                    >
                      <IconComponent 
                        className={`w-5 h-5 ${statusInfo.color} ${
                          status === 'running' ? 'animate-spin' : ''
                        }`} 
                      />
                    </motion.div>
                    
                    {/* Step Label - Only name, no description */}
                    <div className="mt-1 text-center pb-3">
                      <p className={`text-xs font-medium whitespace-nowrap ${
                        status === 'completed' ? 'text-green-700' :
                        status === 'running' ? 'text-blue-700' :
                        status === 'active' ? 'text-indigo-700' :
                        'text-gray-500'
                      }`}>
                        {step.name}
                      </p>
                    </div>
                    
                    {/* Completion Checkmark - Positioned relative to circle, not label */}
                    {status === 'completed' && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                        className="absolute top-0 right-0 w-3 h-3 bg-green-500 rounded-full flex items-center justify-center z-10"
                        style={{ transform: 'translate(30%, -30%)' }}
                      >
                        <CheckCircle className="w-2 h-2 text-white" />
                      </motion.div>
                    )}
                    
                    {/* Progress Indicator */}
                    {status === 'running' && (
                      <motion.div
                        className="absolute top-0 right-0 w-3 h-3 bg-blue-500 rounded-full flex items-center justify-center z-10"
                        style={{ transform: 'translate(30%, -30%)' }}
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 1, repeat: Infinity }}
                      >
                        <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                      </motion.div>
                    )}
                    
                    {/* Tooltip */}
                    <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                      <div className="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap">
                        <div className="font-medium">{step.name}</div>
                        <div className="text-gray-300">{step.description}</div>
                        <div className="text-gray-400 mt-1">
                          Status: {status.charAt(0).toUpperCase() + status.slice(1)}
                        </div>
                      </div>
                      <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                    </div>
                  </motion.div>
                  
                  {/* Arrow Connector */}
                  {!isLast && (
                    <motion.div
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ delay: index * 0.1 + 0.2, duration: 0.3 }}
                      className="flex-1 flex items-center justify-center mx-2"
                    >
                      <div className="flex-1 h-0.5 bg-gray-200 relative overflow-hidden">
                        <motion.div
                          className="absolute top-0 left-0 h-full bg-gradient-to-r from-indigo-400 to-purple-500 rounded-full"
                          initial={{ width: '0%' }}
                          animate={{ 
                            width: getStepStatus(workflowSteps[index + 1]) === 'completed' ? '100%' : 
                                   getStepStatus(workflowSteps[index]) === 'completed' ? '100%' : 
                                   getStepStatus(workflowSteps[index]) === 'running' ? '50%' : '0%'
                          }}
                          transition={{ duration: 0.8, delay: index * 0.1 }}
                        />
                        
                        {/* Animated flow effect */}
                        {getStepStatus(workflowSteps[index]) === 'running' && (
                          <motion.div
                            className="absolute top-0 left-0 h-full w-4 bg-gradient-to-r from-transparent via-white to-transparent opacity-60"
                            animate={{ x: ['-100%', '100%'] }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                          />
                        )}
                        
                        <motion.div
                          animate={{ 
                            opacity: getStepStatus(workflowSteps[index]) === 'completed' ? 1 : 0.3,
                            scale: getStepStatus(workflowSteps[index]) === 'running' ? [1, 1.1, 1] : 1
                          }}
                          transition={{ duration: 1, repeat: getStepStatus(workflowSteps[index]) === 'running' ? Infinity : 0 }}
                        >
                          <ArrowRight className="w-4 h-4 text-gray-400 absolute right-0 top-1/2 transform -translate-y-1/2 translate-x-1/2" />
                        </motion.div>
                      </div>
                    </motion.div>
                  )}
                </React.Fragment>
              )
            })}
          </div>
        </div>
        
        {/* Error Display - Compact */}
        {analysisProgress.errors && analysisProgress.errors.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 p-2 bg-red-50 rounded-lg border border-red-200"
          >
            <div className="flex items-center gap-2">
              <AlertCircle className="w-3 h-3 text-red-500 flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-xs font-medium text-red-900">Errors:</p>
                <ul className="text-xs text-red-700 mt-1 space-y-0.5">
                  {analysisProgress.errors.map((error, index) => (
                    <li key={index} className="truncate">• {error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        )}
        
      </div>
    </div>
  )
}

export default WorkflowVisualization
