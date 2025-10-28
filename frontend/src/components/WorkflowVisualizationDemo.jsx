import React, { useState, useEffect } from 'react'
import WorkflowVisualization from './WorkflowVisualization'

const WorkflowVisualizationDemo = () => {
  const [mockProgress, setMockProgress] = useState({
    progress: 0,
    currentAgent: null,
    completedSteps: [],
    message: 'Starting analysis...'
  })

  // Mock selected agents for testing
  const mockSelectedAgents = [
    'data_quality_audit',
    'churn_prediction', 
    'customer_segmentation',
    'data_visualization'
  ]

  const steps = [
    'data_processor',
    'agent_selector', 
    ...mockSelectedAgents,
    'report_generator'
  ]

  useEffect(() => {
    let stepIndex = 0
    const interval = setInterval(() => {
      if (stepIndex < steps.length) {
        const currentStep = steps[stepIndex]
        const progress = (stepIndex + 1) * 12.5 // Roughly 12.5% per step
        
        setMockProgress({
          progress,
          currentAgent: currentStep,
          completedSteps: steps.slice(0, stepIndex),
          message: `Running ${currentStep.replace(/_/g, ' ')}...`
        })
        
        stepIndex++
      } else {
        // Complete the workflow
        setMockProgress(prev => ({
          ...prev,
          progress: 100,
          currentAgent: null,
          completedSteps: steps,
          message: 'Analysis complete!'
        }))
        clearInterval(interval)
      }
    }, 2000) // Change step every 2 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="p-8 bg-gray-100 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          Workflow Visualization Demo
        </h1>
        
        <WorkflowVisualization 
          analysisProgress={mockProgress}
          selectedAgents={mockSelectedAgents}
          className="mb-8"
        />
        
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Mock Progress Data:</h2>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
            {JSON.stringify(mockProgress, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default WorkflowVisualizationDemo
