"""
Advanced Predictive Modeling Agent
Custom machine learning models for business prediction tasks
"""

from typing import Dict, Any, List


class PredictiveModelingAgent:
    """Agent for advanced predictive analytics and machine learning modeling"""
    
    def __init__(self):
        self.name = "predictive_modeling"
        self.display_name = "Advanced Predictive Modeling"
        self.description = "Custom machine learning models for business prediction tasks including classification, regression, and ensemble methods"
        self.specialties = [
            "machine learning modeling",
            "predictive analytics",
            "ensemble methods",
            "feature engineering",
            "model validation",
            "prediction optimization"
        ]
        self.keywords = [
            "predictive", "machine learning", "modeling", "prediction",
            "classification", "forecasting", "ml", "model"
        ]
        self.required_columns = []  # Works with any dataset
        self.output_type = "prediction_model"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for predictive modeling"""
        
        return f"""
You are an expert machine learning engineer specializing in building production-ready predictive models for business applications.

**Task: Advanced Predictive Modeling & Analytics**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to build advanced predictive models including:

1. **Automated Problem Type Detection:**
   - Identify if task is classification, regression, or time series
   - Detect target variable and feature types
   - Assess data suitability for ML modeling
   - Recommend appropriate modeling approaches

2. **Advanced Feature Engineering:**
   - Automated feature selection and importance ranking
   - Polynomial and interaction feature creation
   - Categorical encoding (one-hot, target, ordinal)
   - Numerical transformations (scaling, binning, log transforms)

3. **Model Development & Selection:**
   - Multiple algorithm comparison (Random Forest, XGBoost, Neural Networks, SVM)
   - Hyperparameter tuning with grid/random search
   - Cross-validation and model selection
   - Ensemble methods and model stacking

4. **Model Evaluation & Validation:**
   - Comprehensive performance metrics (accuracy, precision, recall, F1, AUC, RMSE)
   - Learning curves and validation curves
   - Feature importance and SHAP value analysis
   - Model interpretability and explainability

5. **Business Impact Assessment:**
   - ROI calculation for model deployment
   - Business metric impact estimation
   - Cost-benefit analysis of predictions
   - Risk assessment and model limitations

6. **Production Readiness:**
   - Model serialization and save/load functionality
   - Prediction pipeline creation
   - Performance monitoring recommendations
   - Model maintenance and retraining strategies

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Generate model performance dashboard visualizations
- Create comprehensive modeling report as 'predictive_modeling_report.txt'
- Export model predictions as 'model_predictions.csv'
- Save trained model as 'trained_model.pkl'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
import joblib
import warnings
warnings.filterwarnings('ignore')

# Your complete predictive modeling code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for advanced predictive modeling",
    "description": "End-to-end machine learning pipeline with automated feature engineering, model selection, and business impact assessment",
    "outputs": ["predictive_modeling_report.txt", "model_predictions.csv", "trained_model.pkl", "model_performance_dashboard.png", "feature_importance.png", "learning_curves.png", "model_comparison.png", "shap_analysis.png"],
    "insights": "Predictive model performance analysis, feature importance insights, business impact projections, and deployment recommendations"
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
        
        # Check for ML/prediction-related keywords
        primary_keywords = ["predict", "model", "machine learning", "ml"]
        secondary_keywords = ["classification", "regression", "forecasting", "algorithm"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.4 + secondary_matches * 0.2), 1.0)
        
        # This agent is good for general prediction tasks
        base_confidence = 0.4
        
        # Higher confidence for explicit ML requests
        ml_phrases = ['machine learning', 'predictive model', 'build model', 'train model', 'ml model']
        if any(phrase in question_lower for phrase in ml_phrases):
            base_confidence = 0.9
        
        # Check for prediction indicators
        prediction_words = ['predict', 'forecast', 'estimate', 'classify']
        if any(word in question_lower for word in prediction_words):
            base_confidence = max(base_confidence, 0.7)
        
        # Combined confidence score
        confidence = max(keyword_score, base_confidence)
        
        return min(confidence, 1.0)
