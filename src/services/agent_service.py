"""
Agent management and execution service
"""

import yaml
import os
import json
import logging
import asyncio
import subprocess
import tempfile
import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.claude_service import ClaudeService
from utils.data_processor import DataProcessor, clean_nan_values

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing and executing analysis agents"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
        self.data_processor = DataProcessor()
        self.agents = self._load_agents()
        
    def _load_agents(self) -> Dict[str, Any]:
        """Dynamically load agent classes from individual files"""
        agents = {}
        
        try:
            agents_dir = Path(__file__).parent.parent / "agents"
            
            # List of agent modules to load
            agent_modules = [
                # Core Data Operations
                "data_quality_audit",
                "exploratory_data_analysis", 
                "business_intelligence_dashboard",
                "data_cleaning",  # Keep existing for backward compatibility
                "data_visualization",  # Keep existing for backward compatibility
                
                # Customer & Marketing Analytics
                "churn_prediction",
                "customer_segmentation",
                "cohort_analysis",
                "marketing_roi_analysis",
                
                # Sales & Revenue Analytics
                "sales_performance_analysis",
                
                # Financial Analytics
                "profitability_analysis",
                
                # Risk & Fraud Analytics
                "anomaly_detection",
                
                # Advanced Analytics
                "predictive_modeling",
                "ab_testing_analysis",
                
                # Legacy agents (keep for compatibility)
                "regression_analysis",
                "statistical_analysis",
                "time_series_analysis"
            ]
            
            for module_name in agent_modules:
                try:
                    # Import the module
                    module = importlib.import_module(f"agents.{module_name}")
                    
                    # Get the agent class (assumes class name is module_name in CamelCase + Agent)
                    class_name = ''.join(word.capitalize() for word in module_name.split('_')) + 'Agent'
                    agent_class = getattr(module, class_name)
                    
                    # Instantiate the agent
                    agent_instance = agent_class()
                    agents[agent_instance.name] = agent_instance
                    
                    logger.info(f"Loaded agent: {agent_instance.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load agent {module_name}: {str(e)}")
            
            logger.info(f"Successfully loaded {len(agents)} agents")
            return agents
            
        except Exception as e:
            logger.error(f"Error loading agents: {str(e)}")
            return {}
    
    async def analyze_request(self, file_content: bytes, filename: str, 
                            user_question: str) -> Dict[str, Any]:
        """
        Process an analysis request through the complete agent workflow
        
        Args:
            file_content: Raw file content
            filename: Original filename
            user_question: User's analysis question
            
        Returns:
            Complete analysis results
        """
        try:
            # Step 1: Process data sample
            logger.info("Step 1: Processing data sample...")
            data_sample = self.data_processor.read_file_sample(
                file_content, filename, sample_rows=5
            )
            
            # Step 2: Select appropriate agents
            logger.info("Step 2: Selecting agents...")
            selected_agents = await self._select_agents_smart(
                data_sample, user_question
            )
            
            # Step 3: Execute selected agents
            logger.info(f"Step 3: Executing {len(selected_agents)} agents...")
            agent_results = await self._execute_agents(
                selected_agents, data_sample, user_question, file_content
            )
            
            # Step 4: Generate comprehensive report
            logger.info("Step 4: Generating report...")
            report = await self._generate_report(
                data_sample, user_question, selected_agents, agent_results
            )
            
            result = {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "data_sample": data_sample,
                "user_question": user_question,
                "selected_agents": selected_agents,
                "agent_results": agent_results,
                "report": report
            }
            
            # Clean all NaN values to ensure JSON serializability
            return clean_nan_values(result)
            
        except Exception as e:
            logger.error(f"Error in analyze_request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _select_agents_smart(self, data_sample: Dict[str, Any], user_question: str) -> List[str]:
        """
        Smart agent selection using Claude API to analyze data and user request
        
        Args:
            data_sample: Sample data information
            user_question: User's analysis question
            
        Returns:
            List of selected agent names
        """
        try:
            logger.info("Using Claude API for intelligent agent selection...")
            
            # First, try using Claude API for agent selection
            try:
                selected_agents = await self.claude_service.select_agents(data_sample, user_question)
                if selected_agents and len(selected_agents) > 0:
                    logger.info(f"Claude selected agents: {selected_agents}")
                    return selected_agents
            except Exception as claude_error:
                logger.warning(f"Claude API selection failed: {str(claude_error)}")
            
            # Fallback: Use individual agent scoring logic
            logger.info("Using fallback agent scoring logic...")
            agent_scores = []
            
            # Calculate match scores for each agent
            for agent_name, agent in self.agents.items():
                confidence = agent.matches_request(user_question, data_sample['columns'])
                agent_scores.append((agent_name, confidence))
                logger.info(f"Agent {agent_name} confidence: {confidence:.2f}")
            
            # Sort by confidence score (descending)
            agent_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select top 3 agents with confidence > 0.2
            selected_agents = []
            for agent_name, score in agent_scores:
                if score > 0.2 and len(selected_agents) < 3:
                    selected_agents.append(agent_name)
            
            # Final fallback: if no agents selected, use defaults
            if not selected_agents:
                selected_agents = ["data_cleaning", "data_visualization", "statistical_analysis"]
            
            logger.info(f"Fallback selected agents: {selected_agents}")
            return selected_agents
            
        except Exception as e:
            logger.error(f"Error in smart agent selection: {str(e)}")
            # Ultimate fallback to default agents
            return ["data_cleaning", "data_visualization", "statistical_analysis"]
    
    async def _execute_agents(self, agent_names: List[str], data_sample: Dict[str, Any], 
                            user_question: str, file_content: bytes) -> List[Dict[str, Any]]:
        """Execute the selected agents"""
        results = []
        
        for agent_name in agent_names:
            try:
                logger.info(f"Executing agent: {agent_name}")
                
                # Get agent instance
                agent = self.agents.get(agent_name)
                
                if not agent:
                    logger.warning(f"No agent found for: {agent_name}")
                    continue
                
                # Generate code for this agent using its specific prompt
                code_result = await self._generate_agent_code(
                    agent, data_sample, user_question
                )
                
                # Execute the generated code
                execution_result = await self._execute_agent_code(
                    agent_name, code_result, file_content, data_sample
                )
                
                results.append({
                    "agent_name": agent_name,
                    "agent_info": {
                        "display_name": agent.display_name,
                        "description": agent.description,
                        "specialties": agent.specialties
                    },
                    "code_result": code_result,
                    "execution_result": execution_result,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error executing agent {agent_name}: {str(e)}")
                results.append({
                    "agent_name": agent_name,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return results
    
    async def _generate_agent_code(self, agent: Any, data_sample: Dict[str, Any], 
                                 user_question: str) -> Dict[str, Any]:
        """
        Generate code for a specific agent using its own prompt
        
        Args:
            agent: Agent instance with get_analysis_prompt method
            data_sample: Sample data information
            user_question: User's analysis question
            
        Returns:
            Dict containing generated code and metadata
        """
        try:
            # Get the agent-specific prompt
            prompt = agent.get_analysis_prompt(data_sample, user_question)
            
            # Use Claude to generate the code
            response = await self.claude_service._call_claude_api(prompt)
            
            # Parse the response
            code_result = self.claude_service._parse_code_generation_response(response)
            
            logger.info(f"Generated code for agent: {agent.name}")
            return code_result
            
        except Exception as e:
            logger.error(f"Error generating code for {agent.name}: {str(e)}")
            return {
                "error": str(e),
                "agent_name": agent.name,
                "code": "# Error: Could not generate code",
                "description": "Failed to generate code",
                "outputs": [],
                "insights": "Analysis could not be completed"
            }
    
    async def _execute_agent_code(self, agent_name: str, code_result: Dict[str, Any], 
                                file_content: bytes, data_sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Python code generated by an agent in a safe environment
        
        Args:
            agent_name: Name of the agent
            code_result: Generated code and metadata
            file_content: Original file content
            data_sample: Data sample information
            
        Returns:
            Execution results
        """
        try:
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Save the original data file
                file_extension = Path(data_sample['file_info']['filename']).suffix
                data_file_path = temp_path / f"data{file_extension}"
                
                with open(data_file_path, 'wb') as f:
                    f.write(file_content)
                
                # Create the Python script
                script_content = self._create_execution_script(
                    code_result['code'], str(data_file_path), temp_path
                )
                
                script_path = temp_path / f"{agent_name}_analysis.py"
                
                # Log the generated script for debugging
                logger.info(f"Generated script for {agent_name}:")
                logger.info("=" * 50)
                logger.info(script_content)
                logger.info("=" * 50)
                
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                # Execute the script
                logger.info(f"Executing script for agent {agent_name}")
                result = await self._run_python_script(script_path, temp_path)
                
                logger.info(f"Script execution result for {agent_name}: success={result['success']}")
                if not result["success"]:
                    logger.error(f"Script output for {agent_name}: {result['output']}")
                    logger.error(f"Script error for {agent_name}: {result.get('error')}")
                
                # Collect generated files
                output_files = self._collect_output_files(temp_path, agent_name)
                logger.info(f"Collected {len(output_files)} output files for {agent_name}")
                
                return {
                    "success": result["success"],
                    "output": result["output"],
                    "error": result.get("error"),
                    "execution_time": result.get("execution_time"),
                    "output_files": output_files,
                    "insights": code_result.get("insights", "")
                }
                
        except Exception as e:
            logger.error(f"Error executing code for {agent_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "output_files": [],
                "insights": ""
            }
    
    def _create_execution_script(self, user_code: str, data_file_path: str, 
                               output_dir: Path) -> str:
        """Create a safe execution script wrapper"""
        
        # Properly indent user code to be inside the try block
        indented_user_code = self._indent_code(user_code, "    ")
        
        script_template = f'''
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
import sys
import os
from pathlib import Path

# Set output directory
output_dir = Path(r"{output_dir}")
os.chdir(output_dir)

# Set matplotlib style
plt.style.use('default')
sns.set_palette("husl")

try:
    # Load the data
    data_file = r"{data_file_path}"
    file_extension = Path(data_file).suffix.lower()
    
    if file_extension == '.csv':
        df = pd.read_csv(data_file)
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(data_file)
    else:
        raise ValueError(f"Unsupported file format: {{file_extension}}")
    
    print(f"Data loaded successfully. Shape: {{df.shape}}")
    
    # Execute user code
{indented_user_code}
    
    print("\\nAnalysis completed successfully!")
    
except Exception as e:
    print(f"Error during analysis: {{str(e)}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
        
        return script_template
    
    def _indent_code(self, code: str, indent: str = "    ") -> str:
        """Indent code lines properly"""
        lines = code.split('\n')
        indented_lines = []
        
        for line in lines:
            if line.strip():  # Only indent non-empty lines
                indented_lines.append(indent + line)
            else:
                indented_lines.append(line)  # Keep empty lines as is
        
        return '\n'.join(indented_lines)
    
    async def _run_python_script(self, script_path: Path, working_dir: Path) -> Dict[str, Any]:
        """Run Python script and capture output"""
        try:
            start_time = datetime.utcnow()
            
            # Run the script
            process = await asyncio.create_subprocess_exec(
                'python', str(script_path),
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=os.environ.copy()
            )
            
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 minute timeout
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            output = stdout.decode('utf-8', errors='replace')
            
            return {
                "success": process.returncode == 0,
                "output": output,
                "error": None if process.returncode == 0 else f"Script failed with code {process.returncode}",
                "execution_time": execution_time
            }
            
        except asyncio.TimeoutError:
            logger.error("Script execution timed out")
            return {
                "success": False,
                "output": "",
                "error": "Script execution timed out (5 minutes)",
                "execution_time": 300
            }
        except FileNotFoundError:
            logger.error("Python interpreter not found")
            return {
                "success": False,
                "output": "",
                "error": "Python interpreter not found. Make sure Python is installed and in PATH.",
                "execution_time": 0
            }
        except Exception as e:
            logger.error(f"Error running script: {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": f"Script execution error: {str(e)}",
                "execution_time": 0
            }
    
    def _collect_output_files(self, temp_path: Path, agent_name: str) -> List[Dict[str, Any]]:
        """Collect files generated by the agent execution"""
        output_files = []
        
        try:
            # Look for common output file patterns
            patterns = [
                "*.png", "*.jpg", "*.jpeg", "*.svg",  # Images
                "*.csv", "*.xlsx",  # Data files
                "*.txt", "*.md",  # Text reports
                "*.html",  # HTML reports
            ]
            
            for pattern in patterns:
                for file_path in temp_path.glob(pattern):
                    if file_path.is_file():
                        # Read file content as base64 for images, text for others
                        file_info = {
                            "filename": file_path.name,
                            "size": file_path.stat().st_size,
                            "type": file_path.suffix[1:].lower()
                        }
                        
                        if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                            # For images, we could store as base64 or save to S3
                            with open(file_path, 'rb') as f:
                                import base64
                                file_info["content"] = base64.b64encode(f.read()).decode('utf-8')
                                file_info["encoding"] = "base64"
                        else:
                            # For text files
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    file_info["content"] = f.read()
                                    file_info["encoding"] = "utf-8"
                            except UnicodeDecodeError:
                                # If not text, skip or handle differently
                                file_info["content"] = "Binary file - content not displayed"
                                file_info["encoding"] = "binary"
                        
                        output_files.append(file_info)
            
        except Exception as e:
            logger.error(f"Error collecting output files: {str(e)}")
        
        return output_files
    
    async def _generate_report(self, data_sample: Dict[str, Any], user_question: str,
                             selected_agents: List[str], agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive analysis report"""
        try:
            # Create report prompt
            report_prompt = self._create_report_prompt(
                data_sample, user_question, selected_agents, agent_results
            )
            
            # Use Claude to generate the report
            report_content = await self.claude_service._call_claude_api(report_prompt)
            
            return {
                "content": report_content,
                "summary": self._extract_key_insights(agent_results),
                "recommendations": self._extract_recommendations(agent_results),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                "content": "Error generating report",
                "summary": "Analysis completed with some issues",
                "recommendations": ["Review individual agent results for insights"],
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _create_report_prompt(self, data_sample: Dict[str, Any], user_question: str,
                            selected_agents: List[str], agent_results: List[Dict[str, Any]]) -> str:
        """Create prompt for report generation"""
        
        # Summarize agent results
        agent_summaries = []
        for result in agent_results:
            if "error" not in result:
                agent_summaries.append({
                    "agent": result["agent_name"],
                    "insights": result.get("code_result", {}).get("insights", ""),
                    "success": result.get("execution_result", {}).get("success", False)
                })
        
        return f"""
Generate a comprehensive data analysis report based on the following information:

**Original Question:** "{user_question}"

**Data Overview:**
- File: {data_sample['file_info']['filename']}
- Rows: {data_sample['total_rows']:,}
- Columns: {len(data_sample['columns'])}

**Analysis Performed:**
{json.dumps(agent_summaries, indent=2) if agent_summaries else "No successful analyses completed"}

**Please provide a structured report with:**
1. Executive Summary
2. Key Findings
3. Data Quality Assessment  
4. Insights and Patterns
5. Recommendations
6. Next Steps

Focus on answering the user's original question and providing actionable insights.
"""
    
    def _extract_key_insights(self, agent_results: List[Dict[str, Any]]) -> List[str]:
        """Extract key insights from agent results"""
        insights = []
        
        for result in agent_results:
            if "error" not in result:
                agent_insights = result.get("code_result", {}).get("insights", "")
                if agent_insights:
                    insights.append(f"[{result['agent_name']}] {agent_insights}")
        
        return insights
    
    def _extract_recommendations(self, agent_results: List[Dict[str, Any]]) -> List[str]:
        """Extract recommendations from agent results"""
        recommendations = [
            "Review the detailed analysis results for specific insights",
            "Consider running additional analyses based on initial findings",
            "Validate key findings with domain experts"
        ]
        
        return recommendations
