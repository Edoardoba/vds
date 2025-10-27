#!/usr/bin/env python3
"""
Simple test script to simulate fake data and test agent selection
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

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from services.agent_service import AgentService
from services.claude_service import ClaudeService
from utils.data_processor import DataProcessor
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_fake_sales_data(num_rows=500):
    """Generate realistic fake sales data"""
    np.random.seed(42)  # For consistent results
    
    # Generate customer data
    customer_ids = [f"CUST_{str(i).zfill(4)}" for i in range(1, 201)]  # 200 customers
    
    # Generate dates over last year
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(num_rows)]
    
    data = {
        'customer_id': np.random.choice(customer_ids, num_rows),
        'transaction_date': dates,
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], num_rows),
        'purchase_amount': np.round(np.random.lognormal(4, 1), 2),  # $20-$500 typical range
        'quantity': np.random.randint(1, 5, num_rows),
        'customer_age': np.random.randint(18, 75, num_rows),
        'region': np.random.choice(['North', 'South', 'East', 'West'], num_rows),
        'marketing_channel': np.random.choice(['Email', 'Social', 'Direct', 'Referral'], num_rows),
        'is_returning_customer': np.random.choice([0, 1], num_rows, p=[0.3, 0.7])
    }
    
    df = pd.DataFrame(data)
    
    # Add some missing values (realistic)
    missing_indices = np.random.choice(df.index, size=int(0.03 * len(df)), replace=False)
    df.loc[missing_indices, 'customer_age'] = np.nan
    
    return df


def create_data_sample_from_df(df, filename="test_data.csv"):
    """Convert DataFrame to format expected by agent service"""
    # Convert to CSV bytes (simulating file upload)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue().encode('utf-8')
    
    # Use DataProcessor to create sample
    data_processor = DataProcessor()
    data_sample = data_processor.read_file_sample(csv_content, filename, sample_rows=5)
    
    return data_sample


async def test_agent_selection():
    """Main test function for agent selection"""
    
    print("🚀 VDS Agent Selection Test")
    print("=" * 50)
    
    # Check Claude API configuration
    print(f"🔑 Claude API Key: {'✅ Configured' if settings.ANTHROPIC_API_KEY else '❌ Missing'}")
    print(f"📋 Claude Model: {settings.CLAUDE_MODEL}")
    
    # Generate fake data
    print("\n📊 Generating fake sales dataset...")
    df = generate_fake_sales_data(500)
    print(f"   - Generated {len(df)} rows with {len(df.columns)} columns")
    print(f"   - Columns: {', '.join(df.columns)}")
    
    # Convert to data sample format
    print("\n🔄 Creating data sample...")
    data_sample = create_data_sample_from_df(df, "sales_data.csv")
    print(f"   - Sample rows: {len(data_sample['sample_data'])}")
    print(f"   - Total rows: {data_sample['total_rows']:,}")
    print(f"   - Data types detected: {len(data_sample['data_types'])}")
    
    # Initialize agent service
    print("\n🤖 Initializing Agent Service...")
    agent_service = AgentService()
    print(f"   - Loaded {len(agent_service.agents)} agents")
    
    # Test different user questions
    test_questions = [
        "Analyze customer purchasing patterns and identify high-value segments",
        "Show me sales trends and predict future performance", 
        "Which customers are at risk of churning?",
        "Visualize the data and find interesting patterns",
        "Analyze cash flow and financial performance"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n" + "-" * 60)
        print(f"🔍 Test {i}: \"{question}\"")
        print("-" * 60)
        
        try:
            # Test agent selection
            selected_agents = await agent_service._select_agents_smart(data_sample, question)
            
            print(f"✅ Selected Agents: {selected_agents}")
            
            # Show agent details
            print("📝 Agent Details:")
            for j, agent_name in enumerate(selected_agents, 1):
                if agent_name in agent_service.agents:
                    agent = agent_service.agents[agent_name]
                    print(f"   {j}. {agent.display_name}")
                    print(f"      └─ {agent.description[:80]}...")
                else:
                    print(f"   {j}. {agent_name} (not found)")
            
            # Show individual agent confidence scores (fallback method)
            print("🎯 Agent Confidence Scores:")
            scores = []
            for agent_name, agent in agent_service.agents.items():
                try:
                    confidence = agent.matches_request(question, data_sample['columns'])
                    if confidence > 0:
                        scores.append((agent_name, confidence))
                except Exception as e:
                    continue
            
            # Show top 5 scores
            scores.sort(key=lambda x: x[1], reverse=True)
            for agent_name, score in scores[:5]:
                print(f"   - {agent_name}: {score:.3f}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            logger.error(f"Agent selection failed: {str(e)}")
    
    print(f"\n🎉 Agent selection test completed!")
    print(f"💡 To test full analysis, run the analyze_request method")


def show_sample_data(df):
    """Show sample of the generated data"""
    print("\n📋 Sample Data Preview:")
    print(df.head(3).to_string())
    print(f"\n📊 Data Info:")
    print(f"   - Shape: {df.shape}")
    print(f"   - Memory usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    print(f"   - Missing values: {df.isnull().sum().sum()}")


if __name__ == "__main__":
    print("🔧 Starting VDS Agent Selection Test...")
    
    try:
        # Show sample data first
        df = generate_fake_sales_data(500)
        show_sample_data(df)
        
        # Run agent selection test
        asyncio.run(test_agent_selection())
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        logger.error(f"Test execution failed: {str(e)}", exc_info=True)
