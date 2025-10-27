"""
Competitive Analysis Agent
Market positioning and competitive intelligence for small and medium businesses
"""

from typing import Dict, Any, List


class CompetitiveAnalysisAgent:
    """Agent for competitive analysis and market positioning insights"""
    
    def __init__(self):
        self.name = "competitive_analysis"
        self.display_name = "Competitive Analysis"
        self.description = "Analyze competitive positioning, market share, pricing strategies, and identify competitive advantages for small businesses"
        self.specialties = [
            "competitive positioning analysis",
            "market share assessment",
            "pricing comparison analysis", 
            "competitive advantage identification",
            "competitor performance tracking",
            "market opportunity assessment"
        ]
        self.keywords = [
            "competitive", "competitor", "market share", "positioning",
            "pricing", "competition", "market", "benchmark", "rival"
        ]
        self.required_columns = ["competitor"]
        self.output_type = "competitive_report"
    
    def get_analysis_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Generate the specific prompt for competitive analysis"""
        
        return f"""
You are an expert business strategist specializing in competitive intelligence and market positioning for small and medium businesses.

**Task: Comprehensive Competitive Analysis**

**Data Overview:**
- Dataset: {data_sample['file_info']['filename']}
- Total records: {data_sample['total_rows']:,}
- Available columns: {', '.join(data_sample['columns'])}
- Data types: {data_sample['data_types']}
- Sample data: {data_sample['sample_data'][:3]}

**User Request:** "{user_question}"

**Your mission:**
Generate complete, production-ready Python code to perform SMB-focused competitive analysis including:

1. **Market Position Assessment:**
   - Competitive landscape mapping
   - Market share analysis and trends
   - Positioning matrix development
   - Brand perception comparison

2. **Pricing Strategy Analysis:**
   - Competitive pricing comparison
   - Price elasticity and positioning
   - Value proposition assessment
   - Pricing opportunity identification

3. **Performance Benchmarking:**
   - Key performance indicator comparisons
   - Competitive strengths and weaknesses
   - Performance gap analysis
   - Operational efficiency comparisons

4. **Market Opportunity Analysis:**
   - Underserved market segment identification
   - Competitive gap analysis
   - Blue ocean opportunity assessment
   - Market entry barrier evaluation

5. **Competitive Intelligence:**
   - Competitor strategy pattern analysis
   - Market trend impact assessment
   - Competitive threat evaluation
   - Response strategy recommendations

6. **SMB Competitive Strategies:**
   - Niche market opportunity identification
   - Differentiation strategy recommendations
   - Resource allocation for competitive advantage
   - Local market dominance strategies

**Requirements:**
- Assume data is loaded as pandas DataFrame 'df'
- Save all outputs to current directory
- Focus on actionable SMB competitive insights
- Create competitive dashboard visualizations
- Generate comprehensive report as 'competitive_analysis_report.txt'
- Export competitor comparison as 'competitor_benchmarking.csv'

**Code Structure:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set competitive analysis visualization style
plt.style.use('default')
sns.set_palette("tab10")

# Your complete competitive analysis code here...
```

Respond with ONLY a JSON object:
{{
    "code": "complete Python code for SMB competitive analysis",
    "description": "Comprehensive competitive intelligence analysis with market positioning, pricing strategies, and competitive advantage identification for small businesses",
    "outputs": ["competitive_analysis_report.txt", "competitor_benchmarking.csv", "competitive_landscape.png", "pricing_comparison.png", "market_position.png", "performance_gaps.png", "opportunity_matrix.png"],
    "insights": "Competitive positioning insights, pricing optimization opportunities, market gaps, and strategic recommendations for small business competitive advantage"
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
        
        # Check for competitive analysis keywords
        primary_keywords = ["competitive", "competitor", "competition", "market"]
        secondary_keywords = ["positioning", "benchmark", "rival", "share", "pricing"]
        
        primary_matches = sum(1 for keyword in primary_keywords if keyword in question_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in question_lower)
        
        keyword_score = min((primary_matches * 0.5 + secondary_matches * 0.2), 1.0)
        
        # Check for required columns
        column_score = 0.0
        column_names_lower = [col.lower() for col in data_columns]
        
        # Look for competitor identifiers
        competitor_indicators = ['competitor', 'company', 'brand', 'business', 'vendor', 'supplier']
        has_competitor = any(indicator in ' '.join(column_names_lower) for indicator in competitor_indicators)
        
        # Look for competitive metrics
        competitive_indicators = ['price', 'market_share', 'revenue', 'performance', 'rating', 'score']
        has_metrics = any(indicator in ' '.join(column_names_lower) for indicator in competitive_indicators)
        
        if has_competitor:
            column_score += 0.6
        if has_metrics:
            column_score += 0.4
        
        # Combined confidence score
        confidence = (keyword_score * 0.7) + (column_score * 0.3)
        
        return min(confidence, 1.0)
