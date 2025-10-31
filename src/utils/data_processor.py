"""
Data processing utilities for analyzing uploaded files
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, Any, List, Optional, Union
from io import BytesIO
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def clean_nan_values(obj: Any) -> Any:
    """
    Recursively clean NaN and infinity values from nested data structures
    to make them JSON serializable
    
    Args:
        obj: Any object that might contain NaN values
        
    Returns:
        Object with NaN/infinity values replaced with None
    """
    if isinstance(obj, dict):
        return {key: clean_nan_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, (np.floating, float)):
        if pd.isna(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32, int)):
        return int(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, str):
        return str(obj)
    elif pd.isna(obj):
        return None
    elif obj is None:
        return None
    else:
        # For any other numpy types, try to convert to Python native types
        try:
            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            return obj
        except (ValueError, TypeError):
            return str(obj)  # fallback to string representation


class DataProcessor:
    """Handles data processing operations for uploaded files"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']
    
    def read_file_sample(self, file_content: bytes, filename: str, sample_rows: int = 3) -> Dict[str, Any]:
        """
        Read the first few rows of a file to understand its structure

        Args:
            file_content: Raw file content as bytes
            filename: Original filename to determine file type
            sample_rows: Number of rows to sample (default: 3)
            
        Returns:
            Dict containing sample data, columns info, and basic statistics
        """
        try:
            file_extension = Path(filename).suffix.lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(BytesIO(file_content))
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Get sample rows (first N rows)
            sample_df = df.head(sample_rows)
            
            # Get data info
            data_info = self._analyze_data_structure(df)
            
            # Convert sample to JSON-serializable format
            sample_data = sample_df.to_dict('records')
            
            # Clean all data to ensure JSON serializability
            result = {
                'sample_data': clean_nan_values(sample_data),
                'columns': list(df.columns),
                'total_rows': len(df),
                'data_types': clean_nan_values(data_info['data_types']),
                'missing_values': clean_nan_values(data_info['missing_values']),
                'summary_stats': clean_nan_values(data_info['summary_stats']),
                'file_info': {
                    'filename': filename,
                    'format': file_extension,
                    'size_mb': len(file_content) / (1024 * 1024)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            raise ValueError(f"Failed to process file: {str(e)}")
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the structure and basic statistics of the dataframe
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dict containing data analysis results
        """
        analysis = {
            'data_types': {},
            'missing_values': {},
            'summary_stats': {}
        }
        
        # Data types
        for col in df.columns:
            dtype = str(df[col].dtype)
            analysis['data_types'][col] = dtype
        
        # Missing values
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df) * 100).round(2)
        
        for col in df.columns:
            analysis['missing_values'][col] = {
                'count': int(missing_counts[col]),
                'percentage': float(missing_percentages[col])
            }
        
        # Summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary = df[numeric_cols].describe()
            for col in numeric_cols:
                analysis['summary_stats'][col] = {
                    'mean': float(summary.loc['mean', col]) if not pd.isna(summary.loc['mean', col]) else None,
                    'std': float(summary.loc['std', col]) if not pd.isna(summary.loc['std', col]) else None,
                    'min': float(summary.loc['min', col]) if not pd.isna(summary.loc['min', col]) else None,
                    'max': float(summary.loc['max', col]) if not pd.isna(summary.loc['max', col]) else None,
                    'median': float(summary.loc['50%', col]) if not pd.isna(summary.loc['50%', col]) else None
                }
        
        return analysis
    
    def identify_potential_columns(self, columns: List[str]) -> Dict[str, List[str]]:
        """
        Identify potential column types based on column names
        
        Args:
            columns: List of column names
            
        Returns:
            Dict mapping column types to potential matches
        """
        column_patterns = {
            'customer_id': ['customer_id', 'customer', 'cust_id', 'user_id', 'id'],
            'date': ['date', 'timestamp', 'created_at', 'updated_at', 'time'],
            'revenue': ['revenue', 'sales', 'amount', 'price', 'value', 'cost'],
            'quantity': ['quantity', 'qty', 'count', 'number', 'num'],
            'category': ['category', 'type', 'class', 'group', 'segment'],
            'location': ['location', 'city', 'state', 'country', 'region', 'address']
        }
        
        potential_matches = {pattern_type: [] for pattern_type in column_patterns}
        
        for col in columns:
            col_lower = col.lower().strip()
            for pattern_type, patterns in column_patterns.items():
                if any(pattern in col_lower for pattern in patterns):
                    potential_matches[pattern_type].append(col)
        
        return potential_matches
    
    def generate_column_suggestions(self, columns: List[str], agent_requirements: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        """
        Generate suggestions for which agents can work with the available columns
        
        Args:
            columns: Available columns in the dataset
            agent_requirements: Dict of agent names to required columns
            
        Returns:
            Dict of agent compatibility analysis
        """
        suggestions = {}
        potential_columns = self.identify_potential_columns(columns)
        
        for agent_name, required_cols in agent_requirements.items():
            compatibility = {
                'can_run': True,
                'missing_columns': [],
                'suggested_columns': {},
                'confidence': 0.0
            }
            
            # Check if required columns are available
            for req_col in required_cols:
                matches = potential_columns.get(req_col, [])
                if matches:
                    compatibility['suggested_columns'][req_col] = matches[0]  # Best match
                    compatibility['confidence'] += 1.0 / len(required_cols)
                else:
                    compatibility['missing_columns'].append(req_col)
                    compatibility['can_run'] = False
            
            suggestions[agent_name] = compatibility
        
        return suggestions


def create_sample_prompt(data_sample: Dict[str, Any], user_question: str) -> str:
    """
    Create a prompt for the Claude API that includes data sample and user question
    
    Args:
        data_sample: Sample data from DataProcessor.read_file_sample()
        user_question: User's question about the data
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
You are a data analysis expert. Please analyze the following data sample and user question to determine which specialized analysis agents should be used.

**Data Information:**
- File: {data_sample['file_info']['filename']}
- Total rows: {data_sample['total_rows']:,}
- Columns: {len(data_sample['columns'])} ({', '.join(data_sample['columns'])})

**Sample Data (first {len(data_sample['sample_data'])} rows):**
{data_sample['sample_data']}

**Data Types:**
{data_sample['data_types']}

**User Question:**
"{user_question}"

**Available Analysis Agents:**
1. churn_analysis - Customer churn prediction and retention analysis
2. data_cleaning - Data cleaning, preprocessing, and quality assessment  
3. data_visualization - Exploratory data analysis and visualizations
4. customer_segmentation - Customer clustering and segmentation
5. regression_analysis - Predictive modeling and regression analysis
6. statistical_analysis - Statistical tests and hypothesis testing
7. time_series_analysis - Time-based analysis and forecasting

Please respond with ONLY a JSON array of agent names that should be executed, in order of priority. Consider:
1. The user's specific question and intent
2. The available data columns and types
3. The data quality and structure
4. What analysis would provide the most value

Example response: ["data_cleaning", "data_visualization", "statistical_analysis"]
"""
    
    return prompt
