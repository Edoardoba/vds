"""
Data Cleaning & Preprocessing Agent
Specializes in data quality assessment and preprocessing
"""

from typing import Dict, Any, List


class DataCleaningAgent:
    """Agent for data cleaning and preprocessing operations"""
    
    def __init__(self):
        self.name = "data_cleaning"
        self.display_name = "Data Cleaning & Preprocessing"
        self.description = "Handles missing values, duplicates, outliers, and data type conversions to prepare data for analysis"
        self.specialties = [
            "missing value imputation",
            "outlier detection",
            "duplicate removal", 
            "data type conversion",
            "data quality assessment"
        ]
        self.keywords = [
            "clean", "missing", "null", "duplicates", "outliers",
            "preprocessing", "data quality", "prepare", "standardize"
        ]
        self.required_columns = []  # Works with any dataset
        self.output_type = "cleaned_dataset"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for data cleaning"""
        
        return f"""
You are an expert data scientist specializing in data preprocessing and quality assurance.

**Task: Data Cleaning & Preprocessing**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Missing values: {data_sample['missing_values']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive data cleaning including:

1. **Data Quality Assessment:**
   - Analyze missing value patterns and percentages
   - Identify duplicate records and inconsistencies
   - Detect outliers using statistical methods (IQR, Z-score)
   - Assess data type appropriateness

2. **Missing Value Handling:**
   - Implement appropriate imputation strategies per column type
   - Use mean/median for numerical, mode for categorical
   - Consider forward-fill for time series data
   - Document imputation decisions

3. **Outlier Detection & Treatment:**
   - Use IQR method and Z-score for outlier detection
   - Visualize outliers with box plots and scatter plots
   - Apply capping, transformation, or removal as appropriate

4. **Data Standardization:**
   - Ensure consistent data formats
   - Standardize categorical values (case, spelling)
   - Convert data types appropriately
   - Handle date/time formatting

5. **Quality Reporting:**
   - Generate before/after comparison statistics
   - Create data quality summary report
   - Provide recommendations for further improvements

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save cleaned dataset as 'cleaned_data.csv'
- Generate data quality report as 'data_quality_report.txt'
- Create visualizations showing data quality issues

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Your complete data cleaning code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for data cleaning and preprocessing",
    "description": "Comprehensive data cleaning, outlier detection, and quality assessment",
    "outputs": ["cleaned_data.csv", "data_quality_report.txt", "outlier_analysis.png", "missing_values_heatmap.png"],
    "insights": "Key data quality issues found and cleaning actions performed"
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
        
        # Check for cleaning-related keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in question_lower)
        keyword_score = min(keyword_matches / len(self.keywords), 1.0)
        
        # This agent is universally applicable, so give base confidence
        base_confidence = 0.3
        
        # Higher confidence if explicitly mentioned
        if any(word in question_lower for word in ['clean', 'preprocess', 'quality', 'missing']):
            base_confidence = 0.8
        
        # Combined confidence score
        confidence = max(keyword_score, base_confidence)
        
        return confidence
