"""
Customer Acquisition Cost Analysis Agent
Optimize marketing spend and customer acquisition for small business growth
"""

from typing import Dict, Any, List


class CustomerAcquisitionCostAnalysisAgent:
    """Agent for customer acquisition cost optimization and marketing ROI analysis"""
    
    def __init__(self):
        self.name = "customer_acquisition_cost_analysis"
        self.display_name = "Customer Acquisition Cost Analysis"
        self.description = "Analyze customer acquisition costs, optimize marketing spend efficiency, and maximize customer lifetime value for small business growth"
        self.specialties = [
            "customer acquisition cost optimization",
            "marketing channel roi analysis",
            "customer lifetime value calculation", 
            "payback period analysis",
            "marketing spend efficiency",
            "acquisition funnel optimization"
        ]
        self.keywords = [
            "customer acquisition", "cac", "marketing cost", "acquisition cost",
            "customer lifetime value", "clv", "marketing roi", "acquisition channel"
        ]
        self.required_columns = ["marketing_cost", "customers_acquired"]
        self.output_type = "cac_analysis_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for customer acquisition cost analysis"""
        
        return f"""
You are an expert marketing analyst specializing in customer acquisition optimization and growth strategies for small and medium businesses.

**Task: Comprehensive Customer Acquisition Cost Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform SMB-focused customer acquisition analysis including:

1. **Customer Acquisition Cost (CAC) Analysis:**
   - CAC calculation by channel and campaign
   - CAC trend analysis over time
   - Blended vs. paid CAC analysis
   - Channel-specific CAC optimization

2. **Customer Lifetime Value (CLV) Optimization:**
   - CLV calculation and segmentation
   - CLV to CAC ratio analysis (LTV:CAC)
   - Payback period calculations
   - Revenue per customer analysis

3. **Marketing Channel Efficiency:**
   - Channel performance comparison
   - Cost per lead (CPL) analysis
   - Conversion rate optimization
   - Attribution modeling for multi-touch journeys

4. **Acquisition Funnel Analysis:**
   - Lead-to-customer conversion rates
   - Funnel stage cost analysis
   - Drop-off point identification
   - Conversion optimization opportunities

5. **Budget Allocation Optimization:**
   - Optimal marketing spend distribution
   - Channel budget reallocation recommendations
   - ROI-based budget planning
   - Seasonal acquisition budget planning

6. **SMB Growth Strategies:**
   - Low-cost acquisition channel identification
   - Referral program optimization
   - Organic growth opportunity assessment
   - Customer acquisition scaling strategies

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Focus on actionable SMB marketing insights
- Create customer acquisition dashboard visualizations
- Generate comprehensive report as 'cac_analysis_report.txt'
- Export channel recommendations as 'marketing_optimization.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set CAC analysis visualization style
plt.style.use('default')
sns.set_palette("rocket")

# Your complete customer acquisition cost analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for SMB customer acquisition cost analysis",
    "description": "Comprehensive customer acquisition cost optimization with marketing ROI analysis and growth strategy recommendations for small businesses",
    "outputs": ["cac_analysis_report.txt", "marketing_optimization.csv", "cac_dashboard.png", "channel_efficiency.png", "clv_analysis.png", "acquisition_funnel.png", "budget_allocation.png"],
    "insights": "Customer acquisition cost insights, marketing channel efficiency, CLV optimization opportunities, and budget allocation recommendations for small business growth"
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
        
        # Check for CAC/acquisition keywords
        primary_keywords = ["customer acquisition", "cac", "acquisition cost", "marketing cost"]
        secondary_keywords = ["clv", "lifetime value", "marketing roi", "channel", "funnel"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.6 + secondary_matches * 0.2), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for marketing cost indicators
        cost_indicators = ['cost', 'spend', 'budget', 'investment', 'marketing_cost', 'ad_spend']
        has_cost = any(indicator in ' '.join(column_names_lower) for indicator in cost_indicators)
        
        # Look for customer acquisition indicators
        acquisition_indicators = ['customers', 'leads', 'conversions', 'signups', 'acquisitions']
        has_acquisition = any(indicator in ' '.join(column_names_lower) for indicator in acquisition_indicators)
        
        # Look for channel/campaign indicators
        channel_indicators = ['channel', 'campaign', 'source', 'medium', 'utm']
        has_channel = any(indicator in ' '.join(column_names_lower) for indicator in channel_indicators)
        
        if has_cost and has_acquisition:
            column_score += 0.6
        elif has_cost or has_acquisition:
            column_score += 0.3
        
        if has_channel:
            column_score += 0.2
        
        # Combined confidence score
        confidence = (keyword_score * 0.7) + (column_score * 0.3)
        
        return min(confidence, 1.0)
