"""
Profitability & Cost Analysis Agent
Margin analysis and financial efficiency optimization for business decision making
"""

from typing import Dict, Any, List


class ProfitabilityAnalysisAgent:
    """Agent for profitability analysis and cost optimization"""
    
    def __init__(self):
        self.name = "profitability_analysis"
        self.display_name = "Profitability & Cost Analysis"
        self.description = "Margin analysis, cost optimization, profitability by segment/product/channel, and financial efficiency optimization"
        self.specialties = [
            "margin analysis",
            "cost optimization",
            "profitability segmentation",
            "unit economics",
            "cost-benefit analysis",
            "financial efficiency"
        ]
        self.keywords = [
            "profit", "margin", "cost", "profitability",
            "economics", "efficiency", "revenue", "expense"
        ]
        self.required_columns = ["revenue", "cost"]
        self.output_type = "profitability_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for profitability analysis"""
        
        return f"""
You are an expert financial analyst specializing in profitability optimization and cost management for business operations.

**Task: Comprehensive Profitability & Cost Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive profitability and cost analysis including:

1. **Financial Metrics Calculation:**
   - Gross profit, net profit, and profit margin calculations
   - EBITDA and operating margin analysis
   - Return on investment (ROI) and return on assets (ROA)
   - Cost per unit and revenue per unit metrics

2. **Profitability Segmentation:**
   - Profitability analysis by product/service lines
   - Customer segment profitability assessment
   - Geographic territory profit analysis
   - Channel profitability comparison

3. **Cost Structure Analysis:**
   - Fixed vs variable cost breakdown
   - Cost driver identification and analysis
   - Cost per acquisition and retention costs
   - Operating leverage and cost elasticity

4. **Unit Economics Assessment:**
   - Customer lifetime value (CLV) calculations
   - Customer acquisition cost (CAC) analysis
   - Payback period and break-even analysis
   - Contribution margin by product/customer

5. **Efficiency & Optimization:**
   - Cost reduction opportunities identification
   - Resource allocation optimization
   - Pricing strategy impact analysis
   - Operational efficiency improvements

6. **Trend Analysis & Forecasting:**
   - Profitability trend analysis over time
   - Seasonal profit pattern identification
   - Profit forecast modeling
   - Scenario analysis for different business conditions

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Generate executive financial dashboard visualizations
- Create comprehensive profitability report as 'profitability_analysis_report.txt'
- Export optimization recommendations as 'cost_optimization_opportunities.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set financial visualization style
plt.style.use('default')
sns.set_palette("RdYlGn")

# Your complete profitability analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive profitability and cost analysis",
    "description": "End-to-end profitability analysis with margin optimization, cost structure analysis, and financial efficiency assessment",
    "outputs": ["profitability_analysis_report.txt", "cost_optimization_opportunities.csv", "profit_margins_dashboard.png", "cost_structure_analysis.png", "profitability_trends.png", "unit_economics.png", "roi_analysis.png"],
    "insights": "Key profitability insights, cost optimization opportunities, and actionable financial recommendations for margin improvement and operational efficiency"
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
        
        # Check for profitability-related keywords
        primary_keywords = ["profit", "profitability", "margin", "cost"]
        secondary_keywords = ["efficiency", "economics", "roi", "revenue", "expense"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.4 + secondary_matches * 0.15), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for revenue columns
        revenue_indicators = ['revenue', 'sales', 'income', 'earnings']
        has_revenue = any(indicator in ' '.join(column_names_lower) for indicator in revenue_indicators)
        
        # Look for cost columns
        cost_indicators = ['cost', 'expense', 'spend', 'cogs', 'expenditure']
        has_cost = any(indicator in ' '.join(column_names_lower) for indicator in cost_indicators)
        
        if has_revenue and has_cost:
            column_score = 0.8
        elif has_revenue or has_cost:
            column_score = 0.4
        
        # Combined confidence score
        confidence = (keyword_score * 0.6) + (column_score * 0.4)
        
        return min(confidence, 1.0)
