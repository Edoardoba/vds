import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  ComposedChart
} from 'recharts'
import {
  Download,
  Settings,
  RefreshCw,
  TrendingUp,
  BarChart3 as BarChartIcon,
  PieChart as PieChartIcon,
  Activity,
  Maximize,
  Minimize,
  X
} from 'lucide-react'
import { apiEndpoints } from '../utils/api'
import toast from 'react-hot-toast'

const COLORS = [
  '#3b82f6', '#8b5cf6', '#ec4899', '#10b981', 
  '#f59e0b', '#ef4444', '#06b6d4', '#84cc16'
]

const InteractiveCharts = ({ file, dataPreview, analysisProgress, userQuestion = null }) => {
  const [chartData, setChartData] = useState(null)
  const [loading, setLoading] = useState(false) // Start false, will be set to true only when fetching
  const [fullscreenChart, setFullscreenChart] = useState(null) // Chart ID that's in fullscreen mode
  const [chartConfigs, setChartConfigs] = useState([
    {
      id: 1,
      type: 'bar',
      title: 'Data Distribution',
      xKey: null,
      yKey: null,
      showLegend: true,
      color: COLORS[0]
    },
    {
      id: 2,
      type: 'area',
      title: 'Trend Analysis',
      xKey: null,
      yKey: null,
      showLegend: true,
      color: COLORS[1]
    },
    {
      id: 3,
      type: 'pie',
      title: 'Category Breakdown',
      xKey: null,
      yKey: null,
      showLegend: true,
      color: COLORS[2]
    }
  ])

  const chartRefs = {
    1: useRef(null),
    2: useRef(null),
    3: useRef(null)
  }

  useEffect(() => {
    if (dataPreview) {
      processDataPreview(dataPreview)
    } else if (file && !dataPreview) {
      fetchDataPreview()
    }
  }, [file, dataPreview])

  const fetchDataPreview = async () => {
    if (!file) return
    
    try {
      setLoading(true)
      const response = await apiEndpoints.previewData(file)
      if (response.data?.success && response.data?.preview) {
        processDataPreview(response.data.preview)
      }
    } catch (error) {
      console.error('Error fetching data preview:', error)
      toast.error('Failed to load data for charts')
      generateMockData()
    } finally {
      setLoading(false)
    }
  }

  // Intelligent chart recommendation with variations based on user question and data
  const analyzeBestCharts = (columns, numericColumns, categoricalColumns, sampleData, question) => {
    const questionLower = (question || '').toLowerCase()
    
    // Generate truly random seed using crypto API for better variations each time
    let seed
    if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
      const randomArray = new Uint32Array(1)
      crypto.getRandomValues(randomArray)
      seed = randomArray[0]
    } else {
      // Fallback: use multiple random factors
      const fileHash = sampleData.length > 0 ? JSON.stringify(sampleData[0]).length : 0
      const numCols = numericColumns.length + categoricalColumns.length || columns.length
      seed = Date.now() + Math.random() * 1000000 + (question ? question.length + question.charCodeAt(0) : 0) + fileHash + numCols
    }
    const randomVariation = seed % 3 // 0, 1, or 2 for different variations
    
    // Analyze question intent
    const isTimeSeries = questionLower.match(/time|trend|over time|historical|past|future|forecast|prediction|growth|decline|increase|decrease/i)
    const isComparison = questionLower.match(/compare|comparison|versus|vs|difference|between|across|different/i)
    const isDistribution = questionLower.match(/distribution|spread|range|variation|variability|scatter/i)
    const isProportion = questionLower.match(/percentage|proportion|share|part of|breakdown|category|categories|segment/i)
    const isAggregation = questionLower.match(/total|sum|average|mean|aggregate|group|grouped|by/i)
    
    // Analyze data characteristics
    const uniqueValueCounts = {}
    columns.forEach((col, idx) => {
      const uniqueValues = new Set()
      sampleData.slice(0, 100).forEach(row => {
        const val = row[col] !== undefined ? row[col] : row[idx]
        if (val != null && val !== '') uniqueValues.add(String(val))
      })
      uniqueValueCounts[col] = uniqueValues.size
    })
    
    const dateColumns = columns.filter(col => {
      const colLower = col.toLowerCase()
      return colLower.includes('date') || colLower.includes('time') || colLower.includes('year') || 
             colLower.includes('month') || colLower.includes('day') || colLower.includes('timestamp')
    })
    
    // Shuffle arrays with seed-based randomization for variations
    const shuffleArray = (arr, seed) => {
      const shuffled = [...arr]
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(((seed * (i + 1)) % 1000) / 1000 * (i + 1))
        ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
      }
      return shuffled
    }
    
    // Apply variation to column selection
    const shuffledNumeric = shuffleArray(numericColumns, seed)
    const shuffledCategorical = shuffleArray(categoricalColumns, seed)
    
    // Recommendation 1: Bar Chart (with variations)
    const barTitles = ['Data Distribution', 'Comparison Analysis', 'Overview', 'Key Metrics', 'Performance View', 'Value Comparison', 'Category Analysis']
    const barTitleIndex = (seed % barTitles.length)
    let barChartTitle = barTitles[barTitleIndex] // Always use randomized title
    let barXKey = null
    let barYKey = null
    
    // Only override title if there's a VERY specific intent match AND random chance (50%)
    if (isComparison && shuffledCategorical.length > 0 && shuffledNumeric.length > 0 && (seed % 2 === 0)) {
      barChartTitle = 'Comparison Analysis' // Only sometimes override
    } else if (isAggregation && shuffledCategorical.length > 0 && shuffledNumeric.length > 0 && (seed % 3 === 0)) {
      barChartTitle = 'Aggregated View' // Only sometimes override
    }
    // Otherwise keep the randomized title
    
    if (shuffledCategorical.length > 0 && shuffledNumeric.length > 0) {
      // Always vary column selection
      barXKey = shuffledCategorical[randomVariation % shuffledCategorical.length] || shuffledCategorical[0]
      barYKey = shuffledNumeric[randomVariation % shuffledNumeric.length] || shuffledNumeric[0]
    }
    
    // Recommendation 2: Area Chart (with variations)
    const areaTitles = ['Trend Analysis', 'Time Series Trend', 'Growth Pattern', 'Performance Trend', 'Evolution View', 'Trend View', 'Progressive Analysis']
    const areaTitleIndex = ((seed + 1) % areaTitles.length)
    let areaChartTitle = areaTitles[areaTitleIndex] // Always use randomized title
    let areaXKey = null
    let areaYKey = null
    
    // Only override title if there's a VERY specific time series intent AND random chance (40%)
    if (isTimeSeries && dateColumns.length > 0 && shuffledNumeric.length > 0 && (seed % 5 < 2)) {
      areaChartTitle = 'Time Series Trend' // Only sometimes override
      areaXKey = dateColumns[0]
      areaYKey = shuffledNumeric[(randomVariation + 1) % shuffledNumeric.length] || shuffledNumeric[0]
    } else if (isTimeSeries && shuffledNumeric.length > 0 && (seed % 5 < 2)) {
      areaChartTitle = 'Trend Over Time' // Only sometimes override
      areaXKey = 'index'
      areaYKey = shuffledNumeric[(randomVariation + 2) % shuffledNumeric.length] || shuffledNumeric[0]
    } else if (shuffledNumeric.length > 0) {
      // Keep randomized title and vary columns
      areaXKey = dateColumns.length > 0 ? dateColumns[0] : 'index'
      areaYKey = shuffledNumeric[(randomVariation + 1) % shuffledNumeric.length] || shuffledNumeric[0]
    }
    
    // Recommendation 3: Pie Chart (with variations)
    const pieTitles = ['Category Breakdown', 'Proportion Analysis', 'Distribution View', 'Segment Analysis', 'Composition', 'Share Analysis', 'Partition View']
    const pieTitleIndex = ((seed + 2) % pieTitles.length)
    let pieChartTitle = pieTitles[pieTitleIndex] // Always use randomized title
    let pieXKey = null
    let pieYKey = null
    
    // Find suitable categorical columns
    const suitableCatCols = shuffledCategorical.filter(col => {
      const count = uniqueValueCounts[col] || 0
      return count >= 2 && count <= 15
    })
    
    // Only override title if there's a VERY specific proportion intent AND random chance (40%)
    if (isProportion && suitableCatCols.length > 0 && shuffledNumeric.length > 0 && (seed % 5 < 2)) {
      pieChartTitle = 'Proportion Analysis' // Only sometimes override
    }
    // Otherwise keep the randomized title
    
    if (suitableCatCols.length > 0 && shuffledNumeric.length > 0) {
      // Vary column selection based on variation index
      const catColIndex = (randomVariation + (seed % suitableCatCols.length)) % suitableCatCols.length
      pieXKey = suitableCatCols[catColIndex] || shuffledCategorical[0]
      pieYKey = shuffledNumeric[(randomVariation + 2) % shuffledNumeric.length] || shuffledNumeric[0]
    } else if (shuffledCategorical.length > 0 && shuffledNumeric.length > 0) {
      pieXKey = shuffledCategorical[(randomVariation + 1) % shuffledCategorical.length] || shuffledCategorical[0]
      pieYKey = shuffledNumeric[randomVariation % shuffledNumeric.length] || shuffledNumeric[0]
    }
    
    return {
      bar: { title: barChartTitle, xKey: barXKey, yKey: barYKey },
      area: { title: areaChartTitle, xKey: areaXKey, yKey: areaYKey },
      pie: { title: pieChartTitle, xKey: pieXKey, yKey: pieYKey }
    }
  }

  const processDataPreview = (preview) => {
    try {
      if (!preview?.sample_data || preview.sample_data.length === 0) {
        generateMockData()
        return
      }

      const columns = preview.columns || []
      const sampleData = Array.isArray(preview.sample_data) 
        ? preview.sample_data 
        : JSON.parse(preview.sample_data)

      // Identify numeric and categorical columns
      const numericColumns = columns.filter((col, idx) => {
        if (sampleData.length === 0) return false
        const sampleValue = sampleData[0][col] || sampleData[0][idx]
        return !isNaN(parseFloat(sampleValue)) && isFinite(sampleValue)
      })

      const categoricalColumns = columns.filter((col, idx) => {
        if (sampleData.length === 0) return false
        const sampleValue = sampleData[0][col] || sampleData[0][idx]
        return isNaN(parseFloat(sampleValue)) || !isFinite(sampleValue)
      })

      // Process data for charts
      const processedData = sampleData.slice(0, 20).map((row, idx) => {
        const processed = { index: idx }
        columns.forEach((col, colIdx) => {
          const value = row[col] !== undefined ? row[col] : row[colIdx]
          if (!isNaN(parseFloat(value)) && isFinite(value)) {
            processed[col] = parseFloat(value)
          } else {
            processed[col] = String(value || '')
          }
        })
        return processed
      })

      // Get user question from analysisProgress or props
      const question = userQuestion || analysisProgress?.userQuestion || analysisProgress?.user_question || ''
      
      // Intelligent chart recommendations - make seed truly random
      const recommendations = analyzeBestCharts(columns, numericColumns, categoricalColumns, processedData, question)
      
      // Generate true random seed using crypto if available, fallback to multiple factors
      let randomSeed
      if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
        const randomArray = new Uint32Array(1)
        crypto.getRandomValues(randomArray)
        randomSeed = randomArray[0]
      } else {
        // Fallback: use multiple random factors
        randomSeed = Date.now() + Math.random() * 1000000 + processedData.length * Math.random()
      }
      
      // Apply color variations based on random seed for visual variety
      const colorSeed = randomSeed % COLORS.length
      
      // Chart 1: Bar chart (intelligently configured with variations)
      const config1 = {
        id: 1,
        type: 'bar',
        showLegend: true
      }
      if (recommendations.bar.xKey && recommendations.bar.yKey) {
        config1.title = recommendations.bar.title
        config1.xKey = recommendations.bar.xKey
        config1.yKey = recommendations.bar.yKey
        config1.color = COLORS[colorSeed % COLORS.length]
      } else if (numericColumns.length > 0) {
        config1.title = 'Data Distribution'
        config1.xKey = categoricalColumns[0] || columns[0] || 'index'
        config1.yKey = numericColumns[0]
        config1.color = COLORS[colorSeed % COLORS.length]
      } else {
        config1.title = 'Data Distribution'
        config1.xKey = null
        config1.yKey = null
        config1.color = COLORS[0]
      }

      // Chart 2: Area chart (for trends with variations)
      const config2 = {
        id: 2,
        type: 'area',
        showLegend: true
      }
      if (recommendations.area.xKey && recommendations.area.yKey) {
        config2.title = recommendations.area.title
        config2.xKey = recommendations.area.xKey
        config2.yKey = recommendations.area.yKey
        config2.color = COLORS[(colorSeed + 1) % COLORS.length]
      } else if (numericColumns.length > 0) {
        config2.title = 'Trend Analysis'
        config2.xKey = 'index'
        config2.yKey = numericColumns[0]
        config2.color = COLORS[(colorSeed + 1) % COLORS.length]
      } else {
        config2.title = 'Trend Analysis'
        config2.xKey = null
        config2.yKey = null
        config2.color = COLORS[1]
      }

      // Chart 3: Pie chart (for proportions with variations)
      const config3 = {
        id: 3,
        type: 'pie',
        showLegend: true
      }
      if (recommendations.pie.xKey && recommendations.pie.yKey) {
        config3.title = recommendations.pie.title
        config3.xKey = recommendations.pie.xKey
        config3.yKey = recommendations.pie.yKey
        config3.color = COLORS[(colorSeed + 2) % COLORS.length]
      } else if (categoricalColumns.length > 0 && numericColumns.length > 0) {
        config3.title = 'Category Breakdown'
        config3.xKey = categoricalColumns[0]
        config3.yKey = numericColumns[0]
        config3.color = COLORS[(colorSeed + 2) % COLORS.length]
      } else {
        config3.title = 'Category Breakdown'
        config3.xKey = null
        config3.yKey = null
        config3.color = COLORS[2]
      }

      // Set all configs at once
      setChartConfigs([config1, config2, config3])
      setChartData(processedData)
    } catch (error) {
      console.error('Error processing data:', error)
      generateMockData()
    }
  }

  const generateMockData = () => {
    // Generate mock data if preview is not available
    const mockData = Array.from({ length: 12 }, (_, i) => ({
      index: i,
      month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i],
      sales: Math.floor(Math.random() * 1000) + 500,
      revenue: Math.floor(Math.random() * 5000) + 2000,
      customers: Math.floor(Math.random() * 200) + 100,
      category: ['A', 'B', 'C', 'D', 'E', 'F'][Math.floor(Math.random() * 6)]
    }))

    setChartConfigs([
      {
        id: 1,
        type: 'bar',
        title: 'Data Distribution',
        xKey: 'month',
        yKey: 'sales',
        showLegend: true,
        color: COLORS[0]
      },
      {
        id: 2,
        type: 'area',
        title: 'Trend Analysis',
        xKey: 'index',
        yKey: 'revenue',
        showLegend: true,
        color: COLORS[1]
      },
      {
        id: 3,
        type: 'pie',
        title: 'Category Breakdown',
        xKey: 'category',
        yKey: 'sales',
        showLegend: true,
        color: COLORS[2]
      }
    ])
    setChartData(mockData)
    setLoading(false)
  }

  const exportChartAsPNG = async (chartId) => {
    const chartRef = chartRefs[chartId]?.current
    if (!chartRef) {
      toast.error('Chart element not found')
      return
    }

    try {
      // Try to use html2canvas for high-quality PNG export
      try {
        const html2canvas = (await import('html2canvas')).default
        const canvas = await html2canvas(chartRef, {
          backgroundColor: '#ffffff',
          scale: 2,
          logging: false,
          useCORS: true
        })

        canvas.toBlob((blob) => {
          if (!blob) {
            throw new Error('Failed to create blob')
          }
          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `chart_${chartId}_${Date.now()}.png`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          URL.revokeObjectURL(url)
          toast.success('Chart exported successfully!')
        }, 'image/png')
      } catch (html2canvasError) {
        // Fallback: try to use SVG export
        console.warn('html2canvas not available, using SVG fallback:', html2canvasError)
        const svgElement = chartRef.querySelector('svg')
        if (svgElement) {
          const svgData = new XMLSerializer().serializeToString(svgElement)
          const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
          const url = URL.createObjectURL(svgBlob)
          const link = document.createElement('a')
          link.href = url
          link.download = `chart_${chartId}_${Date.now()}.svg`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          URL.revokeObjectURL(url)
          toast.success('Chart exported as SVG!')
        } else {
          toast.error('Failed to export chart. Chart element not found.')
        }
      }
    } catch (error) {
      console.error('Export error:', error)
      toast.error('Failed to export chart. Please try again.')
    }
  }

  const updateChartConfig = (chartId, updates) => {
    setChartConfigs(prev => 
      prev.map(config => 
        config.id === chartId ? { ...config, ...updates } : config
      )
    )
  }

  const getAvailableColumns = () => {
    if (!chartData || chartData.length === 0) return []
    return Object.keys(chartData[0]).filter(key => key !== 'index')
  }

  const getNumericColumns = () => {
    if (!chartData || chartData.length === 0) return []
    const firstRow = chartData[0]
    return Object.keys(firstRow).filter(key => {
      const value = firstRow[key]
      return key !== 'index' && !isNaN(parseFloat(value)) && isFinite(value)
    })
  }

  const getCategoricalColumns = () => {
    if (!chartData || chartData.length === 0) return []
    const numericCols = getNumericColumns()
    return Object.keys(chartData[0]).filter(key => !numericCols.includes(key) && key !== 'index')
  }

  const processPieData = (data, categoryKey, valueKey) => {
    if (!data || !categoryKey || !valueKey) return []
    
    const aggregated = {}
    data.forEach(item => {
      const category = String(item[categoryKey] || 'Unknown')
      const value = parseFloat(item[valueKey]) || 0
      aggregated[category] = (aggregated[category] || 0) + value
    })

    return Object.entries(aggregated).map(([name, value]) => ({
      name,
      value
    }))
  }

  const renderChart = (config) => {
    if (loading || !chartData || chartData.length === 0) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 text-blue-500 mx-auto mb-2 animate-spin" />
            <p className="text-sm text-gray-500">Loading chart data...</p>
          </div>
        </div>
      )
    }

    const { type, xKey, yKey, title, showLegend } = config

    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey={xKey || 'index'} 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              {showLegend && <Legend />}
              <Bar 
                dataKey={yKey || 'value'} 
                fill={config.color || COLORS[0]}
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'area':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id={`gradient-${config.id}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={config.color || COLORS[1]} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={config.color || COLORS[1]} stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey={xKey || 'index'} 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              {showLegend && <Legend />}
              <Area 
                type="monotone" 
                dataKey={yKey || 'value'} 
                stroke={config.color || COLORS[1]}
                fill={`url(#gradient-${config.id})`}
                strokeWidth={3}
                activeDot={{ r: 6 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )

      case 'pie':
        const pieData = processPieData(chartData, xKey, yKey)
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                outerRadius={70}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              {showLegend && <Legend />}
            </PieChart>
          </ResponsiveContainer>
        )

      default:
        return <div>Unsupported chart type</div>
    }
  }

  if (loading && !chartData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-500 mx-auto mb-4 animate-spin" />
          <p className="text-lg font-medium text-gray-700">Loading interactive charts...</p>
          <p className="text-sm text-gray-500 mt-2">Preparing your data visualization</p>
        </div>
      </div>
    )
  }

  const fullscreenConfig = fullscreenChart ? chartConfigs.find(c => c.id === fullscreenChart) : null

  return (
    <>
      <div className="p-6 space-y-6">
        <div className="mb-4">
          <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Activity className="w-6 h-6 text-indigo-600" />
            Interactive Data Exploration
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Explore your data with interactive charts while agents analyze
          </p>
        </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {chartConfigs.map((config, idx) => (
          <motion.div
            key={config.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="bg-white rounded-xl border border-gray-200 shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
          >
            {/* Chart Header */}
            <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {config.type === 'bar' && <BarChartIcon className="w-5 h-5 text-indigo-600" />}
                  {config.type === 'area' && <TrendingUp className="w-5 h-5 text-purple-600" />}
                  {config.type === 'pie' && <PieChartIcon className="w-5 h-5 text-pink-600" />}
                  <h4 className="font-semibold text-gray-900">{config.title}</h4>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setFullscreenChart(config.id)}
                    className="p-2 text-gray-600 hover:text-indigo-600 hover:bg-white rounded-lg transition-colors"
                    title="Fullscreen"
                  >
                    <Maximize className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => exportChartAsPNG(config.id)}
                    className="p-2 text-gray-600 hover:text-indigo-600 hover:bg-white rounded-lg transition-colors"
                    title="Export as PNG"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Chart Container */}
            <div className="p-4">
              <div 
                ref={chartRefs[config.id]}
                className="h-64 w-full"
              >
                {renderChart(config)}
              </div>
            </div>

            {/* Chart Controls */}
            <div className="p-4 bg-gray-50 border-t border-gray-200 space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    X-Axis / Category
                  </label>
                  <select
                    value={config.xKey || ''}
                    onChange={(e) => updateChartConfig(config.id, { xKey: e.target.value })}
                    className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select column...</option>
                    {(config.type === 'pie' ? getCategoricalColumns() : getAvailableColumns()).map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Y-Axis / Value
                  </label>
                  <select
                    value={config.yKey || ''}
                    onChange={(e) => updateChartConfig(config.id, { yKey: e.target.value })}
                    className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select column...</option>
                    {getNumericColumns().map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                <label className="flex items-center gap-2 text-xs text-gray-600">
                  <input
                    type="checkbox"
                    checked={config.showLegend}
                    onChange={(e) => updateChartConfig(config.id, { showLegend: e.target.checked })}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  Show Legend
                </label>
                <div className="flex items-center gap-2">
                  <label className="text-xs text-gray-600">Color:</label>
                  <input
                    type="color"
                    value={config.color}
                    onChange={(e) => updateChartConfig(config.id, { color: e.target.value })}
                    className="w-8 h-8 rounded border border-gray-300 cursor-pointer"
                  />
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {(!chartData || chartData.length === 0) && !loading && (
        <div className="text-center py-8 text-gray-500">
          <p>No data available for charts. Upload a file to get started.</p>
        </div>
      )}
      </div>

      {/* Fullscreen Modal */}
      {fullscreenChart && fullscreenConfig && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-sm flex flex-col"
          onClick={() => setFullscreenChart(null)}
        >
          {/* Fullscreen Header */}
          <div className="p-6 bg-gray-900 border-b border-gray-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {fullscreenConfig.type === 'bar' && <BarChartIcon className="w-6 h-6 text-indigo-400" />}
              {fullscreenConfig.type === 'area' && <TrendingUp className="w-6 h-6 text-purple-400" />}
              {fullscreenConfig.type === 'pie' && <PieChartIcon className="w-6 h-6 text-pink-400" />}
              <h2 className="text-2xl font-bold text-white">{fullscreenConfig.title}</h2>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  exportChartAsPNG(fullscreenChart)
                }}
                className="p-3 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                title="Export as PNG"
              >
                <Download className="w-5 h-5" />
              </button>
              <button
                onClick={() => setFullscreenChart(null)}
                className="p-3 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                title="Exit Fullscreen"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Fullscreen Chart Container */}
          <div 
            className="flex-1 flex flex-col overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Chart Display */}
            <div className="flex-1 p-8 bg-gray-950">
              <div 
                ref={chartRefs[fullscreenChart]}
                className="w-full h-full"
              >
                {renderChart(fullscreenConfig)}
              </div>
            </div>

            {/* Fullscreen Controls - Same as regular controls */}
            <div className="p-6 bg-gray-900 border-t border-gray-800">
              <div className="max-w-4xl mx-auto space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      X-Axis / Category
                    </label>
                    <select
                      value={fullscreenConfig.xKey || ''}
                      onChange={(e) => updateChartConfig(fullscreenChart, { xKey: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 text-white border border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select column...</option>
                      {(fullscreenConfig.type === 'pie' ? getCategoricalColumns() : getAvailableColumns()).map(col => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Y-Axis / Value
                    </label>
                    <select
                      value={fullscreenConfig.yKey || ''}
                      onChange={(e) => updateChartConfig(fullscreenChart, { yKey: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 text-white border border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Select column...</option>
                      {getNumericColumns().map(col => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-800">
                  <label className="flex items-center gap-2 text-sm text-gray-300">
                    <input
                      type="checkbox"
                      checked={fullscreenConfig.showLegend}
                      onChange={(e) => updateChartConfig(fullscreenChart, { showLegend: e.target.checked })}
                      className="rounded border-gray-600 bg-gray-800 text-indigo-600 focus:ring-indigo-500"
                    />
                    Show Legend
                  </label>
                  <div className="flex items-center gap-3">
                    <label className="text-sm text-gray-300">Color:</label>
                    <input
                      type="color"
                      value={fullscreenConfig.color}
                      onChange={(e) => updateChartConfig(fullscreenChart, { color: e.target.value })}
                      className="w-10 h-10 rounded border border-gray-700 cursor-pointer"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </>
  )
}

export default InteractiveCharts

