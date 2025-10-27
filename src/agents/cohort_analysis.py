"""
Customer Cohort Analysis Agent
Tracks customer behavior and retention patterns over time by acquisition cohorts
"""

from typing import Dict, Any, List


class CohortAnalysisAgent:
    """Agent for customer cohort analysis and retention tracking"""
    
    def __init__(self):
        self.name = "cohort_analysis"
        self.display_name = "Customer Cohort Analysis"
        self.description = "Tracks customer behavior and retention patterns over time by acquisition cohorts to understand customer lifecycle dynamics"
        self.specialties = [
            "cohort retention analysis",
            "customer lifecycle tracking",
            "acquisition cohort comparison",
            "ltv cohort analysis",
            "behavioral trend analysis", 
            "churn pattern identification"
        ]
        self.keywords = [
            "cohort", "retention", "lifecycle", "acquisition",
            "customer behavior", "longitudinal", "timeline", "period"
        ]
        self.required_columns = ["customer_id", "date"]
        self.output_type = "cohort_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for cohort analysis"""
        
        return f"""
You are an expert customer analytics specialist focusing on cohort analysis and customer lifecycle management.

**Task: Comprehensive Customer Cohort Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive cohort analysis including:

1. **Cohort Definition & Setup:**
   - Identify customer acquisition periods (monthly/quarterly cohorts)
   - Define cohort membership based on first activity/purchase date
   - Validate data completeness for cohort analysis
   - Handle timezone and date formatting issues

2. **Retention Cohort Analysis:**
   - Calculate month-over-month retention rates by cohort
   - Generate cohort retention matrices and heatmaps
   - Identify retention patterns across different acquisition periods
   - Analyze retention curve shapes and decay patterns

3. **Revenue Cohort Analysis:**
   - Track revenue per cohort over time
   - Calculate customer lifetime value (CLV) by cohort
   - Analyze revenue retention and expansion patterns
   - Identify high-value vs low-value acquisition periods

4. **Behavioral Cohort Insights:**
   - Activity level analysis by cohort and time period
   - Engagement pattern evolution over customer lifecycle
   - Product usage patterns by acquisition cohort
   - Cross-cohort behavioral comparison analysis

5. **Cohort Performance Benchmarking:**
   - Compare cohort performance across different metrics
   - Identify best and worst performing acquisition periods
   - Seasonal cohort performance analysis
   - External factor impact on cohort behavior

6. **Predictive Cohort Modeling:**
   - Forecast future cohort behavior based on historical patterns
   - Predict customer lifetime value for recent cohorts
   - Early warning indicators for cohort underperformance
   - Cohort maturity curve modeling

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Generate comprehensive cohort visualization suite
- Create detailed cohort analysis report as 'cohort_analysis_report.txt'
- Export cohort matrices as 'cohort_retention_data.csv' and 'cohort_revenue_data.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set cohort analysis visualization style
plt.style.use('default')
sns.set_palette("RdYlBu_r")

# Your complete cohort analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive customer cohort analysis",
    "description": "Customer lifecycle tracking with retention analysis, revenue cohorts, and behavioral pattern identification across acquisition periods",
    "outputs": ["cohort_analysis_report.txt", "cohort_retention_data.csv", "cohort_revenue_data.csv", "retention_heatmap.png", "revenue_cohorts.png", "cohort_comparison.png", "lifecycle_curves.png", "cohort_dashboard.png"],
    "insights": "Customer retention patterns, cohort performance insights, acquisition period effectiveness, and strategic recommendations for customer lifecycle optimization"
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
        
        # Check for cohort-related keywords
        primary_keywords = ["cohort", "retention", "lifecycle", "acquisition"]
        secondary_keywords = ["longitudinal", "timeline", "period", "customer behavior"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.5 + secondary_matches * 0.2), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for customer ID column
        customer_id_indicators = ['customer_id', 'customer', 'user_id', 'account_id', 'client_id']
        has_customer_id = any(indicator in ' '.join(column_names_lower) for indicator in customer_id_indicators)
        
        # Look for date columns
        date_indicators = ['date', 'time', 'created', 'purchase', 'signup', 'acquisition']
        has_date = any(indicator in ' '.join(column_names_lower) for indicator in date_indicators)
        
        if has_customer_id and has_date:
            column_score = 0.8
        elif has_customer_id or has_date:
            column_score = 0.4
        
        # Combined confidence score
        confidence = (keyword_score * 0.6) + (column_score * 0.4)
        
        return min(confidence, 1.0)
