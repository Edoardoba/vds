"""
Exploratory Data Analysis Agent
Deep dive exploration to understand data patterns and generate business insights
"""

from typing import Dict, Any, List


class ExploratoryDataAnalysisAgent:
    """Agent for comprehensive exploratory data analysis and pattern discovery"""
    
    def __init__(self):
        self.name = "exploratory_data_analysis"
        self.display_name = "Exploratory Data Analysis"
        self.description = "Deep dive exploration of datasets to understand structure, patterns, relationships, and generate actionable business insights"
        self.specialties = [
            "data distribution analysis",
            "correlation discovery",
            "pattern identification", 
            "business insight generation",
            "statistical summaries",
            "data storytelling"
        ]
        self.keywords = [
            "explore", "eda", "patterns", "insights", "distribution",
            "relationships", "understand", "analyze", "overview", "summary"
        ]
        self.required_columns = []  # Works with any dataset
        self.output_type = "exploration_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for exploratory data analysis"""
        
        return f"""
You are an expert data analyst specializing in exploratory data analysis and business insight generation.

**Task: Comprehensive Exploratory Data Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Missing values: {data_sample['missing_values']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive exploratory data analysis including:

1. **Data Structure & Overview:**
   - Comprehensive dataset summary with key statistics
   - Data type analysis and memory usage optimization
   - Missing data patterns and impact assessment
   - Basic data quality indicators

2. **Univariate Analysis:**
   - Distribution analysis for numerical variables (histograms, box plots, QQ plots)
   - Frequency analysis for categorical variables
   - Outlier detection and characterization
   - Central tendency and variability measures

3. **Bivariate & Multivariate Analysis:**
   - Correlation matrix with heatmap visualization
   - Scatter plot matrix for numerical relationships
   - Cross-tabulation analysis for categorical relationships
   - Feature interaction identification

4. **Pattern Discovery:**
   - Time series patterns (if temporal data exists)
   - Seasonal and trend analysis
   - Segmentation patterns and clusters
   - Anomaly and unusual pattern detection

5. **Business Insight Generation:**
   - Key findings and patterns with business implications
   - Actionable insights for decision making
   - Data-driven recommendations
   - Hypothesis generation for further analysis

6. **Advanced Visualizations:**
   - Interactive and publication-ready charts
   - Multi-dimensional visualizations
   - Business dashboard elements
   - Story-driven visual narratives

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Create comprehensive visualization suite as PNG files
- Generate executive summary as 'eda_insights_report.txt'
- Export key findings as 'key_findings.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

# Set style for professional visualizations
plt.style.use('default')
sns.set_palette("husl")

# Your complete exploratory data analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive exploratory data analysis",
    "description": "Deep dive exploratory analysis with pattern discovery, correlation analysis, and actionable business insights",
    "outputs": ["eda_insights_report.txt", "key_findings.csv", "data_overview.png", "correlation_matrix.png", "distribution_analysis.png", "pattern_discovery.png", "business_insights.png"],
    "insights": "Key patterns, relationships, and actionable business insights discovered through comprehensive exploratory analysis"
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
        
        # Check for EDA-related keywords with weighted importance
        primary_keywords = ["explore", "eda", "understand", "analyze", "overview"]
        secondary_keywords = ["patterns", "insights", "distribution", "relationships", "summary"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.35 + secondary_matches * 0.15), 1.0)
        
        # This agent is valuable for most data analysis requests
        base_confidence = 0.5
        
        # Higher confidence for explicit exploration requests
        exploration_phrases = ['explore data', 'data analysis', 'understand data', 'analyze dataset', 'data insights']
        if any(phrase in question_lower for phrase in exploration_phrases):
            base_confidence = 0.85
        
        # Boost for general analysis requests
        general_analysis = ['analysis', 'investigate', 'examine', 'study']
        if any(word in question_lower for word in general_analysis):
            base_confidence = max(base_confidence, 0.6)
        
        # Combined confidence score
        confidence = max(keyword_score, base_confidence)
        
        return min(confidence, 1.0)
