"""
Employee Performance Analysis Agent
Workforce productivity and performance optimization for small business teams
"""

from typing import Dict, Any, List


class EmployeePerformanceAnalysisAgent:
    """Agent for employee performance analysis and productivity optimization"""
    
    def __init__(self):
        self.name = "employee_performance_analysis"
        self.display_name = "Employee Performance Analysis"
        self.description = "Analyze workforce productivity, identify top performers, track performance trends, and optimize team efficiency for small businesses"
        self.specialties = [
            "productivity analysis",
            "performance benchmarking",
            "team efficiency optimization",
            "top performer identification", 
            "training needs assessment",
            "workforce analytics"
        ]
        self.keywords = [
            "employee", "performance", "productivity", "workforce", 
            "team", "efficiency", "staff", "worker", "hr", "human resources"
        ]
        self.required_columns = ["employee_id"]
        self.output_type = "performance_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for employee performance analysis"""
        
        return f"""
You are an expert HR analyst specializing in workforce performance optimization for small and medium businesses.

**Task: Comprehensive Employee Performance Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform SMB-focused workforce analysis including:

1. **Individual Performance Analysis:**
   - Employee productivity metrics calculation
   - Performance trend analysis over time
   - Goal achievement rates and KPI tracking
   - Individual contribution to team success

2. **Team Performance Benchmarking:**
   - Top performer identification and characteristics
   - Performance distribution analysis
   - Peer comparison and ranking systems
   - Department/role-based performance comparison

3. **Productivity Optimization:**
   - Efficiency metric calculations
   - Time allocation and utilization analysis
   - Task completion rates and quality metrics
   - Resource utilization per employee

4. **Performance Trend Analysis:**
   - Historical performance patterns
   - Seasonal productivity variations
   - Performance improvement/decline identification
   - Learning curve and skill development tracking

5. **Training & Development Insights:**
   - Skills gap identification
   - Training ROI analysis
   - Development opportunity prioritization
   - Performance correlation with training

6. **SMB Workforce Strategies:**
   - Retention risk assessment
   - Succession planning insights
   - Compensation optimization recommendations
   - Team structure optimization

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Focus on actionable SMB workforce insights
- Create performance dashboard visualizations
- Generate comprehensive report as 'employee_performance_report.txt'
- Export performance rankings as 'employee_rankings.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set performance analysis visualization style
plt.style.use('default')
sns.set_palette("viridis")

# Your complete employee performance analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for SMB employee performance analysis",
    "description": "Comprehensive workforce performance analysis with productivity optimization and team efficiency insights for small businesses",
    "outputs": ["employee_performance_report.txt", "employee_rankings.csv", "performance_dashboard.png", "productivity_trends.png", "team_comparison.png", "training_needs.png", "retention_risk.png"],
    "insights": "Employee performance insights, top performer characteristics, productivity optimization opportunities, and workforce development recommendations for small business teams"
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
        
        # Check for employee/performance keywords
        primary_keywords = ["employee", "performance", "productivity", "workforce"]
        secondary_keywords = ["team", "efficiency", "staff", "worker", "hr", "human resources"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.5 + secondary_matches * 0.2), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for employee identifiers
        employee_indicators = ['employee', 'staff', 'worker', 'user_id', 'person', 'team_member']
        has_employee = any(indicator in ' '.join(column_names_lower) for indicator in employee_indicators)
        
        # Look for performance metrics
        performance_indicators = ['performance', 'productivity', 'score', 'rating', 'kpi', 'target', 'goal']
        has_performance = any(indicator in ' '.join(column_names_lower) for indicator in performance_indicators)
        
        if has_employee:
            column_score += 0.6
        if has_performance:
            column_score += 0.4
        
        # Combined confidence score
        confidence = (keyword_score * 0.7) + (column_score * 0.3)
        
        return min(confidence, 1.0)
