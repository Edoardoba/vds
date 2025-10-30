"""
Claude API integration service for agent selection and code generation
"""

import json
import logging
import yaml
from typing import Dict, Any, List, Optional
import asyncio
from pathlib import Path
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
        
        # Load configurations dynamically (agents + execution plan)
        self.agent_configs, self.execution_config = self._load_configs()
        
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not found in environment variables")
    
    def _load_configs(self) -> (Dict[str, Any], Dict[str, Any]):
        """Load agent and execution configurations from config.yaml"""
        try:
            # Get the directory where this file is located
            current_dir = Path(__file__).parent
            project_root = current_dir.parent  # Go up one level from services/ to src/
            
            # Try multiple possible paths for the config file
            possible_paths = [
                project_root / "agents" / "config.yaml",  # src/agents/config.yaml
                current_dir / "agents" / "config.yaml",   # services/agents/config.yaml
                Path("agents/config.yaml"),               # agents/config.yaml (relative to cwd)
                Path("src/agents/config.yaml"),           # src/agents/config.yaml (relative to cwd)
            ]
            
            config_data = None
            used_path = None
            
            for config_path in possible_paths:
                try:
                    if config_path.exists():
                        with open(config_path, 'r', encoding='utf-8') as file:
                            config_data = yaml.safe_load(file)
                            used_path = str(config_path)
                            break
                except Exception as e:
                    logger.debug(f"Failed to load from {config_path}: {e}")
                    continue
            
            if config_data is None:
                logger.error(f"Could not find config.yaml in any of these paths: {[str(p) for p in possible_paths]}")
                return {}, {}
            
            agents_config = config_data.get('agents', {})
            execution_config = config_data.get('execution', {})
            return agents_config, execution_config
        except Exception as e:
            logger.error(f"Error loading agent configs: {str(e)}")
            return {}, {}
    
    def _generate_agents_section(self) -> str:
        """Generate the agents section for the prompt dynamically from config"""
        if not self.agent_configs:
            return "No agents available"
        
        agents_text = []
        for i, (agent_key, agent_config) in enumerate(self.agent_configs.items(), 1):
            name = agent_config.get('name', agent_key)
            description = agent_config.get('description', '')
            specialties = agent_config.get('specialties', [])
            
            # Format specialties (limit to top 3 for cleaner prompt)
            specialties_text = ', '.join(specialties[:3])
            
            agent_entry = f"""{i}. **{agent_key}** - {name}
   - Specializes in: {specialties_text}"""
            
            agents_text.append(agent_entry)
        
        return '\n\n'.join(agents_text)
    
    def _analyze_data_patterns(self, data_sample: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data patterns to determine what types of analysis are possible"""
        columns = data_sample.get('columns', [])
        data_types = data_sample.get('data_types', {})
        
        patterns = {
            'has_customer_data': False,
            'has_time_data': False,
            'has_financial_data': False,
            'has_categorical_data': False,
            'has_numerical_data': False,
            'has_id_columns': False,
            'has_text_data': False,
            'has_geographic_data': False
        }
        
        # Analyze column patterns
        for col in columns:
            col_lower = col.lower()
            dtype = str(data_types.get(col, '')).lower()
            
            # Customer/ID patterns
            if any(pattern in col_lower for pattern in ['customer', 'user', 'client', 'id', 'uuid']):
                patterns['has_customer_data'] = True
                patterns['has_id_columns'] = True
            
            # Time patterns
            if any(pattern in col_lower for pattern in ['date', 'time', 'timestamp', 'created', 'updated', 'year', 'month', 'day']):
                patterns['has_time_data'] = True
            
            # Financial patterns
            if any(pattern in col_lower for pattern in ['revenue', 'price', 'cost', 'amount', 'value', 'sales', 'profit', 'margin', 'budget']):
                patterns['has_financial_data'] = True
            
            # Geographic patterns
            if any(pattern in col_lower for pattern in ['location', 'address', 'city', 'state', 'country', 'region', 'zip', 'lat', 'lon']):
                patterns['has_geographic_data'] = True
            
            # Data type analysis
            if dtype in ['object', 'string']:
                patterns['has_categorical_data'] = True
                patterns['has_text_data'] = True
            elif dtype in ['int64', 'float64', 'int32', 'float32']:
                patterns['has_numerical_data'] = True
        
        return patterns
    
    def _prefilter_agents(self, data_sample: Dict[str, Any], user_question: str) -> List[str]:
        """Pre-filter agents based on data compatibility and question relevance"""
        patterns = self._analyze_data_patterns(data_sample)
        question_lower = user_question.lower()
        
        compatible_agents = []
        incompatible_agents = []
        
        for agent_key, agent_config in self.agent_configs.items():
            keywords = agent_config.get('keywords', [])
            specialties = agent_config.get('specialties', [])
            
            # Check if agent is relevant to the question
            question_relevant = any(
                keyword.lower() in question_lower 
                for keyword in keywords + specialties
            )
            
            # Check data compatibility - be more lenient
            data_compatible = True
            required_columns = agent_config.get('required_columns', [])
            
            if required_columns:
                # Only exclude if absolutely incompatible (missing critical data types)
                if 'customer_id' in required_columns and not patterns['has_customer_data']:
                    data_compatible = False
                elif 'date' in required_columns and not patterns['has_time_data']:
                    data_compatible = False
                elif 'revenue' in required_columns and not patterns['has_financial_data']:
                    data_compatible = False
                elif 'location' in required_columns and not patterns['has_geographic_data']:
                    data_compatible = False
            
            # Include agents that are either relevant to question OR compatible with data
            if question_relevant or data_compatible:
                score = 0
                if question_relevant:
                    score += 1.0  # Higher weight for question relevance
                if data_compatible:
                    score += 0.5
                
                compatible_agents.append((agent_key, score))
            else:
                incompatible_agents.append(agent_key)
        
        # Sort by score and return all compatible agents (no arbitrary limit)
        compatible_agents.sort(key=lambda x: x[1], reverse=True)
        return [agent[0] for agent in compatible_agents]
    
    def _resolve_dependencies(self, selected_agents: List[str]) -> List[str]:
        """Resolve agent dependencies and return agents in correct execution order"""
        if not selected_agents:
            return []
        
        # Get all agent configs
        agent_configs = self.agent_configs
        
        # Build dependency graph
        resolved = []
        remaining = set(selected_agents)
        
        while remaining:
            # Find agents with no unresolved dependencies
            ready_agents = []
            for agent in remaining:
                dependencies = agent_configs.get(agent, {}).get('dependencies', [])
                # Check if all dependencies are resolved OR not in selected agents
                unresolved_deps = [dep for dep in dependencies if dep not in resolved and dep in selected_agents]
                if not unresolved_deps:
                    ready_agents.append(agent)
            
            if not ready_agents:
                # Circular dependency or missing dependency - add remaining agents
                logger.warning(f"Circular dependency detected or missing dependencies for: {remaining}")
                resolved.extend(sorted(remaining))
                break
            
            # Add ready agents in alphabetical order for consistency
            ready_agents.sort()
            resolved.extend(ready_agents)
            remaining -= set(ready_agents)
        
        return resolved
    
    def _generate_filtered_agents_section(self, agent_keys: List[str]) -> str:
        """Generate agents section for only the filtered agents"""
        if not agent_keys:
            return "No compatible agents found"
        
        agents_text = []
        for i, agent_key in enumerate(agent_keys, 1):
            if agent_key in self.agent_configs:
                agent_config = self.agent_configs[agent_key]
                name = agent_config.get('name', agent_key)
                specialties = agent_config.get('specialties', [])
                
                # Format specialties (limit to top 3 for cleaner prompt)
                specialties_text = ', '.join(specialties[:3])
                
                agent_entry = f"""{i}. **{agent_key}** - {name}
   - Specializes in: {specialties_text}"""
                
                agents_text.append(agent_entry)
        
        return '\n\n'.join(agents_text)
    
    def _format_pattern_summary(self, patterns: Dict[str, Any]) -> str:
        """Format data patterns into a readable summary"""
        detected_patterns = []
        
        if patterns['has_customer_data']:
            detected_patterns.append("[+] Customer/ID data detected")
        if patterns['has_time_data']:
            detected_patterns.append("[+] Time series data detected")
        if patterns['has_financial_data']:
            detected_patterns.append("[+] Financial/revenue data detected")
        if patterns['has_geographic_data']:
            detected_patterns.append("[+] Geographic/location data detected")
        if patterns['has_categorical_data']:
            detected_patterns.append("[+] Categorical/text data detected")
        if patterns['has_numerical_data']:
            detected_patterns.append("[+] Numerical data detected")
        
        if not detected_patterns:
            return "No specific patterns detected - general analysis agents recommended"
        
        return '\n'.join(detected_patterns)
    
    def _get_default_agents(self) -> List[str]:
        """Get default agents for fallback scenarios"""
        # Try to use common agents from config, fallback to hardcoded if config not available
        if self.agent_configs:
            # Prefer these agents in order of preference
            preferred_agents = [
                "data_quality_audit", "exploratory_data_analysis", "statistical_analysis"
            ]
            
            # Return all available agents from preferred list (no arbitrary limit)
            available_defaults = [agent for agent in preferred_agents if agent in self.agent_configs]
            if available_defaults:
                return available_defaults
        
        # Fallback to hardcoded defaults if config not available
        return ["data_quality_audit", "exploratory_data_analysis", "statistical_analysis"]
    
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
            
            # Resolve dependencies and return agents in correct execution order
            ordered_agents = self._resolve_dependencies(agent_names)
            
            logger.info(f"Selected agents: {agent_names}")
            logger.info(f"Execution order: {ordered_agents}")
            return ordered_agents
            
        except Exception as e:
            logger.error(f"Error selecting agents: {str(e)}")
            # Fallback to default agents
            return self._get_default_agents()
    
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
        
        # Simple retry with exponential backoff
        last_err: Optional[Exception] = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        self.base_url,
                        headers=headers,
                        json=payload
                    )
                if response.status_code == 200:
                    result = response.json()
                    return result["content"][0]["text"]
                else:
                    msg = f"Claude API error: {response.status_code} - {response.text[:300]}"
                    last_err = Exception(msg)
                    logger.warning(msg)
            except Exception as e:
                last_err = e
                logger.warning(f"Claude API call failed (attempt {attempt+1}/3): {e}")
            # backoff
            await asyncio.sleep(0.5 * (2 ** attempt))
        # If we reached here, all retries failed
        raise last_err if last_err else Exception("Claude API error: unknown")
    
    def _create_agent_selection_prompt(self, data_sample: Dict[str, Any], user_question: str) -> str:
        """Create prompt for agent selection"""
        
        # Pre-filter agents based on data patterns and question relevance
        compatible_agents = self._prefilter_agents(data_sample, user_question)
        
        # Generate agent list only for compatible agents
        agents_section = self._generate_filtered_agents_section(compatible_agents)
        
        # Analyze data patterns for additional context
        patterns = self._analyze_data_patterns(data_sample)
        pattern_summary = self._format_pattern_summary(patterns)
        
        return f"""
You are an expert data analyst tasked with selecting the most appropriate AI analysis agents for a specific data analysis request.

**Data Overview:**
- File: {data_sample['file_info']['filename']}
- Total rows: {data_sample['total_rows']:,}
- Columns: {len(data_sample['columns'])} ({', '.join(data_sample['columns'])})

**Data Patterns Detected:**
{pattern_summary}

**Sample Data (first {len(data_sample['sample_data'])} rows):**
{json.dumps(data_sample['sample_data'], indent=2)}

**Data Types:**
{json.dumps(data_sample['data_types'], indent=2)}

**Missing Values Summary:**
{json.dumps(data_sample['missing_values'], indent=2)}

**User's Analysis Request:**
"{user_question}"

**Most Compatible AI Agents (pre-filtered based on your data and question):**

{agents_section}

**Selection Criteria:**
1. **Relevance**: Which agents directly address the user's question?
2. **Data Compatibility**: Which agents can work with the detected data patterns?
3. **Value**: What combination provides the most comprehensive insights?
4. **Dependencies**: Some analyses build on others (e.g., quality audit before analysis)

**Instructions:**
- Select ALL agents that would be helpful to answer the user's question
- There is no minimum or maximum - select as many or as few as needed
- The system will automatically resolve dependencies and execution order
- Consider data_quality_audit if data quality issues are evident
- Include exploratory_data_analysis for most requests as it provides crucial insights
- Prioritize agents that directly answer the user's question
- Don't worry about execution order - dependencies will be resolved automatically
- Don't limit yourself - if multiple agents would provide valuable insights, include them all

**Execution Stages:**
- Data Preparation: data_quality_audit, data_cleaning
- Exploration: exploratory_data_analysis, data_visualization  
- Analysis: statistical_analysis, regression_analysis, predictive_modeling, specialized analysis agents
- Reporting: data_visualization, statistical_analysis

Respond with ONLY a JSON array of agent names (order will be resolved automatically):

Example: ["data_quality_audit", "exploratory_data_analysis", "customer_segmentation", "revenue_forecasting"]

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

CRITICAL: The "code" field must be a VALID JSON string with ALL newlines escaped as \\n. Do NOT include actual newlines in the JSON.

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
                logger.info(f"Parsed agent names: {agent_names}")
                
                # Validate agent names against available agents from config
                valid_agents = list(self.agent_configs.keys())
                logger.info(f"Valid agents from config: {valid_agents}")
                
                filtered_agents = [name for name in agent_names if name in valid_agents]
                logger.info(f"Filtered agents: {filtered_agents}")
                
                if not filtered_agents:
                    logger.warning(f"No valid agents found. Claude returned: {agent_names}, but config has: {valid_agents}")
                
                return filtered_agents  # Return all valid agents (no arbitrary limit)
            
            else:
                logger.warning("Could not parse agent selection response, using defaults")
                return self._get_default_agents()
                
        except Exception as e:
            logger.error(f"Error parsing agent selection: {str(e)}")
            return self._get_default_agents()
    
    def _parse_code_generation_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's code generation response"""
        try:
            # Extract JSON from response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx+1]
                
                # Try to parse JSON
                try:
                    code_result = json.loads(json_str)
                except json.JSONDecodeError as e:
                    # Try to fix common JSON issues
                    logger.warning(f"JSON parse failed, attempting repair...")
                    json_str = self._repair_json(json_str)
                    code_result = json.loads(json_str)
                
                # Validate required fields
                required_fields = ["code", "description", "outputs", "insights"]
                for field in required_fields:
                    if field not in code_result:
                        code_result[field] = ""
                
                # Validate that code is not empty
                if not code_result.get("code", "").strip():
                    logger.warning("Generated code is empty, using fallback")
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
                
                return code_result
            
            else:
                logger.error("Could not find JSON in code generation response")
                return self._create_fallback_code_result("Failed to parse JSON from response")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            # Log full response for debugging
            logger.error(f"Full response (first 1000 chars): {response[:1000]}")
            return self._create_fallback_code_result(f"JSON decode error: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing code generation: {str(e)}")
            return self._create_fallback_code_result(f"Parse error: {str(e)}")
    
    def _repair_json(self, json_str: str) -> str:
        """Attempt to repair common JSON issues with unescaped newlines"""
        import re
        import io
        
        # More robust approach: handle multiline strings properly
        # The issue is unescaped newlines inside JSON string values
        
        # Strategy: Find all string fields and escape newlines in them
        lines = json_str.split('\n')
        result_lines = []
        in_string = False
        escape_next = False
        
        for line in lines:
            if escape_next:
                escape_next = False
                result_lines.append(line)
                continue
                
            # Check if line is part of a multiline string
            quote_count = line.count('"') - line.count('\\"')
            
            if in_string:
                # Inside a string - escape the newline at end
                result_lines.append(line + '\\n')
                
                # Check if string ends on this line
                if quote_count % 2 == 1:
                    in_string = False
            else:
                # Not in string, check if string starts
                if quote_count % 2 == 1:
                    in_string = True
                
                result_lines.append(line)
        
        return '\n'.join(result_lines).replace('\\n\\n', '\\n')
    
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
