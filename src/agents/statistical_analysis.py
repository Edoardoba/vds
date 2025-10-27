"""
Statistical Analysis Agent
Specializes in statistical tests and hypothesis testing
"""

from typing import Dict, Any, List


class StatisticalAnalysisAgent:
    """Agent for statistical analysis and hypothesis testing"""
    
    def __init__(self):
        self.name = "statistical_analysis"
        self.display_name = "Statistical Analysis"
        self.description = "Conducts comprehensive statistical tests, hypothesis testing, and descriptive statistics analysis"
        self.specialties = [
            "descriptive statistics",
            "hypothesis testing",
            "t-tests",
            "chi-square tests", 
            "anova",
            "correlation analysis"
        ]
        self.keywords = [
            "statistics", "statistical", "test", "hypothesis",
            "significance", "p-value", "correlation", "mean", "median"
        ]
        self.required_columns = []  # Works with any numerical data
        self.output_type = "statistical_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for statistical analysis"""
        
        return f"""
You are an expert statistician specializing in statistical analysis and hypothesis testing.

**Task: Comprehensive Statistical Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive statistical analysis including:

1. **Descriptive Statistics:**
   - Calculate comprehensive summary statistics (mean, median, mode, std, skewness, kurtosis)
   - Generate frequency distributions for categorical variables
   - Create statistical summaries by groups/categories
   - Identify data distribution shapes and characteristics

2. **Distribution Analysis:**
   - Test for normality (Shapiro-Wilk, Kolmogorov-Smirnov)
   - Identify distribution types (normal, skewed, uniform, etc.)
   - Q-Q plots for normality assessment
   - Transformation recommendations for non-normal data

3. **Hypothesis Testing:**
   - One-sample t-tests for population means
   - Two-sample t-tests for group comparisons
   - Chi-square tests for categorical associations
   - ANOVA for multiple group comparisons
   - Correlation significance tests

4. **Advanced Statistical Tests:**
   - Mann-Whitney U test (non-parametric alternative)
   - Kruskal-Wallis test (non-parametric ANOVA)
   - Fisher's exact test for small samples
   - Levene's test for equal variances

5. **Effect Size Analysis:**
   - Cohen's d for t-tests
   - Eta-squared for ANOVA
   - Correlation coefficients (Pearson, Spearman)
   - Confidence intervals for effect sizes

6. **Statistical Insights:**
   - Interpret p-values and statistical significance
   - Assess practical significance vs statistical significance
   - Identify meaningful patterns and relationships
   - Provide recommendations based on statistical findings

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Handle different data types appropriately
- Save statistical results as 'statistical_results.csv'
- Create comprehensive statistical plots
- Generate detailed statistical report as 'statistical_report.txt'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import shapiro, kstest, ttest_1samp, ttest_ind, chi2_contingency, f_oneway
import warnings
warnings.filterwarnings('ignore')

# Your complete statistical analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive statistical analysis",
    "description": "Statistical tests, hypothesis testing, and descriptive statistics analysis",
    "outputs": ["statistical_results.csv", "statistical_report.txt", "distribution_analysis.png", "hypothesis_tests.png", "correlation_matrix.png"],
    "insights": "Key statistical findings, significant relationships, and hypothesis test results"
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
        
        # Check for statistical keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in question_lower)
        keyword_score = min(keyword_matches / len(self.keywords), 1.0)
        
        # This agent is commonly applicable, give decent base confidence
        base_confidence = 0.2
        
        # Higher confidence for explicit statistical terms
        stat_terms = ['statistic', 'test', 'hypothesis', 'significance', 'correlation', 'mean', 'average']
        if any(term in question_lower for term in stat_terms):
            base_confidence = 0.8
        
        # Check for comparison words
        comparison_terms = ['compare', 'difference', 'relationship', 'association']
        if any(term in question_lower for term in comparison_terms):
            base_confidence = max(base_confidence, 0.6)
        
        # Combined confidence score
        confidence = max(keyword_score, base_confidence)
        
        return confidence
