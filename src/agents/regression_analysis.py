"""
Regression Analysis Agent
Specializes in predictive modeling and regression analysis
"""

from typing import Dict, Any, List


class RegressionAnalysisAgent:
    """Agent for regression analysis and predictive modeling"""
    
    def __init__(self):
        self.name = "regression_analysis"
        self.display_name = "Regression Analysis"
        self.description = "Performs linear and non-linear regression analysis to predict continuous variables and understand relationships"
        self.specialties = [
            "linear regression",
            "multiple regression", 
            "polynomial regression",
            "feature importance",
            "predictive modeling"
        ]
        self.keywords = [
            "regression", "predict", "forecast", "linear",
            "relationship", "correlation", "feature importance", "model"
        ]
        self.required_columns = []  # Works with datasets that have numerical target
        self.output_type = "regression_model"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for regression analysis"""
        
        return f"""
You are an expert data scientist specializing in regression analysis and predictive modeling.

**Task: Regression Analysis & Predictive Modeling**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive regression analysis including:

1. **Target Variable Identification:**
   - Automatically identify the most suitable target variable for regression
   - Analyze target variable distribution and characteristics
   - Handle target variable transformation if needed (log, square root, etc.)

2. **Feature Preparation:**
   - Select relevant numerical and categorical features
   - Handle categorical variables with encoding (one-hot, label encoding)
   - Address multicollinearity issues
   - Feature scaling and normalization

3. **Model Development:**
   - Implement multiple regression algorithms:
     * Linear Regression (baseline)
     * Ridge Regression (regularization)
     * Lasso Regression (feature selection)
     * Random Forest Regression (non-linear)
   - Perform train-test split for validation

4. **Model Evaluation:**
   - Calculate comprehensive metrics (R², RMSE, MAE, MAPE)
   - Cross-validation for robust performance assessment
   - Residual analysis and diagnostic plots
   - Feature importance analysis

5. **Advanced Analysis:**
   - Polynomial features for non-linear relationships
   - Interaction effects between variables
   - Partial dependence plots for key features
   - Prediction confidence intervals

6. **Results Interpretation:**
   - Identify most important predictive features
   - Quantify relationships and effect sizes
   - Provide business insights from model coefficients
   - Generate predictions on sample data

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save model results and predictions as 'regression_results.csv'
- Create comprehensive model evaluation plots
- Generate detailed analysis report as 'regression_report.txt'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Your complete regression analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for regression analysis and predictive modeling",
    "description": "Comprehensive regression modeling with feature importance and prediction analysis",
    "outputs": ["regression_results.csv", "regression_report.txt", "model_performance.png", "feature_importance.png", "residual_analysis.png"],
    "insights": "Key predictive factors identified and model performance insights"
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
        
        # Check for regression-related keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in question_lower)
        keyword_score = min(keyword_matches / len(self.keywords), 1.0)
        
        # Check data suitability for regression
        column_score = 0.0
        
        # Count numerical columns (potential targets and features)
        numerical_indicators = ['amount', 'price', 'value', 'cost', 'revenue', 'sales', 'score', 'rating']
        numerical_count = sum(1 for col in data_columns 
                            if any(indicator in col.lower() for indicator in numerical_indicators))
        
        if numerical_count > 0:
            column_score = min(numerical_count * 0.2, 1.0)
        
        # Higher confidence if prediction/modeling terms mentioned
        predict_terms = ['predict', 'forecast', 'model', 'estimate']
        if any(term in question_lower for term in predict_terms):
            keyword_score = max(keyword_score, 0.7)
        
        # Combined confidence score
        confidence = (keyword_score * 0.8) + (column_score * 0.2)
        
        return confidence
