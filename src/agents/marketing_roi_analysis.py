"""
Marketing ROI & Attribution Agent
Analyzes marketing effectiveness and optimizes campaign performance
"""

from typing import Dict, Any, List


class MarketingRoiAnalysisAgent:
    """Agent for marketing ROI analysis and attribution modeling"""
    
    def __init__(self):
        self.name = "marketing_roi_analysis"
        self.display_name = "Marketing ROI & Attribution"
        self.description = "Analyzes marketing campaign effectiveness, attribution modeling, and ROI optimization across channels and touchpoints"
        self.specialties = [
            "campaign roi analysis",
            "attribution modeling",
            "channel effectiveness",
            "marketing mix optimization",
            "conversion funnel analysis",
            "customer acquisition cost"
        ]
        self.keywords = [
            "marketing", "roi", "attribution", "campaign", "conversion",
            "acquisition cost", "roas", "channel", "touchpoint", "cac"
        ]
        self.required_columns = ["campaign_id"]
        self.output_type = "marketing_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for marketing ROI analysis"""
        
        return f"""
You are an expert marketing analyst specializing in campaign performance optimization and attribution modeling.

**Task: Comprehensive Marketing ROI & Attribution Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive marketing ROI and attribution analysis including:

1. **Campaign Performance Analysis:**
   - ROI and ROAS calculations by campaign
   - Cost per acquisition (CPA) and customer acquisition cost (CAC)
   - Conversion rate analysis by campaign and channel
   - Campaign effectiveness rankings and comparisons

2. **Attribution Modeling:**
   - First-touch and last-touch attribution analysis
   - Multi-touch attribution modeling
   - Channel contribution analysis
   - Cross-channel interaction effects

3. **Channel Effectiveness:**
   - Performance comparison across marketing channels
   - Channel-specific conversion rates and costs
   - Optimal budget allocation recommendations
   - Channel saturation point analysis

4. **Customer Journey Analysis:**
   - Marketing touchpoint sequence analysis
   - Path to conversion optimization
   - Drop-off point identification in marketing funnel
   - Customer lifetime value by acquisition channel

5. **Marketing Mix Optimization:**
   - Budget allocation optimization models
   - Channel mix effectiveness analysis
   - Incremental impact of marketing spend
   - Marketing efficiency frontier analysis

6. **Performance Forecasting:**
   - Future campaign performance predictions
   - Seasonal marketing trend analysis
   - Budget requirement forecasting
   - Growth projection scenarios

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Generate marketing performance dashboard visualizations
- Create comprehensive marketing report as 'marketing_roi_report.txt'
- Export optimization recommendations as 'marketing_optimization.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# Set marketing-focused visualization style
plt.style.use('default')
sns.set_palette("Set2")

# Your complete marketing ROI analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive marketing ROI and attribution analysis",
    "description": "End-to-end marketing performance analysis with ROI optimization, attribution modeling, and channel effectiveness",
    "outputs": ["marketing_roi_report.txt", "marketing_optimization.csv", "campaign_performance.png", "channel_attribution.png", "roi_dashboard.png", "customer_journey.png", "budget_optimization.png"],
    "insights": "Key marketing performance insights, channel effectiveness analysis, and data-driven budget optimization recommendations with projected ROI improvements"
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
        
        # Check for marketing-related keywords with weighted importance
        primary_keywords = ["marketing", "roi", "campaign", "attribution"]
        secondary_keywords = ["roas", "channel", "conversion", "touchpoint", "cac", "acquisition"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.4 + secondary_matches * 0.15), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for campaign/marketing columns
        campaign_indicators = ['campaign', 'channel', 'source', 'medium', 'utm', 'ad']
        has_campaign = any(indicator in ' '.join(column_names_lower) for indicator in campaign_indicators)
        
        if has_campaign:
            column_score += 0.5
        
        # Look for conversion/revenue columns
        conversion_indicators = ['conversion', 'revenue', 'cost', 'spend', 'budget', 'sales']
        has_conversion = any(indicator in ' '.join(column_names_lower) for indicator in conversion_indicators)
        
        if has_conversion:
            column_score += 0.3
        
        # Look for customer journey columns
        journey_indicators = ['touchpoint', 'interaction', 'visit', 'click', 'impression']
        has_journey = any(indicator in ' '.join(column_names_lower) for indicator in journey_indicators)
        
        if has_journey:
            column_score += 0.2
        
        # Combined confidence score
        confidence = (keyword_score * 0.7) + (column_score * 0.3)
        
        return min(confidence, 1.0)
