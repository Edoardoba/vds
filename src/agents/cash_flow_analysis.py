"""
Cash Flow Analysis Agent
Critical cash flow monitoring and forecasting for small and medium businesses
"""

from typing import Dict, Any, List


class CashFlowAnalysisAgent:
    """Agent for cash flow analysis and liquidity management for SMBs"""
    
    def __init__(self):
        self.name = "cash_flow_analysis"
        self.display_name = "Cash Flow Analysis"
        self.description = "Monitor cash flow patterns, predict cash needs, and optimize working capital for small and medium businesses"
        self.specialties = [
            "cash flow forecasting",
            "working capital optimization", 
            "receivables analysis",
            "payables management",
            "liquidity planning",
            "cash flow gap analysis"
        ]
        self.keywords = [
            "cash flow", "receivables", "payables", "liquidity", 
            "working capital", "payment", "collection", "cash gap"
        ]
        self.required_columns = ["date", "amount"]
        self.output_type = "cash_flow_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for cash flow analysis"""
        
        return f"""
You are an expert financial analyst specializing in cash flow management for small and medium businesses.

**Task: Comprehensive Cash Flow Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform SMB-focused cash flow analysis including:

1. **Cash Flow Pattern Analysis:**
   - Daily, weekly, monthly cash flow trends
   - Seasonal cash flow patterns identification
   - Cash flow volatility assessment
   - Peak and trough period analysis

2. **Working Capital Management:**
   - Days sales outstanding (DSO) calculation
   - Days payable outstanding (DPO) analysis
   - Cash conversion cycle optimization
   - Working capital efficiency metrics

3. **Cash Flow Forecasting:**
   - Short-term (30/60/90 day) cash projections
   - Rolling cash flow forecasts
   - Scenario-based cash planning (best/worst/likely)
   - Seasonal adjustment factors

4. **Liquidity Risk Assessment:**
   - Cash runway calculations
   - Minimum cash threshold analysis
   - Cash gap identification and timing
   - Emergency fund requirements

5. **Collections & Payments Optimization:**
   - Receivables aging analysis
   - Payment timing optimization
   - Collection efficiency metrics
   - Supplier payment schedule analysis

6. **SMB-Specific Insights:**
   - Cash flow improvement recommendations
   - Working capital optimization strategies
   - Payment terms negotiation opportunities
   - Emergency cash planning guidelines

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Focus on actionable SMB insights
- Create cash flow dashboard visualizations
- Generate comprehensive report as 'cash_flow_analysis_report.txt'
- Export cash flow forecast as 'cash_flow_forecast.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set cash flow analysis visualization style
plt.style.use('default')
sns.set_palette("RdYlGn_r")

# Your complete cash flow analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for SMB cash flow analysis",
    "description": "Comprehensive cash flow management analysis with forecasting and working capital optimization for small businesses", 
    "outputs": ["cash_flow_analysis_report.txt", "cash_flow_forecast.csv", "cash_flow_dashboard.png", "working_capital_analysis.png", "cash_flow_trends.png", "liquidity_metrics.png", "collections_analysis.png"],
    "insights": "## Cash Flow Analysis - Chart Explanations\n\n### Cash Flow Dashboard\n- **What it shows**: Monthly cash inflows vs outflows with running balance\n- **Key findings**: Seasonal patterns, cash gaps, and peak/trough periods\n- **Business implications**: When to expect cash shortages and optimal timing for investments\n- **Action items**: Specific months to focus on collections or defer payments\n\n### Working Capital Analysis\n- **What it shows**: Days sales outstanding (DSO), days payable outstanding (DPO), and cash conversion cycle\n- **Key findings**: Efficiency of working capital management and comparison to industry benchmarks\n- **Business implications**: How quickly cash is tied up in operations vs. available for growth\n- **Action items**: Opportunities to negotiate better payment terms or improve collections\n\n### Cash Flow Trends\n- **What it shows**: Historical cash flow patterns and trend analysis\n- **Key findings**: Growth trends, volatility patterns, and seasonal adjustments needed\n- **Business implications**: Predictability of cash flows and planning horizon reliability\n- **Action items**: Recommendations for cash flow stabilization strategies\n\n### Liquidity Metrics\n- **What it shows**: Cash runway, minimum cash thresholds, and liquidity ratios\n- **Key findings**: How long current cash will last and safety margins\n- **Business implications**: Risk level and emergency fund requirements\n- **Action items**: Immediate steps needed to improve liquidity position"
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
        
        # Check for cash flow keywords
        primary_keywords = ["cash flow", "cash", "liquidity", "receivables", "payables"]
        secondary_keywords = ["working capital", "payment", "collection", "cash gap", "runway"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.5 + secondary_matches * 0.2), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for date columns
        date_indicators = ['date', 'time', 'period', 'month', 'day']
        has_date = any(indicator in ' '.join(column_names_lower) for indicator in date_indicators)
        
        # Look for amount/cash flow columns
        amount_indicators = ['amount', 'cash', 'payment', 'receipt', 'balance', 'flow']
        has_amount = any(indicator in ' '.join(column_names_lower) for indicator in amount_indicators)
        
        if has_date and has_amount:
            column_score = 0.8
        elif has_date or has_amount:
            column_score = 0.4
        
        # Combined confidence score
        confidence = (keyword_score * 0.6) + (column_score * 0.4)
        
        return min(confidence, 1.0)
