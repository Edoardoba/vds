#!/usr/bin/env python3
"""
Simple test script to demonstrate code execution using AgentService
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path
from io import StringIO

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.agent_service import AgentService
from utils.data_processor import DataProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_test_data(num_rows=100):
    """Generate simple test data"""
    np.random.seed(42)
    
    data = {
        'customer_id': [f"CUST_{i:04d}" for i in range(1, num_rows + 1)],
        'age': np.random.randint(18, 75, num_rows),
        'income': np.random.normal(50000, 15000, num_rows),
        'purchase_amount': np.random.exponential(100, num_rows),
        'region': np.random.choice(['North', 'South', 'East', 'West'], num_rows),
        'category': np.random.choice(['Electronics', 'Clothing', 'Books'], num_rows)
    }
    
    df = pd.DataFrame(data)
    return df


def create_data_sample_from_df(df, filename="test_data.csv"):
    """Convert DataFrame to format expected by agent service"""
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue().encode('utf-8')
    
    data_processor = DataProcessor()
    data_sample = data_processor.read_file_sample(csv_content, filename, sample_rows=10)
    
    return data_sample


async def test_manual_code_execution():
    """Test executing manually written Python code using the execution framework"""
    
    print("Manual Code Execution Test")
    print("=" * 50)
    
    # Generate test data
    print("Generating test dataset...")
    df = generate_test_data(50)
    data_sample = create_data_sample_from_df(df, "manual_execution_test.csv")
    
    # Convert DataFrame to bytes
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    file_content = csv_buffer.getvalue().encode('utf-8')
    
    # Create a simple manual analysis code
    manual_code = """
import pandas as pd
import numpy as np

# Load the data
df = pd.read_csv(data_file)

print("=== MANUAL EDA ANALYSIS ===")
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Data types:\\n{df.dtypes}")

print("\\n=== BASIC STATISTICS ===")
print(df.describe())

print("\\n=== MISSING VALUES ===")
print(df.isnull().sum())

print("\\n=== CORRELATION ANALYSIS ===")
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 1:
    corr_matrix = df[numeric_cols].corr()
    print(corr_matrix)

print("\\n=== CATEGORICAL ANALYSIS ===")
categorical_cols = df.select_dtypes(include=['object']).columns
for col in categorical_cols:
    print(f"\\n{col} value counts:")
    print(df[col].value_counts().head())

print("\\n=== ANALYSIS COMPLETE ===")
"""
    
    # Initialize agent service
    agent_service = AgentService()
    
    try:
        print("Executing manual analysis code...")
        
        # Create code result structure
        code_result = {
            "code": manual_code,
            "description": "Manual EDA analysis",
            "agent_name": "manual_test"
        }
        
        # Execute the manual code
        execution_result = await agent_service._execute_agent_code(
            agent_name="manual_test",
            code_result=code_result,
            file_content=file_content,
            data_sample=data_sample
        )
        
        print(f"Manual execution completed!")
        print(f"Execution success: {execution_result['success']}")
        print(f"Execution time: {execution_result.get('execution_time', 0):.2f} seconds")
        
        if execution_result['success']:
            print(f"Analysis output:")
            print("-" * 50)
            print(execution_result['output'])
            print("-" * 50)
        else:
            print(f"Execution failed: {execution_result.get('error', 'Unknown error')}")
            print(f"Error output: {execution_result['output']}")
        
        return execution_result
        
    except Exception as e:
        print(f"Manual execution test failed: {str(e)}")
        logger.error(f"Manual execution test failed: {str(e)}")
        return None


async def test_simple_analysis():
    """Test a very simple analysis to verify the execution framework works"""
    
    print("\nSimple Analysis Test")
    print("=" * 50)
    
    # Generate test data
    df = generate_test_data(20)
    data_sample = create_data_sample_from_df(df, "simple_test.csv")
    
    # Convert DataFrame to bytes
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    file_content = csv_buffer.getvalue().encode('utf-8')
    
    # Very simple analysis code
    simple_code = """
import pandas as pd

# Load the data
df = pd.read_csv(data_file)

print("Simple Analysis Results:")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")
print(f"Column names: {list(df.columns)}")
print("First 3 rows:")
print(df.head(3))
print("Analysis complete!")
"""
    
    # Initialize agent service
    agent_service = AgentService()
    
    try:
        print("Executing simple analysis...")
        
        code_result = {
            "code": simple_code,
            "description": "Simple analysis test",
            "agent_name": "simple_test"
        }
        
        execution_result = await agent_service._execute_agent_code(
            agent_name="simple_test",
            code_result=code_result,
            file_content=file_content,
            data_sample=data_sample
        )
        
        print(f"Simple execution completed!")
        print(f"Execution success: {execution_result['success']}")
        
        if execution_result['success']:
            print("Analysis output:")
            print("-" * 30)
            print(execution_result['output'])
            print("-" * 30)
        else:
            print(f"Execution failed: {execution_result.get('error')}")
            print(f"Error output: {execution_result['output']}")
        
        return execution_result
        
    except Exception as e:
        print(f"Simple analysis test failed: {str(e)}")
        logger.error(f"Simple analysis test failed: {str(e)}")
        return None


if __name__ == "__main__":
    print("Starting Code Execution Test Suite...")
    
    try:
        # Run simple analysis test first
        simple_result = asyncio.run(test_simple_analysis())
        
        if simple_result and simple_result['success']:
            print("\nSimple analysis test PASSED!")
        else:
            print("\nSimple analysis test FAILED!")
        
        # Run manual code execution test
        print("\n" + "="*60)
        manual_result = asyncio.run(test_manual_code_execution())
        
        if manual_result and manual_result['success']:
            print("\nManual code execution test PASSED!")
        else:
            print("\nManual code execution test FAILED!")
        
        print("\nTest suite completed!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        logger.error(f"Test execution failed: {str(e)}", exc_info=True)
