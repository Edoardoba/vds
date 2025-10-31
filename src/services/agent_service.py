"""
Agent management and execution service
"""

import yaml
import os
import sys
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
from config import settings

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing and executing analysis agents"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
        self.data_processor = DataProcessor()
        self.agents = self._load_agents()
        
    def _load_agents(self) -> Dict[str, Any]:
        """Dynamically load agent classes from individual files with centralized config"""
        agents = {}
        
        try:
            # Load agent configurations from config.yaml
            agent_configs = self._load_agent_configs()
            
            agents_dir = Path(__file__).parent.parent / "agents"
            
            # List of agent modules to load
            agent_modules = [
                # Core Data Operations
                "data_quality_audit",
                "exploratory_data_analysis", 
                "data_cleaning",  # Keep existing for backward compatibility
                "data_visualization",  # Keep existing for backward compatibility
                
                # Customer & Marketing Analytics
                "churn_prediction",
                "customer_segmentation",
                "cohort_analysis",
                "marketing_roi_analysis",
                "customer_acquisition_cost_analysis",
                
                # Sales & Revenue Analytics
                "sales_performance_analysis",
                
                # Financial Analytics
                "profitability_analysis",
                "cash_flow_analysis",
                
                # Operational Analytics (SMB Focus)
                "operational_bottleneck_detection",
                "employee_performance_analysis",
                "seasonal_business_planning",
                
                # Risk & Fraud Analytics
                "anomaly_detection",
                
                # Competitive & Market Analytics (SMB Focus)
                "competitive_analysis",
                
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
                    
                    # Overlay metadata from config.yaml if available
                    if module_name in agent_configs:
                        config = agent_configs[module_name]
                        agent_instance.display_name = config.get('name', agent_instance.display_name)
                        agent_instance.description = config.get('description', agent_instance.description)
                        agent_instance.specialties = config.get('specialties', agent_instance.specialties)
                        agent_instance.keywords = config.get('keywords', agent_instance.keywords)
                        agent_instance.output_type = config.get('output_type', agent_instance.output_type)
                        
                        # logger.info(f"Applied config for agent: {agent_instance.name}")
                    
                    agents[agent_instance.name] = agent_instance
                    
                except Exception as e:
                    logger.error(f"Failed to load agent {module_name}: {str(e)}")
            
            logger.info(f"Loaded {len(agents)} analysis agents")
            return agents
            
        except Exception as e:
            logger.error(f"Error loading agents: {str(e)}")
            return {}
    
    def _load_agent_configs(self) -> Dict[str, Any]:
        """Load agent configurations from config.yaml"""
        try:
            config_path = Path(__file__).parent.parent / "agents" / "config.yaml"
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                return config_data.get('agents', {})
        except Exception as e:
            logger.error(f"Error loading agent configs: {str(e)}")
            return {}
    
    async def analyze_request(self, file_content: bytes, filename: str, 
                            user_question: str, selected_agents: Optional[List[str]] = None,
                            progress_callback: Optional[callable] = None) -> Dict[str, Any]:
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
            # Process data sample
            data_sample = self.data_processor.read_file_sample(
                file_content, filename, sample_rows=5
            )
            
            # Select appropriate agents (or use provided override)
            if not (selected_agents and isinstance(selected_agents, list) and len(selected_agents) > 0):
                selected_agents = await self._select_agents_smart(
                    data_sample, user_question
                )
            logger.info(f"Analyzing with {len(selected_agents)} agents: {', '.join(selected_agents)}")
            
            # Execute selected agents
            agent_results = await self._execute_agents(
                selected_agents, data_sample, user_question, file_content, progress_callback
            )
            
            # Generate comprehensive report
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

    async def plan_request(self, file_content: bytes, filename: str, 
                           user_question: str) -> Dict[str, Any]:
        """Plan which agents to run and return data sample plus agent metadata without execution."""
        try:
            # Create data sample
            data_sample = self.data_processor.read_file_sample(
                file_content, filename, sample_rows=5
            )

            # Select agents
            selected_agents = await self._select_agents_smart(data_sample, user_question)

            # Build agent info for the selected agents
            selected_agent_infos: List[Dict[str, Any]] = []
            for agent_name in selected_agents:
                agent = self.agents.get(agent_name)
                if not agent:
                    continue
                selected_agent_infos.append({
                    "name": agent.name,
                    "display_name": getattr(agent, "display_name", agent.name),
                    "description": getattr(agent, "description", ""),
                    "specialties": getattr(agent, "specialties", []),
                    "output_type": getattr(agent, "output_type", "text"),
                })

            return {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "data_sample": data_sample,
                "user_question": user_question,
                "selected_agents": selected_agents,
                "selected_agent_infos": selected_agent_infos,
            }
        except Exception as e:
            logger.error(f"Error in plan_request: {str(e)}")
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
            # First, try using Claude API for agent selection
            try:
                selected_agents = await self.claude_service.select_agents(data_sample, user_question)
                if selected_agents and len(selected_agents) > 0:
                    return selected_agents
            except Exception as claude_error:
                logger.warning(f"Agent selection failed, using fallback: {str(claude_error)}")
            
            # Fallback: Use individual agent scoring logic
            agent_scores = []
            
            # Calculate match scores for each agent
            for agent_name, agent in self.agents.items():
                confidence = agent.matches_request(user_question, data_sample['columns'])
                agent_scores.append((agent_name, confidence))
            
            # Sort by confidence score (descending)
            agent_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select all agents with confidence > 0.2 (no limit)
            selected_agents = []
            for agent_name, score in agent_scores:
                if score > 0.2:
                    selected_agents.append(agent_name)
            
            # Final fallback: if no agents selected, use defaults
            if not selected_agents:
                selected_agents = ["data_cleaning", "data_visualization", "statistical_analysis"]
            
            return selected_agents
            
        except Exception as e:
            logger.error(f"Error in smart agent selection: {str(e)}")
            # Ultimate fallback to default agents
            return ["data_cleaning", "data_visualization", "statistical_analysis"]
    
    async def _execute_agents(self, agent_names: List[str], data_sample: Dict[str, Any], 
                            user_question: str, file_content: bytes, progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """Execute the selected agents with progress updates"""
        results = []
        
        for i, agent_name in enumerate(agent_names):
            try:
                # Emit progress update - agent starting
                if progress_callback:
                    await progress_callback({
                        "type": "agent_started",
                        "agent_name": agent_name,
                        "agent_index": i,
                        "total_agents": len(agent_names),
                        "progress": (i / len(agent_names)) * 100
                    })
                
                # Get agent instance
                agent = self.agents.get(agent_name)
                
                if not agent:
                    logger.warning(f"No agent found for: {agent_name}")
                    if progress_callback:
                        await progress_callback({
                            "type": "agent_error",
                            "agent_name": agent_name,
                            "error": f"Agent {agent_name} not found"
                        })
                    continue
                
                # Check if mock mode is enabled (exclude agent selector)
                if settings.AGENT_MOCK and agent_name != "agent_selector":
                    logger.info(f"Using mock execution for agent: {agent_name}")
                    result = await self._mock_agent_execution(
                        agent_name, agent, data_sample, user_question, progress_callback
                    )
                    results.append(result)
                    continue
                
                # Generate code for this agent using its specific prompt
                code_result = await self._generate_agent_code(
                    agent, data_sample, user_question
                )
                
                # Emit progress update - code generated
                if progress_callback:
                    await progress_callback({
                        "type": "code_generated",
                        "agent_name": agent_name,
                        "progress": ((i + 0.5) / len(agent_names)) * 100
                    })
                
                # Execute the generated code
                execution_result = await self._execute_agent_code(
                    agent_name, code_result, file_content, data_sample
                )
                
                # Check if execution was successful
                if not execution_result.get("success", False):
                    logger.warning(f"Agent {agent_name} execution failed, but continuing with partial results")
                    # Create a result with execution failure but still include generated code
                    execution_result["success"] = False
                    execution_result["error"] = execution_result.get("error", "Code execution failed")
                    
                    # Provide fallback insights from the generated code
                    if not execution_result.get("insights"):
                        execution_result["insights"] = self._generate_fallback_insights(agent_name, code_result)
                
                result = {
                    "agent_name": agent_name,
                    "agent_info": {
                        "display_name": agent.display_name,
                        "description": agent.description,
                        "specialties": agent.specialties
                    },
                    "code_result": code_result,
                    "execution_result": execution_result,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                results.append(result)
                
                # Emit progress update - agent completed (even if with errors)
                if progress_callback:
                    await progress_callback({
                        "type": "agent_completed",
                        "agent_name": agent_name,
                        "agent_index": i,
                        "total_agents": len(agent_names),
                        "progress": ((i + 1) / len(agent_names)) * 100,
                        "result": result,
                        "success": execution_result.get("success", False)
                    })
                
            except Exception as e:
                logger.error(f"Error executing agent {agent_name}: {str(e)}")
                error_result = {
                    "agent_name": agent_name,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                results.append(error_result)
                
                # Emit progress update - agent error
                if progress_callback:
                    await progress_callback({
                        "type": "agent_error",
                        "agent_name": agent_name,
                        "error": str(e),
                        "progress": ((i + 1) / len(agent_names)) * 100
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
            # Create a persistent directory in temp_scripts for inspection
            # Get the src directory (parent of services/)
            src_dir = Path(__file__).parent.parent if Path(__file__).parent.name == 'services' else Path(__file__).parent
            temp_scripts_dir = src_dir / "temp_scripts"
            temp_scripts_dir.mkdir(exist_ok=True)
            
            # Create a unique directory for this execution (using timestamp)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # microseconds to milliseconds
            execution_dir = temp_scripts_dir / f"{agent_name}_{timestamp}"
            execution_dir.mkdir(exist_ok=True)
            temp_path = execution_dir
            
            # Save the original data file
            file_extension = Path(data_sample['file_info']['filename']).suffix
            data_file_path = temp_path / f"data{file_extension}"
            
            with open(data_file_path, 'wb') as f:
                f.write(file_content)
                
            # Sanitize and validate generated code before execution
            raw_user_code = code_result.get('code', '')
            logger.info(f"Generated code length for {agent_name}: {len(raw_user_code)} chars")
            sanitized_user_code = self._sanitize_user_code(raw_user_code)

            is_valid, validation_error = self._validate_generated_code(sanitized_user_code)
            logger.info(f"Code validation for {agent_name}: valid={is_valid}")
            if not is_valid:
                logger.warning(f"Generated code for {agent_name} failed validation: {validation_error}")
                # Attempt minimal newline normalization and re-validate
                sanitized_user_code = sanitized_user_code.replace('\r\n', '\n').replace('\r', '\n')
                is_valid, validation_error = self._validate_generated_code(sanitized_user_code)

                # If still invalid after retry, return error instead of executing broken code
                if not is_valid:
                    logger.error(f"Generated code for {agent_name} is invalid and cannot be executed: {validation_error}")
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Code validation failed: {validation_error}. The generated code may be truncated or contain syntax errors.",
                        "execution_time": 0,
                        "output_files": [],
                        "insights": code_result.get("insights", "")
                    }

            # Create the Python script
            script_content = self._create_execution_script(
                sanitized_user_code, str(data_file_path), temp_path
            )
            
            script_path = temp_path / f"{agent_name}_analysis.py"
            
            # Validate the final script before writing (syntax check only)
            # Note: Security validation was already done on user code, template is trusted
            is_script_valid, script_validation_error = self._validate_script_syntax(script_content)
            if not is_script_valid:
                logger.error(f"Final script for {agent_name} failed syntax validation: {script_validation_error}")
                # Still save the invalid script for inspection
                logger.info(f"Saving invalid script to {script_path} for inspection")
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                return {
                    "success": False,
                    "output": "",
                    "error": f"Generated script contains syntax errors: {script_validation_error}. This usually indicates the AI-generated code was malformed or truncated. Script saved to: {script_path}",
                    "execution_time": 0,
                    "output_files": [],
                    "insights": code_result.get("insights", "")
                }
            
            # Write script to file
            logger.info(f"Writing script to: {script_path}")
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            logger.info(f"Script written successfully, size: {len(script_content)} chars")
            logger.info(f"Script saved for inspection at: {script_path}")
            
            # Execute the script
            logger.info(f"Starting execution of agent {agent_name}")
            result = await self._run_python_script(script_path, temp_path)
            
            if not result["success"]:
                logger.error(f"Agent {agent_name} failed: {result.get('error', 'Unknown error')}")
                if result.get("output"):
                    logger.error(f"Agent {agent_name} error output: {result['output'][:1000]}")
            
            # Collect generated files
            logger.info(f"Collecting output files for {agent_name}")
            output_files = self._collect_output_files(temp_path, agent_name)
            logger.info(f"Found {len(output_files)} output files")
            
            return {
                "success": result["success"],
                "output": result["output"],
                "error": result.get("error"),
                "execution_time": result.get("execution_time"),
                "output_files": output_files,
                "insights": code_result.get("insights", "")
            }
                
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            error_msg = str(e) if str(e) else repr(e)
            logger.error(f"Error executing code for {agent_name}: {error_msg}")
            logger.error(f"Full traceback:\n{error_traceback}")
            return {
                "success": False,
                "error": f"{type(e).__name__}: {error_msg}",
                "output": "",
                "output_files": [],
                "insights": ""
            }
    
    def _create_execution_script(self, user_code: str, data_file_path: str, 
                               output_dir: Path) -> str:
        """Create a safe execution script wrapper"""
        
        # Properly indent user code to be inside the try block
        indented_user_code = self._indent_code(user_code, "    ")
        
        script_template = '''
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Try to import seaborn, but continue without it if unavailable
try:
    import seaborn as sns
    _has_seaborn = True
except ImportError as e:
    print("Warning: seaborn not available - some visualization features may be limited")
    print(f"Import error")
    _has_seaborn = False
    # Create a dummy sns object to avoid NameError
    class _DummySeaborn:
        def set_palette(self, *args, **kwargs):
            pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    sns = _DummySeaborn()

import sys as _sys
import os as _os
from pathlib import Path as _Path
import traceback as _traceback
import time as _time

# Set output directory
output_dir = _Path(r"{output_dir}")
_os.chdir(output_dir)

# Set matplotlib style
plt.style.use('default')
if _has_seaborn:
    try:
        sns.set_palette("husl")
    except Exception as e:
        print(f"Warning: Could not set seaborn palette: ")

# Configure matplotlib for better compatibility
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['savefig.bbox'] = 'tight'

def _auto_save_show(*args, **kwargs):
    try:
        filename = "figure_" + str(int(_time.time()*1000)) + ".png"
        plt.savefig(filename)
        plt.close()
        print("Saved figure: " + filename)
    except Exception as e:
        print("Failed to save figure: " + str(e))

plt.show = _auto_save_show

try:
    # Load the data
    data_file = r"{data_file_path}"
    file_extension = _Path(data_file).suffix.lower()
    
    print("Loading data from: " + str(data_file))
    print("File extension: " + str(file_extension))
    
    if file_extension == '.csv':
        df = pd.read_csv(data_file)
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(data_file)
    else:
        raise ValueError("Unsupported file format: " + str(file_extension))
    
    print("Data loaded successfully. Shape: " + str(df.shape))
    print("Columns: " + str(list(df.columns)))
    print("Data types: " + str(df.dtypes.to_dict()))
    
    # Execute user code
{indented_user_code}
    
    print("Analysis completed successfully!")
    
except Exception as e:
    print("Error during analysis: " + str(e))
    print("Full traceback:")
    _traceback.print_exc()
    _sys.exit(1)
'''
        
        return script_template.format(
            output_dir=output_dir,
            data_file_path=data_file_path,
            indented_user_code=indented_user_code
        )
    
    def _sanitize_user_code(self, code: str) -> str:
        """Remove markdown fencing, magics, and normalize common patterns."""
        try:
            if not isinstance(code, str):
                return ""
            cleaned = code.strip()
            # Remove surrounding triple backtick blocks
            if cleaned.startswith('```') and cleaned.endswith('```'):
                cleaned = cleaned[3:-3].strip()
            # Remove language hint prefix
            if cleaned.lower().startswith('python\n'):
                cleaned = cleaned[7:]
            if cleaned.lower().startswith('```python'):
                cleaned = cleaned[9:].strip()
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3].strip()
            # Strip stray backticks
            cleaned = cleaned.replace('```', '')
            # Comment out Jupyter/IPython magics and shell escapes
            normalized_lines: List[str] = []
            for line in cleaned.split('\n'):
                stripped = line.lstrip()
                if stripped.startswith('%') or stripped.startswith('!'):
                    normalized_lines.append('# ' + line)
                else:
                    normalized_lines.append(line)
            return '\n'.join(normalized_lines)
        except Exception:
            return code if isinstance(code, str) else ""

    def _validate_generated_code(self, code: str) -> (bool, str):
        """Quick AST validation and safety screening for generated code."""
        try:
            import ast
            # Basic syntax check
            ast.parse(code)
            # Safety denylist scan (simple heuristic)
            # Check for dangerous imports/patterns that aren't aliased
            lines = code.split('\n')
            lowered = code.lower()
            forbidden_patterns = [
                ("import sys", True),  # Only block if not aliased
                ("import subprocess", False),
                ("subprocess.", False),
                ("os.system", False),
                ("import socket", False),
                ("import requests", False),
                ("import httpx", False),
                ("import urllib", False),
                ("import ftplib", False),
                ("import paramiko", False),
                ("shutil.rmtree", False),
                ("exec(", False),
                ("eval(", False),
                ("__import__(", False),
            ]
            
            for pattern, check_aliased in forbidden_patterns:
                if pattern in lowered:
                    # If pattern requires aliasing check, verify it's not aliased
                    if check_aliased:
                        # Check if this is an aliased import (e.g., "import sys as _sys")
                        pattern_lower = pattern.lower()
                        found_unsafe = False
                        for line in lines:
                            line_lower = line.lower().strip()
                            # Check if this line contains the pattern
                            if pattern_lower in line_lower:
                                # Check if it's aliased (contains " as ")
                                if " as " in line_lower:
                                    # This is safe (aliased import), skip this match
                                    continue
                                else:
                                    # Found bare import, this is unsafe
                                    found_unsafe = True
                                    break
                        
                        if found_unsafe:
                            return False, f"Forbidden pattern detected in generated code: {pattern} (must use aliased import like 'import sys as _sys')"
                    else:
                        # Pattern is always forbidden
                        return False, f"Forbidden pattern detected in generated code: {pattern}"
            
            return True, ""
        except SyntaxError as e:
            # Provide more detailed syntax error information
            error_msg = f"SyntaxError: {e.msg}"
            if e.lineno:
                error_msg += f" at line {e.lineno}"
            if e.offset:
                error_msg += f", column {e.offset}"
            if e.text:
                error_msg += f"\nLine: {e.text.strip()}"
            return False, error_msg
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_script_syntax(self, code: str) -> (bool, str):
        """Validate only syntax of the final script (no security checks, template is trusted)."""
        try:
            import ast
            # Basic syntax check only
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            # Provide more detailed syntax error information
            error_msg = f"SyntaxError: {e.msg}"
            if e.lineno:
                error_msg += f" at line {e.lineno}"
            if e.offset:
                error_msg += f", column {e.offset}"
            if e.text:
                error_msg += f"\nLine: {e.text.strip()}"
            return False, error_msg
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
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
    
    def _generate_fallback_insights(self, agent_name: str, code_result: Dict[str, Any]) -> str:
        """Generate fallback insights when code execution fails"""
        try:
            # Extract insights from the generated code if available
            if code_result.get("insights"):
                return code_result["insights"]
            
            # Generate basic insights based on agent type
            agent_insights = {
                "data_quality_audit": "Data quality analysis was attempted but execution failed. The generated code includes data profiling, missing value analysis, and data type validation.",
                "exploratory_data_analysis": "Exploratory data analysis was attempted but execution failed. The generated code includes statistical summaries, distribution analysis, and correlation studies.",
                "data_visualization": "Data visualization was attempted but execution failed. The generated code includes various chart types and visual analysis techniques.",
                "statistical_analysis": "Statistical analysis was attempted but execution failed. The generated code includes hypothesis testing, regression analysis, and statistical modeling.",
                "churn_prediction": "Customer churn prediction was attempted but execution failed. The generated code includes machine learning models for churn prediction.",
                "customer_segmentation": "Customer segmentation was attempted but execution failed. The generated code includes clustering algorithms and customer profiling.",
                "sales_performance_analysis": "Sales performance analysis was attempted but execution failed. The generated code includes sales metrics, trend analysis, and performance evaluation.",
                "revenue_forecasting": "Revenue forecasting was attempted but execution failed. The generated code includes time series analysis and predictive modeling.",
                "market_basket_analysis": "Market basket analysis was attempted but execution failed. The generated code includes association rule mining and product recommendation algorithms.",
                "predictive_modeling": "Predictive modeling was attempted but execution failed. The generated code includes machine learning algorithms and model evaluation techniques.",
                "anomaly_detection": "Anomaly detection was attempted but execution failed. The generated code includes outlier detection algorithms and anomaly scoring.",
                "cohort_analysis": "Cohort analysis was attempted but execution failed. The generated code includes customer lifecycle analysis and retention modeling.",
                "ab_testing_analysis": "A/B testing analysis was attempted but execution failed. The generated code includes statistical significance testing and experiment evaluation.",
                "marketing_roi_analysis": "Marketing ROI analysis was attempted but execution failed. The generated code includes campaign performance evaluation and ROI calculations.",
                "profitability_analysis": "Profitability analysis was attempted but execution failed. The generated code includes profit margin analysis and cost optimization.",
                "cash_flow_analysis": "Cash flow analysis was attempted but execution failed. The generated code includes cash flow forecasting and liquidity analysis.",
                "employee_performance_analysis": "Employee performance analysis was attempted but execution failed. The generated code includes performance metrics and productivity analysis.",
                "operational_bottleneck_detection": "Operational bottleneck detection was attempted but execution failed. The generated code includes process analysis and efficiency optimization.",
                "seasonal_business_planning": "Seasonal business planning was attempted but execution failed. The generated code includes seasonal trend analysis and planning algorithms.",
                "competitive_analysis": "Competitive analysis was attempted but execution failed. The generated code includes market positioning and competitive benchmarking.",
                "customer_acquisition_cost_analysis": "Customer acquisition cost analysis was attempted but execution failed. The generated code includes CAC calculations and marketing efficiency analysis."
            }
            
            return agent_insights.get(agent_name, f"Analysis for {agent_name} was attempted but execution failed. The generated code includes relevant analysis techniques for this domain.")
            
        except Exception as e:
            logger.error(f"Error generating fallback insights for {agent_name}: {str(e)}")
            return f"Analysis for {agent_name} was attempted but execution failed. Please check the generated code for the intended analysis approach."
    
    async def _run_python_script(self, script_path: Path, working_dir: Path) -> Dict[str, Any]:
        """Run Python script and capture output"""
        import traceback
        try:
            start_time = datetime.utcnow()
            logger.info(f"Executing Python script: {script_path}")

            # Verify script exists
            if not script_path.exists():
                error_msg = f"Script file not found: {script_path}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "output": "",
                    "error": error_msg,
                    "execution_time": 0
                }

            # Verify working directory exists
            if not working_dir.exists():
                logger.warning(f"Working directory does not exist: {working_dir}, creating it...")
                working_dir.mkdir(parents=True, exist_ok=True)

            # Ensure working_dir is absolute
            working_dir = working_dir.resolve()
            script_path = script_path.resolve()

            logger.info(f"Working directory: {working_dir}")
            logger.info(f"Script path (absolute): {script_path}")
            logger.info(f"sys.executable: {sys.executable}")

            # Verify Python executable exists (for sys.executable)
            if os.path.exists(sys.executable):
                logger.info(f"sys.executable exists: {sys.executable}")
                # Try to get version to verify it works
                try:
                    import subprocess as sp
                    result = sp.run([sys.executable, '--version'], capture_output=True, text=True, timeout=5)
                    logger.info(f"Python version check: {result.stdout.strip()}")
                except Exception as e:
                    logger.warning(f"Could not verify Python version: {e}")
            else:
                logger.warning(f"sys.executable does not exist: {sys.executable}")

            # Try different Python commands, starting with the current interpreter
            # This ensures we use the same Python that's running the application
            python_commands = [sys.executable, 'python', 'python3', 'py']
            last_error = None
            last_traceback = None

            # Run subprocess in executor for better cross-platform compatibility
            # This avoids asyncio subprocess issues on Windows
            def run_script(cmd_str):
                """Run script synchronously in thread"""
                try:
                    logger.info(f"Trying Python command: {cmd_str}")
                    result = subprocess.run(
                        [cmd_str, str(script_path)],
                        cwd=str(working_dir),
                        capture_output=True,
                        timeout=300,  # 5 minute timeout
                        env=os.environ.copy()
                    )
                    return {
                        'success': True,
                        'returncode': result.returncode,
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'cmd': cmd_str
                    }
                except FileNotFoundError as e:
                    return {
                        'success': False,
                        'error': f"Python command not found: {cmd_str}",
                        'exception': e,
                        'traceback': traceback.format_exc()
                    }
                except PermissionError as e:
                    return {
                        'success': False,
                        'error': f"Permission denied for Python command: {cmd_str}",
                        'exception': e,
                        'traceback': traceback.format_exc()
                    }
                except subprocess.TimeoutExpired as e:
                    return {
                        'success': False,
                        'error': f"Script execution timed out after 5 minutes",
                        'exception': e,
                        'traceback': traceback.format_exc()
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f"Failed to start process with {cmd_str}: {type(e).__name__}: {str(e)}",
                        'exception': e,
                        'traceback': traceback.format_exc()
                    }

            # Try each Python command
            result = None
            loop = asyncio.get_event_loop()

            for cmd in python_commands:
                cmd_str = str(cmd)
                if os.path.exists(cmd_str):
                    logger.info(f"Trying Python command (exists): {cmd_str}")
                else:
                    logger.info(f"Trying Python command (will search PATH): {cmd_str}")

                # Run in executor to avoid blocking
                try:
                    result = await loop.run_in_executor(None, run_script, cmd_str)

                    if result['success']:
                        logger.info(f"Successfully executed script using command: {cmd_str}")
                        break
                    else:
                        last_error = result.get('error', 'Unknown error')
                        last_traceback = result.get('traceback', '')
                        logger.warning(f"{last_error}")
                        if last_traceback:
                            logger.error(f"Traceback:\n{last_traceback}")
                        result = None  # Reset for next iteration
                        continue
                except Exception as e:
                    last_error = f"Executor error with {cmd_str}: {str(e)}"
                    last_traceback = traceback.format_exc()
                    logger.error(f"{last_error}\n{last_traceback}")
                    continue

            if result is None or not result['success']:
                commands_tried = ', '.join([str(cmd) for cmd in python_commands])
                error_msg = f"No Python interpreter found. Tried: {commands_tried}"
                if last_error:
                    error_msg += f"\nLast error: {last_error}"
                if last_traceback:
                    logger.error(f"Last error traceback:\n{last_traceback}")
                logger.error(error_msg)
                # Log additional diagnostic info
                logger.error(f"Script path: {script_path}")
                logger.error(f"Script exists: {script_path.exists()}")
                logger.error(f"Working dir: {working_dir}")
                logger.error(f"Working dir exists: {working_dir.exists()}")
                logger.error(f"sys.executable: {sys.executable}")
                logger.error(f"sys.executable exists: {os.path.exists(sys.executable) if sys.executable else False}")
                return {
                    "success": False,
                    "output": "",
                    "error": error_msg,
                    "execution_time": 0
                }

            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            # Decode both stdout and stderr
            output = result['stdout'].decode('utf-8', errors='replace') if result['stdout'] else ""
            stderr_output = result['stderr'].decode('utf-8', errors='replace') if result['stderr'] else ""

            # Combine output and stderr
            full_output = output
            if stderr_output:
                full_output = f"{output}\n--- STDERR ---\n{stderr_output}" if output else stderr_output

            logger.info(f"Script execution completed with return code: {result['returncode']}, took {execution_time:.2f}s")

            # Log output for debugging
            if full_output:
                logger.debug(f"Script output (first 1000 chars): {full_output[:1000]}")
            if result['returncode'] != 0:
                logger.error(f"Script failed with return code {result['returncode']}")
                if stderr_output:
                    logger.error(f"Script stderr (first 1000 chars): {stderr_output[:1000]}")

            return {
                "success": result['returncode'] == 0,
                "output": full_output,
                "error": None if result['returncode'] == 0 else (
                    stderr_output[:500] if stderr_output else f"Script failed with code {result['returncode']}"
                ),
                "execution_time": execution_time
            }

        except Exception as e:
            error_traceback = traceback.format_exc()
            error_msg = f"Script execution error: {str(e)}\n{error_traceback}"
            logger.error(f"Error running script: {error_msg}")
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
                            # For images, embed base64 only if reasonably small (<=200KB)
                            if file_path.stat().st_size <= 200_000:
                                with open(file_path, 'rb') as f:
                                    import base64
                                    file_info["content"] = base64.b64encode(f.read()).decode('utf-8')
                                    file_info["encoding"] = "base64"
                            else:
                                file_info["content"] = None
                                file_info["encoding"] = "omitted-large"
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
    
    async def _mock_agent_execution(self, agent_name: str, agent: Any, data_sample: Dict[str, Any], 
                                  user_question: str, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Mock agent execution that returns sample text with 3-second delay
        
        Args:
            agent_name: Name of the agent
            agent: Agent instance
            data_sample: Sample data information
            user_question: User's analysis question
            progress_callback: Optional progress callback
            
        Returns:
            Mock execution results
        """
        try:
            logger.info(f"Mock execution for agent: {agent_name}")
            
            # Minimal delay for mock execution (reduced from 3s to 0.1s for faster testing)
            await asyncio.sleep(0.1)
            
            # Create mock result
            mock_result = {
                "agent_name": agent_name,
                "agent_info": {
                    "display_name": agent.display_name,
                    "description": agent.description,
                    "specialties": agent.specialties
                },
                "code_result": {
                    "code": f"# Mock code for {agent_name}\nprint('This is mock analysis for {agent_name}')\n# Sample text analysis",
                    "description": f"Mock analysis for {agent_name}",
                    "outputs": ["sample_text"],
                    "insights": f"This is sample text analysis for {agent_name}. The mock analysis shows typical patterns and insights that would be generated by this agent."
                },
                "execution_result": {
                    "success": True,
                    "output": f"Mock execution completed for {agent_name}\nSample text: This is sample text analysis for {agent_name}",
                    "error": None,
                    "execution_time": 3.0,
                    "output_files": [],
                    "insights": f"This is sample text analysis for {agent_name}. The mock analysis shows typical patterns and insights that would be generated by this agent."
                },
                "timestamp": datetime.utcnow().isoformat(),
                "success": True
            }
            
            # Send progress update if callback provided
            if progress_callback:
                await progress_callback({
                    "type": "agent_completed",
                    "agent_name": agent_name,
                    "progress": 100,
                    "result": mock_result,
                    "success": True
                })
            
            return mock_result
            
        except Exception as e:
            logger.error(f"Error in mock execution for {agent_name}: {str(e)}")
            return {
                "agent_name": agent_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
