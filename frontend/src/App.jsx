import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import DataUpload from './pages/DataUpload'
import AnalysisResults from './pages/AnalysisResults'
import ErrorBoundary from './components/ErrorBoundary'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="min-h-screen"
        >
          <Routes>
            <Route path="/" element={<DataUpload />} />
            <Route path="/analysis-results" element={
              <ErrorBoundary>
                <AnalysisResults />
              </ErrorBoundary>
            } />
          </Routes>
        </motion.div>
      </div>
    </Router>
  )
}

export default App
