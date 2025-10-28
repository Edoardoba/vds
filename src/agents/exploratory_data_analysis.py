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
        """Generate intelligent, context-aware prompt for exploratory data analysis"""
        
        # Analyze dataset characteristics
        columns = data_sample['columns']
        data_types = data_sample['data_types']
        total_rows = data_sample['total_rows']
        missing_values = data_sample['missing_values']
        
        # Detect data characteristics
        numerical_cols = [col for col, dtype in data_types.items() if dtype in ['int64', 'float64', 'int32', 'float32']]
        categorical_cols = [col for col, dtype in data_types.items() if dtype in ['object', 'category', 'bool']]
        datetime_cols = [col for col, dtype in data_types.items() if dtype in ['datetime64[ns]', 'datetime64']]
        
        # Analyze user intent
        question_lower = user_question.lower()
        
        # Determine analysis focus based on user request
        analysis_focus = self._determine_analysis_focus(question_lower, columns, data_types)
        
        # Determine appropriate techniques based on data characteristics
        techniques = self._select_analysis_techniques(analysis_focus, numerical_cols, categorical_cols, datetime_cols, total_rows)
        
        return f"""
You are an expert data analyst specializing in intelligent exploratory data analysis that adapts to specific user needs and dataset characteristics.

**Task: Context-Aware Exploratory Data Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {total_rows:,}
- Available columns: {', '.join(columns)}
- Data types: {data_types}
- Missing values: {missing_values}
- Sample data: {data_sample['sample_data'][:3]}

**Data Characteristics Detected:**
- Numerical columns ({len(numerical_cols)}): {', '.join(numerical_cols[:5])}{'...' if len(numerical_cols) > 5 else ''}
- Categorical columns ({len(categorical_cols)}): {', '.join(categorical_cols[:5])}{'...' if len(categorical_cols) > 5 else ''}
- Datetime columns ({len(datetime_cols)}): {', '.join(datetime_cols)}

**User Request:** "{user_question}"

**Analysis Focus:** {analysis_focus['focus']}
**Primary Objectives:** {', '.join(analysis_focus['objectives'])}

**Your mission:**
Generate focused, production-ready Python code that performs ONLY the most relevant exploratory analysis for this specific request and dataset. Focus on:

{self._build_technique_instructions(techniques)}

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Generate ONLY relevant analysis based on user request and data characteristics
- Save outputs to current directory
- Create targeted visualizations as PNG files
- Generate focused insights report as 'eda_insights_report.txt'
- Export key findings as 'key_findings.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style for professional visualizations
plt.style.use('default')
sns.set_palette("husl")

# Your focused exploratory data analysis code here...
# Focus on: {analysis_focus['focus']}
# Key techniques: {', '.join(techniques['primary'])}
```

Respond with ONLY a JSON object:
{{
    "code": "focused Python code for targeted exploratory data analysis",
    "description": "{analysis_focus['description']}",
    "insights": "Key findings and actionable insights specific to the user's request and dataset characteristics"
}}
"""

    def _determine_analysis_focus(self, question_lower: str, columns: List[str], data_types: Dict[str, str]) -> Dict[str, Any]:
        """Determine the analysis focus based on user request and data characteristics"""
        
        # Detect user intent patterns
        if any(word in question_lower for word in ['correlation', 'relationship', 'related', 'associate']):
            return {
                'focus': 'Relationship Analysis',
                'objectives': ['Identify correlations between variables', 'Discover hidden relationships', 'Understand variable interactions'],
                'description': 'Focused correlation and relationship analysis to understand variable interactions'
            }
        
        elif any(word in question_lower for word in ['pattern', 'trend', 'seasonal', 'time', 'temporal']):
            return {
                'focus': 'Pattern Discovery',
                'objectives': ['Identify temporal patterns', 'Detect trends and seasonality', 'Find recurring patterns'],
                'description': 'Pattern discovery analysis focusing on trends, seasonality, and recurring behaviors'
            }
        
        elif any(word in question_lower for word in ['distribution', 'spread', 'outlier', 'skew', 'normal']):
            return {
                'focus': 'Distribution Analysis',
                'objectives': ['Analyze data distributions', 'Identify outliers and anomalies', 'Understand data spread'],
                'description': 'Distribution-focused analysis examining data spread, outliers, and statistical properties'
            }
        
        elif any(word in question_lower for word in ['segment', 'group', 'cluster', 'category', 'classification']):
            return {
                'focus': 'Segmentation Analysis',
                'objectives': ['Identify natural groupings', 'Discover customer segments', 'Understand categorical patterns'],
                'description': 'Segmentation analysis to identify natural groupings and categorical patterns'
            }
        
        elif any(word in question_lower for word in ['summary', 'overview', 'describe', 'understand', 'explore']):
            return {
                'focus': 'Comprehensive Overview',
                'objectives': ['Provide data summary', 'Generate key insights', 'Create executive overview'],
                'description': 'Comprehensive exploratory analysis providing data overview and key business insights'
            }
        
        else:
            return {
                'focus': 'Adaptive Analysis',
                'objectives': ['Analyze based on data characteristics', 'Generate relevant insights', 'Provide actionable findings'],
                'description': 'Adaptive exploratory analysis tailored to dataset characteristics and user context'
            }

    def _select_analysis_techniques(self, analysis_focus: Dict[str, Any], numerical_cols: List[str], 
                                  categorical_cols: List[str], datetime_cols: List[str], total_rows: int) -> Dict[str, List[str]]:
        """Select appropriate analysis techniques based on focus and data characteristics"""
        
        techniques = {
            'primary': [],
            'secondary': [],
            'visualizations': []
        }
        
        focus = analysis_focus['focus']
        
        if focus == 'Relationship Analysis':
            techniques['primary'] = ['correlation_matrix', 'scatter_plots', 'cross_tabulation']
            techniques['secondary'] = ['feature_interactions', 'association_rules']
            techniques['visualizations'] = ['correlation_heatmap', 'scatter_matrix', 'pairplot']
        
        elif focus == 'Pattern Discovery':
            techniques['primary'] = ['time_series_decomposition', 'trend_analysis', 'seasonality_detection']
            techniques['secondary'] = ['autocorrelation', 'periodogram']
            techniques['visualizations'] = ['time_series_plot', 'seasonal_decomposition', 'trend_analysis']
        
        elif focus == 'Distribution Analysis':
            techniques['primary'] = ['distribution_analysis', 'outlier_detection', 'normality_tests']
            techniques['secondary'] = ['skewness_kurtosis', 'quantile_analysis']
            techniques['visualizations'] = ['histogram', 'box_plot', 'qq_plot', 'violin_plot']
        
        elif focus == 'Segmentation Analysis':
            techniques['primary'] = ['clustering_analysis', 'categorical_analysis', 'group_statistics']
            techniques['secondary'] = ['rfm_analysis', 'behavioral_segmentation']
            techniques['visualizations'] = ['cluster_plot', 'categorical_distribution', 'segment_comparison']
        
        else:  # Comprehensive Overview or Adaptive Analysis
            # Select techniques based on data characteristics
            if len(numerical_cols) > 0:
                techniques['primary'].append('descriptive_statistics')
                techniques['primary'].append('distribution_summary')
            if len(categorical_cols) > 0:
                techniques['primary'].append('categorical_summary')
            if len(datetime_cols) > 0:
                techniques['primary'].append('temporal_summary')
            if total_rows > 1000:
                techniques['secondary'].append('sampling_analysis')
        
        return techniques

    def _build_technique_instructions(self, techniques: Dict[str, List[str]]) -> str:
        """Build specific instructions for the selected techniques"""
        
        instructions = []
        
        for technique in techniques['primary']:
            if technique == 'correlation_matrix':
                instructions.append("• **Correlation Analysis**: Calculate correlation matrices and identify strong relationships")
            elif technique == 'distribution_analysis':
                instructions.append("• **Distribution Analysis**: Analyze data distributions, detect outliers, and assess normality")
            elif technique == 'time_series_decomposition':
                instructions.append("• **Time Series Analysis**: Decompose temporal patterns and identify trends/seasonality")
            elif technique == 'clustering_analysis':
                instructions.append("• **Clustering Analysis**: Identify natural groupings and segment patterns")
            elif technique == 'descriptive_statistics':
                instructions.append("• **Descriptive Statistics**: Generate comprehensive statistical summaries")
            elif technique == 'categorical_summary':
                instructions.append("• **Categorical Analysis**: Analyze categorical variable distributions and patterns")
        
        return '\n'.join(instructions) if instructions else "• **Adaptive Analysis**: Focus on the most relevant analysis based on data characteristics"

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
