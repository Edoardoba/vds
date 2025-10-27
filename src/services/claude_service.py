"""
Claude API integration service for agent selection and code generation
"""

import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Claude API"""
    
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.CLAUDE_MAX_TOKENS
        self.temperature = settings.CLAUDE_TEMPERATURE
        self.base_url = "https://api.anthropic.com/v1/messages"
        
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not found in environment variables")
    
    async def select_agents(self, data_sample: Dict[str, Any], user_question: str) -> List[str]:
        """
        Use Claude to select appropriate agents based on data sample and user question
        
        Args:
            data_sample: Sample data from DataProcessor
            user_question: User's analysis question
            
        Returns:
            List of selected agent names
        """
        try:
            prompt = self._create_agent_selection_prompt(data_sample, user_question)
            
            response = await self._call_claude_api(prompt)
            
            # Parse the JSON response to get agent names
            agent_names = self._parse_agent_selection_response(response)
            
            logger.info(f"Selected agents: {agent_names}")
            return agent_names
            
        except Exception as e:
            logger.error(f"Error selecting agents: {str(e)}")
            # Fallback to default agents
            return ["data_cleaning", "data_visualization", "statistical_analysis"]
    
    async def generate_agent_code(self, agent_name: str, agent_config: Dict[str, Any], 
                                data_sample: Dict[str, Any], user_question: str) -> Dict[str, Any]:
        """
        Generate Python code for a specific agent to execute
        
        Args:
            agent_name: Name of the agent
            agent_config: Agent configuration from YAML
            data_sample: Sample data
            user_question: User's question
            
        Returns:
            Dict containing generated code and metadata
        """
        try:
            prompt = self._create_code_generation_prompt(
                agent_name, agent_config, data_sample, user_question
            )
            
            response = await self._call_claude_api(prompt)
            
            # Parse the code generation response
            code_result = self._parse_code_generation_response(response)
            
            logger.info(f"Generated code for agent: {agent_name}")
            return code_result
            
        except Exception as e:
            logger.error(f"Error generating code for {agent_name}: {str(e)}")
            return {
                "error": str(e),
                "agent_name": agent_name,
                "code": "",
                "description": "Failed to generate code"
            }
    
    async def _call_claude_api(self, prompt: str) -> str:
        """
        Make API call to Claude
        
        Args:
            prompt: The prompt to send to Claude
            
        Returns:
            Claude's response text
        """
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                raise Exception(f"Claude API error: {response.status_code}")
            
            result = response.json()
            return result["content"][0]["text"]
    
    def _create_agent_selection_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Create prompt for agent selection"""
        
        return f"""
You are an expert data analyst tasked with selecting the most appropriate AI analysis agents for a specific data analysis request.

**Data Overview:**
- File: {data_sample['file_info']['filename']}
- Total rows: {data_sample['total_rows']:,}
- Columns: {len(data_sample['columns'])} ({', '.join(data_sample['columns'])})

**Sample Data (first {len(data_sample['sample_data'])} rows):**
{json.dumps(data_sample['sample_data'], indent=2)}

**Data Types:**
{json.dumps(data_sample['data_types'], indent=2)}

**Missing Values Summary:**
{json.dumps(data_sample['missing_values'], indent=2)}

**User's Analysis Request:**
"{user_question}"

**Available Specialized AI Agents:**

1. **churn_analysis** - Customer Churn Prediction
   - Specializes in: churn prediction, customer retention analysis, customer lifetime value, attrition modeling
   - Best for: Questions about customer leaving, subscription cancellations, retention strategies
   - Requires: customer_id column and behavioral/transaction data

2. **data_cleaning** - Data Quality & Preprocessing  
   - Specializes in: missing value handling, outlier detection, duplicate removal, data standardization
   - Best for: Data quality issues, preprocessing needs, inconsistent data formats
   - Universal: Can work with any dataset to improve quality

3. **data_visualization** - Exploratory Data Analysis
   - Specializes in: statistical visualization, correlation analysis, distribution analysis, trend identification
   - Best for: Understanding data patterns, exploring relationships, creating charts and graphs
   - Universal: Valuable for most analysis requests to understand data structure

4. **customer_segmentation** - Customer Clustering
   - Specializes in: k-means clustering, behavioral segmentation, RFM analysis, market segmentation  
   - Best for: Grouping customers, identifying personas, targeted marketing analysis
   - Requires: customer_id and behavioral/demographic features

5. **regression_analysis** - Predictive Modeling
   - Specializes in: linear/non-linear regression, feature importance, predictive modeling
   - Best for: Predicting continuous values, understanding variable relationships, forecasting
   - Requires: numerical target variables and predictor features

6. **statistical_analysis** - Statistical Testing
   - Specializes in: hypothesis testing, t-tests, correlation analysis, statistical significance
   - Best for: Comparing groups, testing relationships, statistical validation
   - Works with: any numerical or categorical data for statistical comparisons

7. **time_series_analysis** - Temporal Analysis
   - Specializes in: trend analysis, seasonality detection, time-based forecasting, ARIMA modeling
   - Best for: Time-based patterns, forecasting future values, temporal trends
   - Requires: date/time columns and time-ordered data

**Selection Criteria:**
1. **Relevance**: Which agents directly address the user's question?
2. **Data Compatibility**: Which agents can work with the available data columns/types?
3. **Value**: What combination provides the most comprehensive insights?
4. **Dependencies**: Some analyses build on others (e.g., cleaning before visualization)

**Instructions:**
- Select 2-4 agents maximum for optimal analysis depth
- Always consider data_cleaning if data quality issues are evident
- Include data_visualization for most requests as it provides crucial insights
- Prioritize agents that directly answer the user's question
- Consider the sequence: cleaning → exploration → specialized analysis

Respond with ONLY a JSON array of agent names in execution order:

Example: ["data_cleaning", "data_visualization", "statistical_analysis"]

Response (JSON array only):"""
    
    def _create_code_generation_prompt(self, agent_name: str, agent_config: Dict[str, Any], 
                                     data_sample: Dict[str, Any], user_question: str) -> str:
        """Create prompt for code generation"""
        
        return f"""
You are a Python data analysis expert. Generate complete, production-ready Python code for the following analysis task.

**Agent: {agent_name}**
Description: {agent_config.get('description', '')}
Specialties: {', '.join(agent_config.get('specialties', []))}

**Data Information:**
- File: {data_sample['file_info']['filename']}
- Total rows: {data_sample['total_rows']:,}
- Columns: {', '.join(data_sample['columns'])}
- Data types: {json.dumps(data_sample['data_types'], indent=2)}

**Sample Data:**
{json.dumps(data_sample['sample_data'], indent=2)}

**User Question:**
"{user_question}"

**Requirements:**
1. Generate complete Python code that can be executed immediately
2. Include all necessary imports
3. Assume the data is available as a pandas DataFrame named 'df'
4. Save results to appropriate files (CSV, images, etc.)
5. Include error handling and logging
6. Add comprehensive comments explaining the analysis
7. Generate insights and key findings as text
8. Return a summary of what was accomplished

**Code Structure:**
- Start with imports
- Include data validation
- Perform the analysis specific to this agent
- Generate visualizations if applicable  
- Save outputs to files
- Return summary and insights

Please respond with ONLY a JSON object containing:
{{
    "code": "complete Python code here",
    "description": "What this code does",
    "outputs": ["list of files that will be created"],
    "insights": "Key insights and findings from this analysis"
}}

Response (JSON only):"""
    
    def _parse_agent_selection_response(self, response: str) -> List[str]:
        """Parse Claude's agent selection response"""
        try:
            # Try to extract JSON array from response
            response = response.strip()
            
            # Handle cases where response might have extra text
            start_idx = response.find('[')
            end_idx = response.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                agent_names = json.loads(json_str)
                
                # Validate agent names
                valid_agents = [
                    "churn_analysis", "data_cleaning", "data_visualization",
                    "customer_segmentation", "regression_analysis", 
                    "statistical_analysis", "time_series_analysis"
                ]
                
                filtered_agents = [name for name in agent_names if name in valid_agents]
                return filtered_agents[:3]  # Limit to 3 agents max
            
            else:
                logger.warning("Could not parse agent selection response, using defaults")
                return ["data_cleaning", "data_visualization", "statistical_analysis"]
                
        except Exception as e:
            logger.error(f"Error parsing agent selection: {str(e)}")
            return ["data_cleaning", "data_visualization", "statistical_analysis"]
    
    def _parse_code_generation_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's code generation response"""
        try:
            # Extract JSON from response
            response = response.strip()
            logger.info(f"Raw Claude response for code generation: {response[:500]}...")
            
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                logger.info(f"Extracted JSON: {json_str[:200]}...")
                
                code_result = json.loads(json_str)
                
                # Validate required fields
                required_fields = ["code", "description", "outputs", "insights"]
                for field in required_fields:
                    if field not in code_result:
                        code_result[field] = ""
                        logger.warning(f"Missing field '{field}' in code generation response")
                
                # Validate that code is not empty
                if not code_result.get("code", "").strip():
                    logger.warning("Generated code is empty")
                    code_result["code"] = """
# Simple fallback analysis
print("Performing basic data analysis...")
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Data types:\\n{df.dtypes}")
print(f"Missing values:\\n{df.isnull().sum()}")
if len(df.select_dtypes(include=[np.number]).columns) > 0:
    print(f"Numerical summary:\\n{df.describe()}")
"""
                
                logger.info(f"Successfully parsed code generation for agent")
                return code_result
            
            else:
                logger.warning("Could not find JSON in code generation response")
                return self._create_fallback_code_result("Failed to parse JSON from response")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in code generation: {str(e)}")
            return self._create_fallback_code_result(f"JSON decode error: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing code generation: {str(e)}")
            return self._create_fallback_code_result(f"Parse error: {str(e)}")
    
    def _create_fallback_code_result(self, error_msg: str) -> Dict[str, Any]:
        """Create a fallback code result when parsing fails"""
        return {
            "code": """
# Fallback analysis due to code generation error
print("Performing fallback data analysis...")
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Basic data info
print("\\nData Types:")
print(df.dtypes)

print("\\nMissing Values:")
print(df.isnull().sum())

# Basic statistics for numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    print("\\nNumerical Summary:")
    print(df[numeric_cols].describe())

# Sample data
print("\\nFirst 5 rows:")
print(df.head())

print("\\nBasic analysis completed successfully!")
""",
            "description": f"Fallback analysis - {error_msg}",
            "outputs": [],
            "insights": f"Basic data overview completed. Original error: {error_msg}"
        }
