"""
Anomaly & Fraud Detection Agent
Advanced outlier identification and suspicious pattern recognition for risk management
"""

from typing import Dict, Any, List


class AnomalyDetectionAgent:
    """Agent for anomaly detection and fraud prevention"""
    
    def __init__(self):
        self.name = "anomaly_detection"
        self.display_name = "Anomaly & Fraud Detection"
        self.description = "Advanced anomaly detection for fraud prevention, outlier identification, and suspicious pattern recognition using ML algorithms"
        self.specialties = [
            "fraud detection",
            "anomaly identification",
            "outlier analysis",
            "pattern recognition",
            "risk scoring",
            "suspicious activity detection"
        ]
        self.keywords = [
            "anomaly", "fraud", "outlier", "suspicious",
            "detection", "risk", "unusual", "abnormal"
        ]
        self.required_columns = []  # Works with any dataset
        self.output_type = "anomaly_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for anomaly detection"""
        
        return f"""
You are an expert data scientist specializing in anomaly detection, fraud prevention, and risk assessment using advanced machine learning techniques.

**Task: Comprehensive Anomaly & Fraud Detection**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive anomaly detection and risk assessment including:

1. **Statistical Anomaly Detection:**
   - Z-score and modified Z-score outlier detection
   - Interquartile range (IQR) method for outliers
   - Mahalanobis distance for multivariate outliers
   - Statistical process control (SPC) charts

2. **Machine Learning Anomaly Detection:**
   - Isolation Forest for unsupervised anomaly detection
   - One-Class SVM for novelty detection
   - Local Outlier Factor (LOF) for density-based detection
   - Autoencoder neural networks for complex pattern detection

3. **Time Series Anomaly Detection:**
   - Seasonal decomposition for temporal anomalies
   - Change point detection algorithms
   - Trend deviation analysis
   - ARIMA residual-based anomaly detection

4. **Business Rule-Based Detection:**
   - Domain-specific business rule violations
   - Threshold-based alerting systems
   - Pattern matching for known fraud signatures
   - Velocity checks and frequency analysis

5. **Risk Scoring & Prioritization:**
   - Composite anomaly scores calculation
   - Risk level categorization (high/medium/low)
   - False positive reduction techniques
   - Anomaly severity assessment

6. **Fraud Pattern Analysis:**
   - Network analysis for connected fraud
   - Sequential pattern mining
   - Behavioral baseline establishment
   - Social network analysis for collusion detection

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Generate anomaly detection dashboard visualizations
- Create comprehensive anomaly report as 'anomaly_detection_report.txt'
- Export flagged records as 'anomalies_flagged.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from scipy import stats
from scipy.spatial.distance import mahalanobis
import warnings
warnings.filterwarnings('ignore')

# Set anomaly detection visualization style
plt.style.use('default')
sns.set_palette("Reds_r")

# Your complete anomaly detection code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for comprehensive anomaly and fraud detection",
    "description": "Multi-method anomaly detection with statistical, ML-based, and business rule approaches for fraud prevention and risk management",
    "outputs": ["anomaly_detection_report.txt", "anomalies_flagged.csv", "anomaly_dashboard.png", "outlier_analysis.png", "risk_scoring.png", "detection_methods_comparison.png", "time_series_anomalies.png"],
    "insights": "Critical anomalies identified, fraud risk assessment, and recommended investigation priorities with confidence scores and risk levels"
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
        
        # Check for anomaly-related keywords
        primary_keywords = ["anomaly", "fraud", "outlier", "detection"]
        secondary_keywords = ["suspicious", "risk", "unusual", "abnormal", "irregular"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.5 + secondary_matches * 0.15), 1.0)
        
        # This agent is valuable for many datasets, especially those with potential quality issues
        base_confidence = 0.3
        
        # Higher confidence for explicit anomaly/fraud requests
        anomaly_phrases = ['detect anomal', 'find outlier', 'fraud detect', 'suspicious activity', 'identify risk']
        if any(phrase in question_lower for phrase in anomaly_phrases):
            base_confidence = 0.9
        
        # Look for financial/transactional data (higher fraud risk)
        financial_indicators = ['transaction', 'payment', 'amount', 'account', 'card', 'transfer']
        column_names_lower = [col.lower() for col in data_columns]
        has_financial = any(indicator in ' '.join(column_names_lower) for indicator in financial_indicators)
        
        if has_financial:
            base_confidence = max(base_confidence, 0.5)
        
        # Combined confidence score
        confidence = max(keyword_score, base_confidence)
        
        return min(confidence, 1.0)
