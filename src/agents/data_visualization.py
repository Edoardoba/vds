"""
Data Visualization & EDA Agent
Specializes in exploratory data analysis and creating insightful visualizations
"""

from typing import Dict, Any, List


class DataVisualizationAgent:
    """Agent for data visualization and exploratory data analysis"""
    
    def __init__(self):
        self.name = "data_visualization"
        self.display_name = "Data Visualization & EDA"
        self.description = "Creates comprehensive visualizations and performs exploratory data analysis to uncover patterns and insights"
        self.specialties = [
            "exploratory data analysis",
            "statistical visualization",
            "correlation analysis",
            "distribution analysis", 
            "trend identification"
        ]
        self.keywords = [
            "visualize", "plot", "chart", "graph", "explore",
            "eda", "correlation", "distribution", "trend", "pattern"
        ]
        self.required_columns = []  # Works with any dataset
        self.output_type = "visualization_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for data visualization"""
        
        return f"""
You are an expert data scientist specializing in exploratory data analysis and data visualization.

**Task: Data Visualization & Exploratory Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive exploratory data analysis including:

1. **Dataset Overview:**
   - Generate comprehensive data summary statistics
   - Create info dashboard showing data shape, types, missing values
   - Identify numerical vs categorical variables

2. **Distribution Analysis:**
   - Plot histograms for numerical variables
   - Create count plots for categorical variables  
   - Generate box plots to identify outliers
   - Show distribution normality tests

3. **Correlation Analysis:**
   - Create correlation matrix heatmap
   - Identify strong positive/negative correlations
   - Generate scatter plots for interesting relationships
   - Calculate and visualize correlation coefficients

4. **Pattern Discovery:**
   - Time series plots if date columns exist
   - Groupby analysis for categorical variables
   - Cross-tabulation analysis
   - Identify trends and seasonal patterns

5. **Advanced Visualizations:**
   - Pair plots for numerical variables
   - Violin plots for distribution comparison
   - Feature relationship analysis
   - Interactive-style static plots

6. **Chart Explanations & Business Insights:**
   - For each visualization created, provide detailed explanations of:
     * What the chart shows and why it's important
     * Key patterns, trends, or outliers visible in the chart
     * Business implications of the findings
     * Actionable recommendations based on the visual insights
   - Document key patterns discovered across all visualizations
   - Highlight unusual observations and their potential significance
   - Suggest areas for deeper analysis

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Create multiple high-quality visualizations
- Use professional styling and clear labels
- Save all plots as high-resolution PNG files
- Generate insights summary as 'eda_insights.txt'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style for professional plots
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Your complete EDA code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive EDA and visualization",
    "description": "Exploratory data analysis with statistical visualizations and pattern discovery",
    "outputs": ["eda_insights.txt", "data_overview.png", "correlation_matrix.png", "distributions.png", "relationships.png"],
    "insights": "## Chart Explanations & Key Insights\n\n### Data Overview Chart\n- **What it shows**: [Explain the overview visualization]\n- **Key findings**: [What patterns are visible]\n- **Business implications**: [What this means for the business]\n\n### Correlation Matrix\n- **What it shows**: [Explain the correlation heatmap]\n- **Key findings**: [Strong correlations discovered]\n- **Business implications**: [How to leverage these relationships]\n\n### Distribution Analysis\n- **What it shows**: [Explain the distribution charts]\n- **Key findings**: [Notable distribution patterns]\n- **Business implications**: [What the distributions suggest]\n\n### Additional Insights\n- [Overall patterns discovered]\n- [Unusual observations and their significance]\n- [Recommended next steps for analysis]"
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
        
        # Check for visualization-related keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in question_lower)
        keyword_score = min(keyword_matches / len(self.keywords), 1.0)
        
        # This agent is very commonly needed, so give good base confidence
        base_confidence = 0.4
        
        # Higher confidence if explicitly mentioned
        viz_terms = ['plot', 'chart', 'graph', 'visualiz', 'explore', 'eda']
        if any(term in question_lower for term in viz_terms):
            base_confidence = 0.9
        
        # Combined confidence score
        confidence = max(keyword_score, base_confidence)
        
        return confidence
