"""
Business Intelligence Dashboard Agent
Executive-ready visualizations and KPI dashboards for strategic decision making
"""

from typing import Dict, Any, List


class BusinessIntelligenceDashboardAgent:
    """Agent for creating executive business intelligence dashboards"""
    
    def __init__(self):
        self.name = "business_intelligence_dashboard"
        self.display_name = "Business Intelligence Dashboard"
        self.description = "Creates executive-ready visualizations and KPI dashboards for business decision makers and stakeholders"
        self.specialties = [
            "kpi visualization",
            "executive dashboards",
            "business metrics",
            "performance tracking",
            "trend visualization",
            "comparative analysis"
        ]
        self.keywords = [
            "dashboard", "kpi", "business intelligence", "executive",
            "metrics", "performance", "tracking", "visualization", "bi"
        ]
        self.required_columns = []  # Works with any dataset
        self.output_type = "dashboard_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for business intelligence dashboard"""
        
        return f"""
You are an expert business intelligence analyst specializing in creating executive-level dashboards and strategic visualizations.

**Task: Executive Business Intelligence Dashboard Creation**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to create comprehensive business intelligence dashboards including:

1. **Key Performance Indicator (KPI) Metrics:**
   - Identify and calculate critical business KPIs
   - Revenue, growth, efficiency, and profitability metrics
   - Customer acquisition and retention indicators
   - Operational performance measurements

2. **Executive Summary Visualizations:**
   - High-level performance overview cards
   - Trend indicators with directional arrows
   - Goal vs actual progress bars
   - Performance scorecards with traffic light systems

3. **Comparative Analysis Charts:**
   - Year-over-year and period-over-period comparisons
   - Benchmark vs actual performance
   - Segment performance comparisons
   - Geographic or categorical breakdowns

4. **Trend and Forecasting Visuals:**
   - Time series trend analysis with projections
   - Seasonal pattern identification
   - Moving averages and trend lines
   - Performance trajectory visualization

5. **Drill-down Capabilities:**
   - Multi-level data exploration views
   - Detailed breakdowns by dimensions
   - Interactive filtering and segmentation
   - Root cause analysis visualizations

6. **Business Insight Narratives:**
   - Data-driven story telling
   - Key findings and implications
   - Actionable recommendations
   - Strategic decision support insights

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Create publication-ready, executive-quality visualizations
- Generate comprehensive dashboard report as 'business_intelligence_report.txt'
- Export key metrics summary as 'kpi_summary.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set professional BI visualization style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

# Your complete business intelligence dashboard code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for executive business intelligence dashboard creation",
    "description": "Executive-ready business intelligence dashboard with KPIs, trend analysis, and strategic insights for decision makers",
    "outputs": ["business_intelligence_report.txt", "kpi_summary.csv", "executive_dashboard.png", "kpi_scorecard.png", "trend_analysis.png", "comparative_analysis.png", "performance_metrics.png"],
    "insights": "Strategic business insights, key performance trends, and executive recommendations for data-driven decision making"
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
        
        # Check for dashboard/BI keywords
        primary_keywords = ["dashboard", "kpi", "business intelligence", "executive"]
        secondary_keywords = ["metrics", "performance", "tracking", "visualization", "bi"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.5 + secondary_matches * 0.15), 1.0)
        
        # This agent is valuable for executive reporting needs
        base_confidence = 0.3
        
        # Higher confidence for explicit dashboard requests
        dashboard_phrases = ['create dashboard', 'build dashboard', 'executive report', 'business intelligence', 'kpi dashboard']
        if any(phrase in question_lower for phrase in dashboard_phrases):
            base_confidence = 0.9
        
        # Look for business metrics data
        business_indicators = ['revenue', 'sales', 'profit', 'customer', 'performance', 'growth']
        column_names_lower = [col.lower() for col in data_columns]
        has_business_data = any(indicator in ' '.join(column_names_lower) for indicator in business_indicators)
        
        if has_business_data:
            base_confidence = max(base_confidence, 0.5)
        
        # Combined confidence score
        confidence = max(keyword_score, base_confidence)
        
        return min(confidence, 1.0)
