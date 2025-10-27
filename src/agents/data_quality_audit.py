"""
Data Quality Audit Agent
Comprehensive data quality assessment for business-critical data
"""

from typing import Dict, Any, List


class DataQualityAuditAgent:
    """Agent for comprehensive data quality assessment and validation"""
    
    def __init__(self):
        self.name = "data_quality_audit"
        self.display_name = "Data Quality Audit"
        self.description = "Comprehensive data quality assessment focusing on completeness, accuracy, consistency, and validity of business data"
        self.specialties = [
            "data completeness assessment", 
            "accuracy validation",
            "consistency checking",
            "business rule validation", 
            "data profiling",
            "quality scoring"
        ]
        self.keywords = [
            "data quality", "audit", "completeness", "accuracy",
            "validation", "profiling", "assessment", "quality", "clean"
        ]
        self.required_columns = []  # Works with any dataset
        self.output_type = "quality_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for data quality audit"""
        
        return f"""
You are an expert data quality engineer specializing in comprehensive data auditing and validation for business systems.

**Task: Comprehensive Data Quality Audit**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Missing values: {data_sample['missing_values']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform enterprise-grade data quality audit including:

1. **Data Completeness Assessment:**
   - Calculate completeness percentages for each column
   - Identify critical missing data patterns
   - Assess row-level completeness and data coverage
   - Generate completeness heat maps and trends

2. **Accuracy & Validity Validation:**
   - Validate data formats (emails, phone numbers, dates)
   - Check numerical ranges and business logic constraints
   - Identify invalid or suspicious values
   - Validate referential integrity where applicable

3. **Consistency Analysis:**
   - Check for data standardization issues
   - Identify inconsistent naming conventions
   - Detect contradictory data relationships
   - Analyze cross-field consistency rules

4. **Data Profiling & Statistics:**
   - Generate comprehensive statistical profiles
   - Identify data distribution patterns and anomalies
   - Calculate uniqueness and cardinality metrics
   - Detect potential duplicate records using fuzzy matching

5. **Business Rule Validation:**
   - Implement domain-specific validation rules
   - Check for logical inconsistencies in business data
   - Validate calculated fields and derived metrics
   - Assess data freshness and timeliness

6. **Quality Scoring & Reporting:**
   - Calculate overall data quality score
   - Generate dimension-specific quality metrics
   - Create executive summary with quality assessment
   - Provide prioritized recommendations for improvement

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Generate comprehensive quality dashboard visualizations
- Create detailed audit report as 'data_quality_audit_report.txt'
- Export quality issues as 'data_quality_issues.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Your complete data quality audit code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive data quality audit",
    "description": "Enterprise-grade data quality assessment with completeness, accuracy, consistency, and validity analysis",
    "outputs": ["data_quality_audit_report.txt", "data_quality_issues.csv", "quality_dashboard.png", "completeness_heatmap.png", "data_profiling_summary.png", "quality_scores.png"],
    "insights": "Comprehensive data quality assessment with specific quality scores, critical issues identified, and prioritized improvement recommendations"
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
        
        # Check for quality-related keywords with weighted importance
        primary_keywords = ["quality", "audit", "validation", "assessment"]
        secondary_keywords = ["completeness", "accuracy", "consistency", "profiling", "clean"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.4 + secondary_matches * 0.15), 1.0)
        
        # This agent is highly valuable for any dataset
        base_confidence = 0.4
        
        # Higher confidence for explicit quality requests
        quality_phrases = ['data quality', 'quality check', 'audit data', 'validate data', 'assess quality']
        if any(phrase in question_lower for phrase in quality_phrases):
            base_confidence = 0.9
        
        # Combined confidence score
        confidence = max(keyword_score, base_confidence)
        
        return min(confidence, 1.0)
