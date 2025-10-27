"""
Time Series Analysis Agent
Specializes in time-based data analysis and forecasting
"""

from typing import Dict, Any, List


class TimeSeriesAnalysisAgent:
    """Agent for time series analysis and forecasting"""
    
    def __init__(self):
        self.name = "time_series_analysis"
        self.display_name = "Time Series Analysis"
        self.description = "Analyzes time-based data to identify trends, seasonality, and make forecasts"
        self.specialties = [
            "trend analysis",
            "seasonality detection",
            "forecasting",
            "arima modeling",
            "time series decomposition"
        ]
        self.keywords = [
            "time series", "trend", "forecast", "seasonal",
            "temporal", "date", "time", "arima", "prediction"
        ]
        self.required_columns = ["date"]
        self.output_type = "time_series_model"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for time series analysis"""
        
        return f"""
You are an expert data scientist specializing in time series analysis and forecasting.

**Task: Time Series Analysis & Forecasting**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive time series analysis including:

1. **Data Preparation:**
   - Identify and parse date/time columns automatically
   - Set proper datetime index for time series analysis
   - Handle missing dates and irregular intervals
   - Aggregate data to appropriate time frequency if needed

2. **Time Series Exploration:**
   - Create comprehensive time series plots
   - Analyze data frequency and time spans
   - Identify gaps, outliers, and anomalies in time series
   - Generate summary statistics over time periods

3. **Trend & Seasonality Analysis:**
   - Decompose time series into trend, seasonal, and residual components
   - Detect and quantify seasonal patterns (daily, weekly, monthly, yearly)
   - Identify long-term trends and change points
   - Calculate seasonal indices and trend strength

4. **Statistical Properties:**
   - Test for stationarity (Augmented Dickey-Fuller test)
   - Apply differencing to achieve stationarity if needed
   - Analyze autocorrelation and partial autocorrelation
   - Identify optimal parameters for ARIMA modeling

5. **Forecasting Models:**
   - Implement multiple forecasting approaches:
     * Simple methods (moving average, exponential smoothing)
     * ARIMA/SARIMA models
     * Seasonal decomposition forecasting
   - Generate forecasts with confidence intervals
   - Evaluate model accuracy using appropriate metrics

6. **Advanced Analysis:**
   - Anomaly detection in time series
   - Change point detection
   - Cross-correlation analysis with other variables
   - Business cycle analysis if applicable

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Handle different date formats automatically
- Save forecasts and results as 'time_series_results.csv'
- Create comprehensive time series visualizations
- Generate detailed analysis report as 'time_series_report.txt'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
warnings.filterwarnings('ignore')

# Your complete time series analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for time series analysis and forecasting",
    "description": "Time series decomposition, trend analysis, and forecasting with seasonal patterns",
    "outputs": ["time_series_results.csv", "time_series_report.txt", "time_series_plot.png", "decomposition.png", "forecast_plot.png"],
    "insights": "Time-based patterns, trends, seasonality findings, and forecast insights"
}}
"""

    def matches_request(self, user_question: str, data_columns: List[str]) -> float:
        """
        Calculate how well this agent matches the user's request
        
        Args:
            user_question: User's analysis question
            data_columns: Available data columns
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        question_lower = user_question.lower()
        
        # Check for time series keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in question_lower)
        keyword_score = min(keyword_matches / len(self.keywords), 1.0)
        
        # Check for date/time columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for date/time columns
        date_indicators = ['date', 'time', 'timestamp', 'created_at', 'updated_at', 
                          'year', 'month', 'day', 'datetime']
        has_date_col = any(indicator in ' '.join(column_names_lower) 
                          for indicator in date_indicators)
        
        if has_date_col:
            column_score = 0.8
        
        # Check for time-related values in data types
        date_types = ['datetime64', 'date', 'timestamp']
        has_date_type = any(date_type in str(dtype).lower() 
                           for dtype in data_columns)
        
        if has_date_type:
            column_score = max(column_score, 0.9)
        
        # Combined confidence score
        confidence = (keyword_score * 0.6) + (column_score * 0.4)
        
        return confidence
