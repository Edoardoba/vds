"""
A/B Testing & Experimentation Agent
Statistical analysis of experiments for data-driven business decisions
"""

from typing import Dict, Any, List


class AbTestingAnalysisAgent:
    """Agent for A/B testing analysis and experimentation"""
    
    def __init__(self):
        self.name = "ab_testing_analysis"
        self.display_name = "A/B Testing & Experimentation"
        self.description = "Statistical analysis of A/B tests, experiment design validation, significance testing, and business impact assessment"
        self.specialties = [
            "a/b test analysis",
            "statistical significance testing",
            "experiment design",
            "conversion analysis",
            "impact measurement",
            "test optimization"
        ]
        self.keywords = [
            "a/b test", "experiment", "testing", "significance",
            "conversion", "impact", "control", "treatment"
        ]
        self.required_columns = ["test_group"]
        self.output_type = "experiment_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for A/B testing analysis"""
        
        return f"""
You are an expert experimentation analyst specializing in A/B testing, statistical significance, and causal inference for business optimization.

**Task: Comprehensive A/B Testing & Experimentation Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive A/B testing analysis including:

1. **Experiment Design Validation:**
   - Sample size and power analysis validation
   - Randomization quality assessment
   - Treatment group balance evaluation
   - Temporal bias and external validity checks

2. **Statistical Significance Testing:**
   - Two-sample t-tests for continuous metrics
   - Chi-square tests for categorical outcomes
   - Mann-Whitney U tests for non-parametric data
   - Multiple comparison corrections (Bonferroni, FDR)

3. **Effect Size & Business Impact:**
   - Cohen's d and other effect size measures
   - Confidence intervals for treatment effects
   - Relative and absolute improvement calculations
   - Revenue impact and ROI projections

4. **Advanced Experimentation Analysis:**
   - Segmented analysis by user characteristics
   - Time-based trend analysis during experiment
   - Survival analysis for time-to-event outcomes
   - Bayesian A/B testing approaches

5. **Conversion Funnel Analysis:**
   - Multi-step conversion analysis
   - Funnel stage impact assessment
   - User journey optimization insights
   - Drop-off point identification

6. **Recommendations & Next Steps:**
   - Statistical conclusion and business recommendation
   - Sample size recommendations for future tests
   - Segmentation insights for targeted experiments
   - Follow-up experiment design suggestions

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Generate experiment analysis dashboard visualizations
- Create comprehensive testing report as 'ab_testing_analysis_report.txt'
- Export detailed results as 'experiment_results.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import ttest_ind, chi2_contingency, mannwhitneyu
from statsmodels.stats.power import ttest_power
from statsmodels.stats.proportion import proportions_ztest
import warnings
warnings.filterwarnings('ignore')

# Set experiment analysis visualization style
plt.style.use('default')
sns.set_palette("Set1")

# Your complete A/B testing analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive A/B testing analysis",
    "description": "Statistical experiment analysis with significance testing, effect size calculation, and business impact assessment",
    "outputs": ["ab_testing_analysis_report.txt", "experiment_results.csv", "significance_testing_dashboard.png", "effect_size_analysis.png", "conversion_funnel.png", "segment_analysis.png", "power_analysis.png"],
    "insights": "Statistical significance results, effect sizes, business impact projections, and recommendations for experiment optimization and future testing strategy"
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
        
        # Check for A/B testing keywords
        primary_keywords = ["a/b test", "experiment", "testing", "significance"]
        secondary_keywords = ["control", "treatment", "conversion", "impact", "test group"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.5 + secondary_matches * 0.2), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for test group indicators
        test_group_indicators = ['test_group', 'group', 'variant', 'treatment', 'control', 'experiment']
        has_test_group = any(indicator in ' '.join(column_names_lower) for indicator in test_group_indicators)
        
        if has_test_group:
            column_score += 0.6
        
        # Look for conversion/outcome metrics
        outcome_indicators = ['conversion', 'outcome', 'success', 'click', 'purchase', 'signup']
        has_outcome = any(indicator in ' '.join(column_names_lower) for indicator in outcome_indicators)
        
        if has_outcome:
            column_score += 0.4
        
        # Combined confidence score
        confidence = (keyword_score * 0.6) + (column_score * 0.4)
        
        return min(confidence, 1.0)
