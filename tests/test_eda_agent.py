#!/usr/bin/env python3
"""
Test script specifically for the Exploratory Data Analysis Agent
Tests agent selection, analysis execution, and output generation
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
import sys
import os
from pathlib import Path
from io import StringIO

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.agent_service import AgentService
from services.claude_service import ClaudeService
from utils.data_processor import DataProcessor
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_complex_test_data(num_rows=1000):
    """Generate complex test data suitable for comprehensive EDA"""
    np.random.seed(42)  # For consistent results
    
    # Generate customer data with realistic patterns
    customer_ids = [f"CUST_{str(i).zfill(4)}" for i in range(1, 301)]  # 300 customers
    
    # Generate dates over last 2 years with seasonal patterns
    start_date = datetime.now() - timedelta(days=730)
    dates = []
    # Seasonal probability distribution (normalize to avoid floating sum issues)
    seasonal_probs = np.array([0.06, 0.06, 0.07, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.09, 0.10, 0.12], dtype=float)
    seasonal_probs = seasonal_probs / seasonal_probs.sum()
    for _ in range(num_rows):
        # Add seasonal bias (more sales in Q4)
        month_bias = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], p=seasonal_probs)
        day_in_year = int((month_bias - 1) * 30 + np.random.randint(0, 30))
        dates.append(start_date + timedelta(days=day_in_year))
    
    # Generate correlated data for realistic patterns
    base_amount = np.random.lognormal(4.2, 0.8, num_rows)  # Base purchase amount
    
    # Create correlation between age and purchase amount
    customer_ages = np.random.randint(18, 75, num_rows)
    age_factor = (customer_ages - 18) / 57  # Normalize to 0-1
    purchase_amount = base_amount * (0.8 + 0.4 * age_factor) + np.random.normal(0, 10, num_rows)
    purchase_amount = np.maximum(purchase_amount, 5)  # Minimum $5
    
    # Create regional patterns
    region_probs = np.array([0.25, 0.30, 0.20, 0.25], dtype=float)
    region_probs = region_probs / region_probs.sum()
    regions = np.random.choice(['North', 'South', 'East', 'West'], num_rows, p=region_probs)
    region_multiplier = {'North': 1.1, 'South': 0.9, 'East': 1.0, 'West': 1.05}
    purchase_amount = purchase_amount * [region_multiplier[r] for r in regions]
    
    # Create product categories with different price ranges
    category_probs = np.array([0.25, 0.20, 0.15, 0.25, 0.15], dtype=float)
    category_probs = category_probs / category_probs.sum()
    categories = np.random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], num_rows, p=category_probs)
    category_multiplier = {'Electronics': 1.5, 'Clothing': 0.8, 'Books': 0.6, 'Home': 1.2, 'Sports': 1.1}
    purchase_amount = purchase_amount * [category_multiplier[c] for c in categories]
    
    data = {
        'customer_id': np.random.choice(customer_ids, num_rows),
        'transaction_date': dates,
        'product_category': categories,
        'purchase_amount': np.round(purchase_amount, 2),
        'quantity': np.random.poisson(2, num_rows) + 1,  # 1-6 items typically
        'customer_age': customer_ages,
        'region': regions,
        'marketing_channel': np.random.choice(
            ['Email', 'Social', 'Direct', 'Referral', 'Paid_Search'],
            num_rows,
            p=(np.array([0.30, 0.20, 0.15, 0.20, 0.15], dtype=float) / np.array([0.30, 0.20, 0.15, 0.20, 0.15], dtype=float).sum())
        ),
        'is_returning_customer': np.random.choice([0, 1], num_rows, p=[0.25, 0.75]),
        'customer_satisfaction': np.random.normal(4.2, 0.8, num_rows),  # 1-5 scale
        'discount_percentage': np.random.exponential(5, num_rows),  # 0-50% typically
        'shipping_cost': np.random.exponential(8, num_rows)
    }
    
    df = pd.DataFrame(data)
    
    # Add some realistic missing values
    missing_indices = np.random.choice(df.index, size=int(0.05 * len(df)), replace=False)
    df.loc[missing_indices, 'customer_satisfaction'] = np.nan
    
    # Add some outliers
    outlier_indices = np.random.choice(df.index, size=int(0.02 * len(df)), replace=False)
    df.loc[outlier_indices, 'purchase_amount'] = df.loc[outlier_indices, 'purchase_amount'] * 3
    
    return df


def create_data_sample_from_df(df, filename="eda_test_data.csv"):
    """Convert DataFrame to format expected by agent service"""
    # Convert to CSV bytes (simulating file upload)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue().encode('utf-8')
    
    # Use DataProcessor to create sample
    data_processor = DataProcessor()
    data_sample = data_processor.read_file_sample(csv_content, filename, sample_rows=10)
    
    return data_sample


async def test_eda_agent_direct():
    """Test EDA agent directly, assuming it's already selected"""
    
    print("🔍 EDA Agent Direct Test")
    print("=" * 50)
    
    # Check Claude API configuration
    print(f"🔑 Claude API Key: {'✅ Configured' if settings.ANTHROPIC_API_KEY else '❌ Missing'}")
    print(f"📋 Claude Model: {settings.CLAUDE_MODEL}")

    # Enforce API key requirement for this test
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is required for this test. Set it in your environment.")
    
    # Generate complex test data
    print("\n📊 Generating complex test dataset for EDA...")
    df = generate_complex_test_data(1000)
    print(f"   - Generated {len(df)} rows with {len(df.columns)} columns")
    print(f"   - Columns: {', '.join(df.columns)}")
    
    # Convert to data sample format
    print("\n🔄 Creating data sample...")
    data_sample = create_data_sample_from_df(df, "eda_test_data.csv")
    print(f"   - Sample rows: {len(data_sample['sample_data'])}")
    print(f"   - Total rows: {data_sample['total_rows']:,}")
    print(f"   - Data types detected: {len(data_sample['data_types'])}")
    
    # Import and initialize EDA agent directly
    print("\n🤖 Initializing EDA Agent...")
    from agents.exploratory_data_analysis import ExploratoryDataAnalysisAgent
    eda_agent = ExploratoryDataAnalysisAgent()
    print(f"   - Agent: {eda_agent.display_name}")
    print(f"   - Description: {eda_agent.description}")
    
    # Test EDA-specific questions
    eda_test_questions = [
        "Explore this dataset and find interesting patterns"
    ]
    
    for i, question in enumerate(eda_test_questions, 1):
        print(f"\n" + "-" * 60)
        print(f"🔍 EDA Test {i}: \"{question}\"")
        print("-" * 60)
        
        try:
            # Test agent matching
            confidence = eda_agent.matches_request(question, data_sample['columns'])
            print(f"✅ Agent Confidence: {confidence:.3f}")
            
            # Test prompt generation
            print("📝 Testing prompt generation...")
            prompt = eda_agent.get_analysis_prompt(data_sample, question)
            print(f"   - Prompt length: {len(prompt)} characters")
            print(f"   - Prompt preview: {prompt[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            logger.error(f"EDA agent test failed: {str(e)}")
    
    print(f"\n🎉 EDA agent direct test completed!")


async def test_eda_analysis_execution():
    """Test actual EDA analysis execution by directly calling the agent"""
    
    print("\n🚀 EDA Analysis Execution Test")
    print("=" * 50)
    
    # Generate test data
    print("📊 Generating test dataset...")
    df = generate_complex_test_data(500)
    data_sample = create_data_sample_from_df(df, "eda_execution_test.csv")
    
    # Initialize EDA agent directly
    from agents.exploratory_data_analysis import ExploratoryDataAnalysisAgent
    eda_agent = ExploratoryDataAnalysisAgent()
    
    # Initialize Claude service
    claude_service = ClaudeService()
    
    # Test question
    question = "Perform comprehensive exploratory data analysis and find interesting patterns"
    
    print(f"🔍 Testing question: \"{question}\"")
    
    try:
        # Generate prompt from EDA agent
        print("📝 Generating EDA prompt...")
        prompt = eda_agent.get_analysis_prompt(data_sample, question)
        
        # Call Claude API directly
        print("⚡ Calling Claude API...")
        result = await claude_service._call_claude_api(prompt)
        
        print("✅ Analysis completed!")
        print(f"📝 Result type: {type(result)}")
        print(f"📊 Result length: {len(result)} characters")
        print(f"💡 Result preview: {result[:300]}...")

        
        
        return result
        
    except Exception as e:
        print(f"❌ Analysis execution failed: {str(e)}")
        logger.error(f"EDA analysis execution failed: {str(e)}")
        return None


def show_sample_data(df):
    """Show sample of the generated data"""
    print("\n📋 Sample Data Preview:")
    print(df.head(3).to_string())
    print(f"\n📊 Data Info:")
    print(f"   - Shape: {df.shape}")
    print(f"   - Memory usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    print(f"   - Missing values: {df.isnull().sum().sum()}")
    print(f"   - Numeric columns: {df.select_dtypes(include=[np.number]).columns.tolist()}")
    print(f"   - Categorical columns: {df.select_dtypes(include=['object']).columns.tolist()}")


def test_eda_agent_properties():
    """Test EDA agent properties and basic functionality"""
    
    print("\n🔬 EDA Agent Properties Test")
    print("=" * 30)
    
    # Import the EDA agent directly
    from agents.exploratory_data_analysis import ExploratoryDataAnalysisAgent
    
    # Create agent instance
    eda_agent = ExploratoryDataAnalysisAgent()
    
    print(f"🤖 Agent: {eda_agent.display_name}")
    print(f"📝 Description: {eda_agent.description}")
    print(f"🎯 Specialties: {', '.join(eda_agent.specialties)}")
    print(f"🔑 Keywords: {', '.join(eda_agent.keywords)}")
    print(f"📊 Output Type: {eda_agent.output_type}")
    print(f"📋 Required Columns: {eda_agent.required_columns}")
    
    # Generate test data
    df = generate_complex_test_data(200)
    data_sample = create_data_sample_from_df(df, "properties_test.csv")
    
    # Test matching with different questions
    test_questions = [
        "explore the data"
    ]
    
    print(f"\n🎯 Testing agent matching:")
    for question in test_questions:
        confidence = eda_agent.matches_request(question, data_sample['columns'])
        print(f"   - \"{question}\": {confidence:.3f}")
    
    # Test prompt generation
    print(f"\n📝 Testing prompt generation:")
    try:
        prompt = eda_agent.get_analysis_prompt(data_sample, "explore this dataset")
        print(f"   ✅ Prompt generated ({len(prompt)} characters)")
        print(f"   📊 Prompt preview: {prompt[:200]}...")
    except Exception as e:
        print(f"   ❌ Prompt generation failed: {str(e)}")


if __name__ == "__main__":
    print("🔧 Starting EDA Agent Test Suite...")
    
    try:
        # Fail fast if API key is missing
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is required for this test. Set it in your environment.")
        
        # Show sample data first
        df = generate_complex_test_data(500)
        show_sample_data(df)
        
        # Test agent properties
        test_eda_agent_properties()
        
        # Run direct agent test
        asyncio.run(test_eda_agent_direct())
        
        # Run analysis execution test
        result = asyncio.run(test_eda_analysis_execution())
        if result:
            print(f"\n🎉 EDA Analysis Result Retrieved!")
            print(f"📊 Final result length: {len(result)} characters")
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        logger.error(f"Test execution failed: {str(e)}", exc_info=True)
