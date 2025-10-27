"""
Sales Performance Analytics Agent
Comprehensive sales analysis for revenue optimization and performance tracking
"""

from typing import Dict, Any, List


class SalesPerformanceAnalysisAgent:
    """Agent for sales performance analysis and revenue optimization"""
    
    def __init__(self):
        self.name = "sales_performance_analysis"
        self.display_name = "Sales Performance Analytics"
        self.description = "Comprehensive sales analysis including revenue trends, conversion rates, sales funnel optimization, and territory performance"
        self.specialties = [
            "revenue trend analysis",
            "conversion rate optimization",
            "sales funnel analysis",
            "territory performance",
            "quota attainment tracking",
            "sales efficiency metrics"
        ]
        self.keywords = [
            "sales", "revenue", "conversion", "funnel", 
            "territory", "quota", "performance", "deals", "pipeline"
        ]
        self.required_columns = ["revenue"]
        self.output_type = "sales_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for sales performance analysis"""
        
        return f"""
You are an expert sales analyst specializing in revenue optimization and sales performance management.

**Task: Comprehensive Sales Performance Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive sales performance analysis including:

1. **Revenue Analysis & Trends:**
   - Total revenue calculation and growth trends
   - Monthly/quarterly/yearly revenue patterns
   - Revenue by product, territory, and sales rep
   - Revenue forecasting and trend projections

2. **Sales Funnel Analysis:**
   - Lead conversion rates at each stage
   - Sales cycle length and velocity analysis
   - Drop-off points and bottleneck identification
   - Funnel optimization opportunities

3. **Territory & Rep Performance:**
   - Sales performance by geographic territory
   - Individual sales rep performance metrics
   - Quota attainment and goal achievement analysis
   - Top performers vs underperformers analysis

4. **Customer & Deal Analysis:**
   - Average deal size and distribution
   - Customer acquisition trends and patterns
   - Win/loss rate analysis by segment
   - Customer lifetime value calculations

5. **Sales Efficiency Metrics:**
   - Cost of customer acquisition (CAC)
   - Sales productivity and efficiency ratios
   - Return on sales investment (ROSI)
   - Sales team capacity utilization

6. **Performance Benchmarking:**
   - Industry benchmarking where possible
   - Year-over-year performance comparisons
   - Seasonal performance patterns
   - Goal vs actual performance tracking

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Generate executive sales dashboard visualizations
- Create comprehensive sales report as 'sales_performance_report.txt'
- Export key metrics as 'sales_kpis.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set professional visualization style
plt.style.use('default')
sns.set_palette("viridis")

# Your complete sales performance analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive sales performance analysis",
    "description": "End-to-end sales performance analytics with revenue trends, funnel analysis, and territory performance optimization",
    "outputs": ["sales_performance_report.txt", "sales_kpis.csv", "revenue_trends.png", "sales_funnel.png", "territory_performance.png", "rep_performance.png", "sales_dashboard.png"],
    "insights": "Key sales performance insights, revenue optimization opportunities, and actionable recommendations for sales team improvement"
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
        
        # Check for sales-related keywords with weighted importance
        primary_keywords = ["sales", "revenue", "conversion", "performance"]
        secondary_keywords = ["funnel", "territory", "quota", "deals", "pipeline", "rep"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.4 + secondary_matches * 0.15), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for revenue/sales columns
        revenue_indicators = ['revenue', 'sales', 'amount', 'value', 'price', 'total']
        has_revenue = any(indicator in ' '.join(column_names_lower) for indicator in revenue_indicators)
        
        if has_revenue:
            column_score = 0.6
        
        # Look for sales-related columns
        sales_indicators = ['deal', 'opportunity', 'lead', 'customer', 'territory', 'rep']
        has_sales_data = any(indicator in ' '.join(column_names_lower) for indicator in sales_indicators)
        
        if has_sales_data:
            column_score = max(column_score, 0.4)
        
        # Combined confidence score
        confidence = (keyword_score * 0.7) + (column_score * 0.3)
        
        return min(confidence, 1.0)
