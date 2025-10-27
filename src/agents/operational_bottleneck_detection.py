"""
Operational Bottleneck Detection Agent
Identify process inefficiencies and optimization opportunities for small business operations
"""

from typing import Dict, Any, List


class OperationalBottleneckDetectionAgent:
    """Agent for operational bottleneck detection and process optimization"""
    
    def __init__(self):
        self.name = "operational_bottleneck_detection"
        self.display_name = "Operational Bottleneck Detection"
        self.description = "Identify operational bottlenecks, analyze process inefficiencies, and provide optimization recommendations for small business operations"
        self.specialties = [
            "process bottleneck identification",
            "workflow optimization",
            "capacity utilization analysis", 
            "throughput optimization",
            "resource allocation efficiency",
            "operational performance metrics"
        ]
        self.keywords = [
            "bottleneck", "process", "efficiency", "workflow", "throughput",
            "capacity", "utilization", "operations", "optimization", "performance"
        ]
        self.required_columns = ["process_time"]
        self.output_type = "bottleneck_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for operational bottleneck detection"""
        
        return f"""
You are an expert operations consultant specializing in process optimization and efficiency improvement for small and medium businesses.

**Task: Comprehensive Operational Bottleneck Detection & Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform SMB-focused operational analysis including:

1. **Process Flow Analysis:**
   - Process step timing and duration analysis
   - Workflow sequence optimization
   - Process variance and consistency measurement
   - Critical path identification

2. **Bottleneck Identification:**
   - Constraint theory (Theory of Constraints) application
   - Queue time and wait time analysis
   - Resource utilization bottleneck detection
   - Capacity constraint identification

3. **Throughput Optimization:**
   - Production rate analysis and optimization
   - Cycle time reduction opportunities
   - Batch size optimization
   - Parallel processing opportunities

4. **Resource Utilization Analysis:**
   - Equipment and resource efficiency metrics
   - Idle time and downtime analysis
   - Resource allocation optimization
   - Multi-resource coordination analysis

5. **Performance Metrics & KPIs:**
   - Overall Equipment Effectiveness (OEE)
   - Process efficiency ratios
   - Quality and rework impact analysis
   - Cost per unit/transaction analysis

6. **SMB Operational Improvements:**
   - Low-cost optimization recommendations
   - Process automation opportunities
   - Workflow redesign suggestions
   - Resource reallocation strategies

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Focus on actionable SMB operational insights
- Create operational efficiency dashboard visualizations
- Generate comprehensive report as 'bottleneck_analysis_report.txt'
- Export optimization recommendations as 'process_optimization.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set operational analysis visualization style
plt.style.use('default')
sns.set_palette("plasma")

# Your complete operational bottleneck detection code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for SMB operational bottleneck detection and analysis",
    "description": "Comprehensive operational efficiency analysis with bottleneck identification, process optimization, and throughput improvement recommendations for small businesses",
    "outputs": ["bottleneck_analysis_report.txt", "process_optimization.csv", "operations_dashboard.png", "bottleneck_analysis.png", "process_flow.png", "utilization_metrics.png", "throughput_analysis.png"],
    "insights": "Operational bottleneck identification, process efficiency opportunities, resource optimization recommendations, and throughput improvement strategies for small business operations"
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
        
        # Check for operational/process keywords
        primary_keywords = ["bottleneck", "process", "efficiency", "operations"]
        secondary_keywords = ["workflow", "throughput", "capacity", "utilization", "optimization"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.5 + secondary_matches * 0.2), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for process timing indicators
        timing_indicators = ['time', 'duration', 'cycle_time', 'processing_time', 'wait_time']
        has_timing = any(indicator in ' '.join(column_names_lower) for indicator in timing_indicators)
        
        # Look for process/operational indicators
        process_indicators = ['process', 'step', 'stage', 'operation', 'task', 'activity']
        has_process = any(indicator in ' '.join(column_names_lower) for indicator in process_indicators)
        
        # Look for resource/capacity indicators
        resource_indicators = ['resource', 'capacity', 'utilization', 'equipment', 'machine']
        has_resource = any(indicator in ' '.join(column_names_lower) for indicator in resource_indicators)
        
        if has_timing:
            column_score += 0.5
        if has_process:
            column_score += 0.3
        if has_resource:
            column_score += 0.2
        
        # Combined confidence score
        confidence = (keyword_score * 0.7) + (column_score * 0.3)
        
        return min(confidence, 1.0)
