"""
Seasonal Business Planning Agent
Seasonal pattern analysis and planning optimization for small businesses
"""

from typing import Dict, Any, List


class SeasonalBusinessPlanningAgent:
    """Agent for seasonal business analysis and planning optimization"""
    
    def __init__(self):
        self.name = "seasonal_business_planning"
        self.display_name = "Seasonal Business Planning"
        self.description = "Analyze seasonal patterns, optimize inventory and staffing for seasonal fluctuations, and develop strategic plans for peak and off-seasons"
        self.specialties = [
            "seasonal pattern analysis",
            "peak season optimization",
            "off-season planning",
            "inventory seasonal planning", 
            "staffing level optimization",
            "revenue seasonality forecasting"
        ]
        self.keywords = [
            "seasonal", "season", "peak", "off-season", "holiday",
            "quarterly", "monthly", "cyclical", "pattern", "fluctuation"
        ]
        self.required_columns = ["date"]
        self.output_type = "seasonal_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for seasonal business planning"""
        
        return f"""
You are an expert business strategist specializing in seasonal business optimization and planning for small and medium enterprises.

**Task: Comprehensive Seasonal Business Planning Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform SMB-focused seasonal planning analysis including:

1. **Seasonal Pattern Discovery:**
   - Monthly and quarterly seasonal trends
   - Peak and trough period identification
   - Holiday and special event impact analysis
   - Year-over-year seasonal comparison

2. **Revenue Seasonality Analysis:**
   - Seasonal revenue patterns and forecasting
   - Peak season revenue concentration
   - Off-season revenue strategies
   - Seasonal profitability analysis

3. **Inventory Seasonal Planning:**
   - Seasonal inventory requirements forecasting
   - Peak season stock optimization
   - Off-season inventory minimization
   - Seasonal product mix analysis

4. **Staffing Optimization:**
   - Seasonal workforce planning
   - Peak season staffing requirements
   - Off-season cost management
   - Seasonal hiring and training schedules

5. **Cash Flow Seasonal Management:**
   - Seasonal cash flow forecasting
   - Peak season cash requirements
   - Off-season cash preservation strategies
   - Seasonal financing needs assessment

6. **Strategic Seasonal Planning:**
   - Peak season preparation strategies
   - Off-season business development opportunities
   - Seasonal marketing calendar optimization
   - Year-round business stability recommendations

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Focus on actionable SMB seasonal strategies
- Create seasonal planning dashboard visualizations
- Generate comprehensive report as 'seasonal_planning_report.txt'
- Export seasonal forecasts as 'seasonal_forecasts.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

# Set seasonal analysis visualization style
plt.style.use('default')
sns.set_palette("husl")

# Your complete seasonal business planning code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for SMB seasonal business planning analysis",
    "description": "Comprehensive seasonal pattern analysis with peak/off-season optimization strategies and resource planning for small businesses",
    "outputs": ["seasonal_planning_report.txt", "seasonal_forecasts.csv", "seasonal_patterns.png", "revenue_seasonality.png", "inventory_planning.png", "staffing_calendar.png", "cash_flow_seasons.png"],
    "insights": "Seasonal business patterns, peak season opportunities, off-season strategies, and year-round planning recommendations for small business seasonal optimization"
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
        
        # Check for seasonal keywords
        primary_keywords = ["seasonal", "season", "peak", "off-season"]
        secondary_keywords = ["holiday", "quarterly", "monthly", "cyclical", "pattern", "fluctuation"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.5 + secondary_matches * 0.2), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for date columns (essential for seasonal analysis)
        date_indicators = ['date', 'time', 'month', 'quarter', 'year', 'period']
        has_date = any(indicator in ' '.join(column_names_lower) for indicator in date_indicators)
        
        # Look for business metrics that show seasonality
        business_indicators = ['revenue', 'sales', 'orders', 'customers', 'inventory', 'staff']
        has_metrics = any(indicator in ' '.join(column_names_lower) for indicator in business_indicators)
        
        if has_date:
            column_score += 0.6
        if has_metrics:
            column_score += 0.4
        
        # Combined confidence score
        confidence = (keyword_score * 0.7) + (column_score * 0.3)
        
        return min(confidence, 1.0)
