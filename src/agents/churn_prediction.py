"""
Customer Churn Prediction Agent
Advanced machine learning models to predict customer churn and identify at-risk customers
"""

from typing import Dict, Any, List


class ChurnPredictionAgent:
    """Agent for customer churn prediction and retention optimization"""
    
    def __init__(self):
        self.name = "churn_prediction"
        self.display_name = "Customer Churn Prediction"
        self.description = "Advanced machine learning models to predict customer churn probability and identify at-risk customers for proactive retention"
        self.specialties = [
            "churn probability modeling",
            "retention strategy optimization", 
            "customer lifetime value prediction",
            "early warning systems",
            "feature importance analysis",
            "risk scoring"
        ]
        self.keywords = [
            "churn", "attrition", "retention", "customer lifetime",
            "dropout", "cancel", "unsubscribe", "leaving", "risk"
        ]
        self.required_columns = ["customer_id"]
        self.output_type = "churn_model"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for churn prediction"""
        
        return f"""
You are an expert data scientist specializing in advanced customer churn prediction and retention strategy optimization.

**Task: Customer Churn Prediction & Risk Assessment**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to build advanced churn prediction models including:

1. **Data Preprocessing & Feature Engineering:**
   - Handle missing values with domain-specific imputation
   - Create behavioral features (RFM, engagement patterns, usage trends)
   - Generate time-based features (tenure, days since last activity)
   - Create interaction and derived features for better predictions

2. **Churn Risk Assessment:**
   - Calculate baseline churn rate and segment-specific rates
   - Identify early warning indicators and risk patterns
   - Create customer risk scoring framework
   - Analyze churn patterns by customer segments

3. **Advanced Predictive Modeling:**
   - Build multiple models (Logistic Regression, Random Forest, XGBoost, Neural Network)
   - Implement ensemble methods for improved accuracy
   - Perform hyperparameter tuning and cross-validation
   - Generate probability scores and risk categories

4. **Model Evaluation & Interpretation:**
   - Use appropriate metrics (AUC-ROC, Precision-Recall, F1-Score)
   - Create feature importance analysis and SHAP values
   - Identify key churn drivers and their business impact
   - Validate model performance with holdout testing

5. **Business Impact & Retention Strategy:**
   - Calculate potential revenue impact of churn prevention
   - Identify high-value at-risk customers for targeted intervention
   - Generate retention recommendations by customer segment
   - Create actionable early warning system thresholds

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Handle imbalanced dataset with appropriate techniques
- Generate comprehensive visualizations as PNG files
- Create detailed business report as 'churn_prediction_report.txt'
- Export model predictions as 'high_risk_customers.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.utils import resample
import warnings
warnings.filterwarnings('ignore')

# Your complete churn prediction analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for advanced churn prediction",
    "description": "Advanced machine learning-based customer churn prediction with risk scoring and retention strategies",
    "outputs": ["churn_prediction_report.txt", "high_risk_customers.csv", "churn_model_performance.png", "feature_importance.png", "risk_distribution.png", "retention_strategy.png"],
    "insights": "Key findings about churn patterns, high-risk customers, and recommended retention strategies with potential revenue impact"
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
        
        # Check for churn-related keywords with weighted importance
        primary_keywords = ["churn", "attrition", "retention", "cancel"]
        secondary_keywords = ["dropout", "unsubscribe", "leaving", "risk", "customer lifetime"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.3 + secondary_matches * 0.1), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for customer ID column (essential for churn analysis)
        customer_id_indicators = ['customer_id', 'customer', 'cust_id', 'user_id', 'id', 'account_id']
        has_customer_id = any(indicator in ' '.join(column_names_lower) for indicator in customer_id_indicators)
        
        if has_customer_id:
            column_score += 0.4
        
        # Look for potential churn indicators
        churn_indicators = ['churn', 'status', 'active', 'cancelled', 'subscription', 'contract']
        has_churn_indicator = any(indicator in ' '.join(column_names_lower) for indicator in churn_indicators)
        
        if has_churn_indicator:
            column_score += 0.4
            
        # Look for temporal data (important for churn prediction)
        temporal_indicators = ['date', 'time', 'created', 'last_active', 'tenure']
        has_temporal = any(indicator in ' '.join(column_names_lower) for indicator in temporal_indicators)
        
        if has_temporal:
            column_score += 0.2
        
        # Combined confidence score
        confidence = (keyword_score * 0.7) + (column_score * 0.3)
        
        return min(confidence, 1.0)
