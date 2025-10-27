"""
Customer Segmentation Agent
Specializes in clustering customers into meaningful segments
"""

from typing import Dict, Any, List


class CustomerSegmentationAgent:
    """Agent for customer segmentation and clustering analysis"""
    
    def __init__(self):
        self.name = "customer_segmentation"
        self.display_name = "Customer Segmentation & Personas"
        self.description = "Advanced customer clustering using RFM, behavioral, and demographic data to create actionable customer personas and targeting strategies"
        self.specialties = [
            "rfm segmentation",
            "behavioral clustering",
            "persona development",
            "targeting strategies",
            "customer profiling",
            "value-based segmentation"
        ]
        self.keywords = [
            "segment", "cluster", "personas", "customer groups",
            "rfm", "behavioral", "demographics", "targeting"
        ]
        self.required_columns = ["customer_id"]
        self.output_type = "segmentation_model"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for customer segmentation"""
        
        return f"""
You are an expert data scientist specializing in customer segmentation and behavioral analysis.

**Task: Customer Segmentation Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform comprehensive customer segmentation including:

1. **Data Preparation:**
   - Identify and prepare customer-level features
   - Handle missing values appropriately for clustering
   - Scale/normalize numerical features for clustering algorithms
   - Create RFM features if transaction data available

2. **Feature Engineering:**
   - Calculate behavioral metrics (frequency, recency, monetary value)
   - Create demographic profiles if data available
   - Generate engagement and activity scores
   - Identify relevant clustering features

3. **Clustering Analysis:**
   - Implement K-Means clustering with optimal k selection
   - Use elbow method and silhouette analysis for k selection
   - Try hierarchical clustering as alternative approach
   - Evaluate cluster quality and stability

4. **Segment Profiling:**
   - Analyze characteristics of each customer segment
   - Create detailed segment profiles and personas
   - Calculate segment sizes and key metrics
   - Identify high-value vs low-value segments

5. **Visualization & Insights:**
   - Create cluster visualization using PCA/t-SNE
   - Generate segment comparison charts
   - Visualize segment characteristics and differences
   - Provide actionable business insights for each segment

6. **Business Recommendations:**
   - Suggest targeted marketing strategies per segment
   - Identify opportunities for cross-selling/upselling
   - Recommend retention strategies for each group

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save segmentation results as 'customer_segments.csv'
- Create cluster visualization plots
- Generate segment profile report as 'segmentation_report.txt'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

# Your complete segmentation code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for customer segmentation analysis",
    "description": "Customer clustering and segmentation with behavioral analysis",
    "outputs": ["customer_segments.csv", "segmentation_report.txt", "cluster_visualization.png", "segment_profiles.png", "elbow_analysis.png"],
    "insights": "Key customer segments identified and their characteristics for targeted strategies"
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
        
        # Check for segmentation-related keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in question_lower)
        keyword_score = min(keyword_matches / len(self.keywords), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for customer ID column
        customer_id_indicators = ['customer_id', 'customer', 'cust_id', 'user_id', 'id']
        has_customer_id = any(indicator in ' '.join(column_names_lower) for indicator in customer_id_indicators)
        
        if has_customer_id:
            column_score += 0.6
        
        # Look for potential segmentation features
        segment_indicators = ['purchase', 'transaction', 'revenue', 'amount', 'age', 'gender']
        segment_features = sum(1 for indicator in segment_indicators 
                             if indicator in ' '.join(column_names_lower))
        
        if segment_features > 0:
            column_score += min(segment_features * 0.1, 0.4)
        
        # Combined confidence score
        confidence = (keyword_score * 0.7) + (column_score * 0.3)
        
        return confidence
