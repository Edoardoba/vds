"""
LangGraph Multi-Agent Workflow Implementation
Complete implementation of the multi-agent framework using LangGraph
"""

from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import asyncio
import logging
import json
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)

class AnalysisState(TypedDict):
    """Shared state across all agents in the workflow"""
    # Input data
    file_content: bytes
    filename: str
    user_question: str
    
    # Data processing
    data_sample: Dict[str, Any]
    processed_data: Optional[Any]
    
    # Agent execution
    selected_agents: List[str]
    agent_results: Dict[str, Any]
    current_agent: Optional[str]
    
    # Progress tracking
    progress: float
    completed_steps: List[str]
    errors: List[str]
    
    # Shared insights between agents
    shared_insights: Dict[str, Any]
    
    # Final results
    final_report: Optional[Dict[str, Any]]
    success: bool
    
    # WebSocket callback for progress updates
    progress_callback: Optional[callable]

class LangGraphMultiAgentWorkflow:
    """LangGraph-based multi-agent workflow for data analysis"""
    
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the complete multi-agent workflow graph"""
        
        # Create the state graph
        workflow = StateGraph(AnalysisState)
        
        # Add core workflow nodes
        workflow.add_node("data_processor", self._process_data_node)
        workflow.add_node("agent_selector", self._select_agents_node)
        workflow.add_node("dynamic_agent_executor", self._run_dynamic_agents_node)
        workflow.add_node("report_generator", self._generate_report_node)
        
        # Define the workflow edges
        workflow.set_entry_point("data_processor")
        
        # Sequential flow
        workflow.add_edge("data_processor", "agent_selector")
        workflow.add_edge("agent_selector", "dynamic_agent_executor")
        workflow.add_edge("dynamic_agent_executor", "report_generator")
        workflow.add_edge("report_generator", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _process_data_node(self, state: AnalysisState) -> AnalysisState:
        """Process the input data and create data sample"""
        logger.info("Processing data...")
        
        # Update progress
        state["progress"] = 10.0
        state["completed_steps"].append("data_processing")
        
        # Send progress update
        await self._send_progress_update(state, "data_processing", "Processing data sample...")
        
        try:
            # Process the data using existing DataProcessor
            from utils.data_processor import DataProcessor
            processor = DataProcessor()
            state["data_sample"] = processor.read_file_sample(
                state["file_content"], 
                state["filename"], 
                sample_rows=5
            )
            
            # Initialize shared insights
            state["shared_insights"] = {
                "data_shape": state["data_sample"].get("shape", "Unknown"),
                "columns": state["data_sample"].get("columns", []),
                "data_types": state["data_sample"].get("dtypes", {}),
                "missing_values": state["data_sample"].get("missing_values", {}),
                "sample_data": state["data_sample"].get("sample_data", [])
            }
            
            logger.info(f"Data processed successfully. Shape: {state['shared_insights']['data_shape']}")
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            state["errors"].append(f"Data processing: {str(e)}")
            await self._send_error_update(state, "data_processing", str(e))
        
        return state
    
    async def _select_agents_node(self, state: AnalysisState) -> AnalysisState:
        """Select appropriate agents based on data and question"""
        logger.info("Selecting agents...")
        
        state["progress"] = 20.0
        state["completed_steps"].append("agent_selection")
        
        await self._send_progress_update(state, "agent_selection", "Selecting appropriate agents...")
        
        try:
            # If agents were already provided, use them
            if state["selected_agents"] and len(state["selected_agents"]) > 0:
                logger.info(f"Using provided agents: {state['selected_agents']}")
            else:
                # Use Claude to select agents
                from services.claude_service import ClaudeService
                claude_service = ClaudeService()
                state["selected_agents"] = await claude_service.select_agents(
                    state["data_sample"], 
                    state["user_question"]
                )
                logger.info(f"Selected agents: {state['selected_agents']}")
            
        except Exception as e:
            logger.error(f"Agent selection failed: {e}")
            state["errors"].append(f"Agent selection: {str(e)}")
            # Fallback to default agents
            state["selected_agents"] = ["data_quality_audit", "exploratory_data_analysis", "data_visualization"]
            await self._send_error_update(state, "agent_selection", str(e))
        
        return state
    
    async def _run_dynamic_agents_node(self, state: AnalysisState) -> AnalysisState:
        """Run all selected agents dynamically"""
        logger.info("Running dynamic agents...")
        
        selected_agents = state.get("selected_agents", [])
        if not selected_agents:
            logger.warning("No agents selected, skipping agent execution")
            return state
        
        logger.info(f"Running {len(selected_agents)} agents: {selected_agents}")
        
        # Calculate progress per agent
        progress_per_agent = 60.0 / len(selected_agents)  # Use 60% of total progress for agents
        base_progress = 30.0
        
        for i, agent_name in enumerate(selected_agents):
            try:
                # Update progress
                current_progress = base_progress + (i * progress_per_agent)
                state["progress"] = current_progress
                state["current_agent"] = agent_name
                
                await self._send_agent_started(state, agent_name)
                
                # Execute the agent
                result = await self._execute_agent(agent_name, state)
                state["agent_results"][agent_name] = result
                state["completed_steps"].append(agent_name)
                
                # Update shared insights
                if result.get("success") and result.get("code_result", {}).get("insights"):
                    state["shared_insights"][agent_name] = result["code_result"]["insights"]
                
                await self._send_agent_completed(state, agent_name, result)
                
                logger.info(f"Completed agent {agent_name}: {result.get('success', False)}")
                
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                state["errors"].append(f"{agent_name}: {str(e)}")
                
                # Add error result
                error_result = {
                    "agent_name": agent_name,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                state["agent_results"][agent_name] = error_result
                
                await self._send_agent_error(state, agent_name, str(e))
        
        # Update final progress
        state["progress"] = 90.0
        state["current_agent"] = None
        
        logger.info(f"Completed running {len(selected_agents)} agents")
        return state
    
    async def _run_data_quality_node(self, state: AnalysisState) -> AnalysisState:
        """Run data quality audit agent"""
        logger.info("Running data quality audit...")
        
        state["progress"] = 30.0
        state["current_agent"] = "data_quality_audit"
        
        await self._send_agent_started(state, "data_quality_audit")
        
        try:
            result = await self._execute_agent("data_quality_audit", state)
            state["agent_results"]["data_quality_audit"] = result
            state["completed_steps"].append("data_quality_audit")
            
            # Update shared insights with data quality findings
            if result.get("success") and result.get("insights"):
                state["shared_insights"]["data_quality"] = result["insights"]
            
            await self._send_agent_completed(state, "data_quality_audit", result)
            
        except Exception as e:
            logger.error(f"Data quality audit failed: {e}")
            state["errors"].append(f"Data quality audit: {str(e)}")
            await self._send_agent_error(state, "data_quality_audit", str(e))
        
        return state
    
    async def _run_exploratory_node(self, state: AnalysisState) -> AnalysisState:
        """Run exploratory data analysis agent"""
        logger.info("Running exploratory analysis...")
        
        state["progress"] = 50.0
        state["current_agent"] = "exploratory_data_analysis"
        
        await self._send_agent_started(state, "exploratory_data_analysis")
        
        try:
            result = await self._execute_agent("exploratory_data_analysis", state)
            state["agent_results"]["exploratory_data_analysis"] = result
            state["completed_steps"].append("exploratory_analysis")
            
            # Update shared insights with exploratory findings
            if result.get("success") and result.get("insights"):
                state["shared_insights"]["exploratory"] = result["insights"]
            
            await self._send_agent_completed(state, "exploratory_data_analysis", result)
            
        except Exception as e:
            logger.error(f"Exploratory analysis failed: {e}")
            state["errors"].append(f"Exploratory analysis: {str(e)}")
            await self._send_agent_error(state, "exploratory_data_analysis", str(e))
        
        return state
    
    def _route_after_exploratory(self, state: AnalysisState) -> str:
        """Decide routing after exploratory analysis"""
        # Check if we have numerical data for statistical analysis
        data_sample = state.get("data_sample", {})
        columns = data_sample.get("columns", [])
        
        # Handle different column data structures
        has_numerical = False
        has_categorical = False
        
        for col in columns:
            # Handle both dict and string column structures
            if isinstance(col, dict):
                dtype = col.get("dtype", "")
            elif isinstance(col, str):
                # If column is just a string, check the dtypes dict
                dtypes = data_sample.get("dtypes", {})
                dtype = dtypes.get(col, "")
            else:
                continue
                
            if dtype in ["int64", "float64", "int32", "float32"]:
                has_numerical = True
            elif dtype in ["object", "category", "string"]:
                has_categorical = True
        
        if has_numerical:
            return "statistical"
        elif has_categorical:
            return "visualization"
        else:
            return "specialized"
    
    async def _run_statistical_node(self, state: AnalysisState) -> AnalysisState:
        """Run statistical analysis agent"""
        logger.info("Running statistical analysis...")
        
        state["progress"] = 60.0
        state["current_agent"] = "statistical_analysis"
        
        await self._send_agent_started(state, "statistical_analysis")
        
        try:
            result = await self._execute_agent("statistical_analysis", state)
            state["agent_results"]["statistical_analysis"] = result
            state["completed_steps"].append("statistical_analysis")
            
            # Update shared insights with statistical findings
            if result.get("success") and result.get("insights"):
                state["shared_insights"]["statistical"] = result["insights"]
            
            await self._send_agent_completed(state, "statistical_analysis", result)
            
        except Exception as e:
            logger.error(f"Statistical analysis failed: {e}")
            state["errors"].append(f"Statistical analysis: {str(e)}")
            await self._send_agent_error(state, "statistical_analysis", str(e))
        
        return state
    
    async def _run_visualization_node(self, state: AnalysisState) -> AnalysisState:
        """Run data visualization agent"""
        logger.info("Running data visualization...")
        
        state["progress"] = 70.0
        state["current_agent"] = "data_visualization"
        
        await self._send_agent_started(state, "data_visualization")
        
        try:
            result = await self._execute_agent("data_visualization", state)
            state["agent_results"]["data_visualization"] = result
            state["completed_steps"].append("data_visualization")
            
            # Update shared insights with visualization findings
            if result.get("success") and result.get("insights"):
                state["shared_insights"]["visualization"] = result["insights"]
            
            await self._send_agent_completed(state, "data_visualization", result)
            
        except Exception as e:
            logger.error(f"Data visualization failed: {e}")
            state["errors"].append(f"Data visualization: {str(e)}")
            await self._send_agent_error(state, "data_visualization", str(e))
        
        return state
    
    async def _run_specialized_node(self, state: AnalysisState) -> AnalysisState:
        """Run specialized analysis agents based on data characteristics"""
        logger.info("Running specialized analysis...")
        
        state["progress"] = 80.0
        
        # Determine specialized agents based on data and user question
        specialized_agents = self._get_specialized_agents(state)
        
        for agent_name in specialized_agents:
            state["current_agent"] = agent_name
            
            await self._send_agent_started(state, agent_name)
            
            try:
                result = await self._execute_agent(agent_name, state)
                state["agent_results"][agent_name] = result
                state["completed_steps"].append(agent_name)
                
                # Update shared insights
                if result.get("success") and result.get("insights"):
                    state["shared_insights"][agent_name] = result["insights"]
                
                await self._send_agent_completed(state, agent_name, result)
                
            except Exception as e:
                logger.error(f"Specialized agent {agent_name} failed: {e}")
                state["errors"].append(f"{agent_name}: {str(e)}")
                await self._send_agent_error(state, agent_name, str(e))
        
        return state
    
    async def _generate_report_node(self, state: AnalysisState) -> AnalysisState:
        """Generate comprehensive final report"""
        logger.info("Generating final report...")
        
        state["progress"] = 100.0
        state["current_agent"] = None
        state["completed_steps"].append("report_generation")
        
        await self._send_progress_update(state, "report_generation", "Generating comprehensive report...")
        
        try:
            # Generate comprehensive report from all agent results
            report = await self._create_comprehensive_report(state)
            state["final_report"] = report
            state["success"] = True
            
            await self._send_workflow_completed(state)
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            state["errors"].append(f"Report generation: {str(e)}")
            state["success"] = False
            await self._send_error_update(state, "report_generation", str(e))
        
        return state
    
    async def _execute_agent(self, agent_name: str, state: AnalysisState) -> Dict[str, Any]:
        """Execute a specific agent with access to shared state"""
        try:
            # Import and use existing agent service
            from services.agent_service import AgentService
            agent_service = AgentService()
            
            # Get agent instance
            agent = agent_service.agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")
            
            # Check if mock mode is enabled (exclude agent selector)
            if settings.AGENT_MOCK and agent_name != "agent_selector":
                logger.info(f"Using mock execution for agent: {agent_name}")
                return await self._mock_agent_execution(agent_name, agent, state)
            
            # Generate code for this agent
            from services.claude_service import ClaudeService
            claude_service = ClaudeService()
            
            # Load agent config
            agent_config = claude_service.agent_configs.get(agent_name, {})
            if not agent_config:
                raise ValueError(f"Config for agent {agent_name} not found")
            
            # Generate code with access to shared insights
            code_result = await claude_service.generate_agent_code(
                agent_name, agent_config, state["data_sample"], state["user_question"]
            )
            
            # Execute the code
            execution_result = await agent_service._execute_agent_code(
                agent_name, code_result, state["file_content"], state["data_sample"]
            )
            
            # Combine results
            result = {
                "agent_name": agent_name,
                "agent_info": {
                    "display_name": agent.display_name,
                    "description": agent.description,
                    "specialties": agent.specialties
                },
                "code_result": code_result,
                "execution_result": execution_result,
                "timestamp": datetime.utcnow().isoformat(),
                "success": execution_result.get("success", False)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing agent {agent_name}: {str(e)}")
            return {
                "agent_name": agent_name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _mock_agent_execution(self, agent_name: str, agent: Any, state: AnalysisState) -> Dict[str, Any]:
        """
        Mock agent execution that returns sample text with 3-second delay
        
        Args:
            agent_name: Name of the agent
            agent: Agent instance
            state: Analysis state
            
        Returns:
            Mock execution results
        """
        try:
            logger.info(f"Mock execution for agent: {agent_name}")
            
            # Wait 3 seconds to simulate processing
            await asyncio.sleep(3)
            
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
            
            return mock_result
            
        except Exception as e:
            logger.error(f"Error in mock execution for {agent_name}: {str(e)}")
            return {
                "agent_name": agent_name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _get_specialized_agents(self, state: AnalysisState) -> List[str]:
        """Determine specialized agents based on data characteristics and user question"""
        specialized_agents = []
        
        # Get data characteristics
        columns = state.get("data_sample", {}).get("columns", [])
        user_question = state.get("user_question", "").lower()
        
        # Handle different column data structures
        column_names = []
        for col in columns:
            if isinstance(col, dict):
                column_names.append(col.get("name", "").lower())
            elif isinstance(col, str):
                column_names.append(col.lower())
        
        # Check for specific data patterns and user questions
        column_names_str = " ".join(column_names)
        
        # Customer-related analysis
        if any(keyword in user_question for keyword in ["customer", "churn", "retention", "segment"]):
            if any(name in column_names_str for name in ["customer", "user", "client"]):
                specialized_agents.extend(["churn_prediction", "customer_segmentation"])
        
        # Sales-related analysis
        if any(keyword in user_question for keyword in ["sales", "revenue", "profit", "performance"]):
            if any(name in column_names_str for name in ["sales", "revenue", "profit", "price"]):
                specialized_agents.extend(["sales_performance_analysis", "revenue_forecasting"])
        
        # Marketing analysis
        if any(keyword in user_question for keyword in ["marketing", "campaign", "roi", "acquisition"]):
            specialized_agents.extend(["marketing_roi_analysis", "customer_acquisition_cost_analysis"])
        
        # Time series analysis
        if any(keyword in user_question for keyword in ["trend", "forecast", "time", "seasonal"]):
            specialized_agents.append("time_series_analysis")
        
        # Anomaly detection
        if any(keyword in user_question for keyword in ["anomaly", "outlier", "unusual", "detect"]):
            specialized_agents.append("anomaly_detection")
        
        # Limit to 3 specialized agents to avoid overwhelming
        return specialized_agents[:3]
    
    async def _create_comprehensive_report(self, state: AnalysisState) -> Dict[str, Any]:
        """Create comprehensive report from all agent results and shared insights"""
        
        # Collect all insights
        all_insights = []
        
        # Add shared insights
        shared_insights = state.get("shared_insights", {})
        for category, insights in shared_insights.items():
            if insights:
                all_insights.append(f"**{category.title()} Analysis:**\n{insights}")
        
        # Add individual agent insights
        agent_results = state.get("agent_results", {})
        for agent_name, result in agent_results.items():
            if result.get("success") and result.get("code_result", {}).get("insights"):
                all_insights.append(f"**{agent_name.replace('_', ' ').title()}:**\n{result['code_result']['insights']}")
        
        # Create comprehensive report
        report = {
            "summary": f"Analysis completed for {state['filename']}",
            "user_question": state["user_question"],
            "data_overview": {
                "filename": state["filename"],
                "shape": shared_insights.get("data_shape", "Unknown"),
                "columns": shared_insights.get("columns", []),
                "data_types": shared_insights.get("data_types", {})
            },
            "agents_executed": list(agent_results.keys()),
            "insights": "\n\n".join(all_insights),
            "agent_results": agent_results,
            "errors": state.get("errors", []),
            "success": state.get("success", False),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return report
    
    # WebSocket progress update methods
    async def _send_progress_update(self, state: AnalysisState, step: str, message: str):
        """Send workflow progress update"""
        if self.websocket_manager:
            await self.websocket_manager.send_progress({
                "type": "workflow_progress",
                "step": step,
                "progress": state["progress"],
                "message": message,
                "completed_steps": state["completed_steps"],
                "current_agent": state.get("current_agent")
            })
    
    async def _send_agent_started(self, state: AnalysisState, agent_name: str):
        """Send agent started notification"""
        if self.websocket_manager:
            await self.websocket_manager.send_progress({
                "type": "agent_started",
                "agent_name": agent_name,
                "progress": state["progress"]
            })
    
    async def _send_agent_completed(self, state: AnalysisState, agent_name: str, result: Dict[str, Any]):
        """Send agent completed notification"""
        if self.websocket_manager:
            await self.websocket_manager.send_progress({
                "type": "agent_completed",
                "agent_name": agent_name,
                "progress": state["progress"],
                "result": result,
                "success": result.get("success", False)
            })
    
    async def _send_agent_error(self, state: AnalysisState, agent_name: str, error: str):
        """Send agent error notification"""
        if self.websocket_manager:
            await self.websocket_manager.send_progress({
                "type": "agent_error",
                "agent_name": agent_name,
                "error": error,
                "progress": state["progress"]
            })
    
    async def _send_error_update(self, state: AnalysisState, step: str, error: str):
        """Send workflow error update"""
        if self.websocket_manager:
            await self.websocket_manager.send_progress({
                "type": "workflow_error",
                "step": step,
                "error": error,
                "progress": state["progress"]
            })
    
    async def _send_workflow_completed(self, state: AnalysisState):
        """Send workflow completed notification"""
        if self.websocket_manager:
            await self.websocket_manager.send_progress({
                "type": "workflow_completed",
                "progress": 100.0,
                "success": state["success"],
                "final_report": state.get("final_report")
            })
    
    async def run_analysis(self, file_content: bytes, filename: str, user_question: str, selected_agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run the complete multi-agent analysis workflow"""
        
        # Initialize state
        initial_state = AnalysisState(
            file_content=file_content,
            filename=filename,
            user_question=user_question,
            data_sample={},
            processed_data=None,
            selected_agents=selected_agents or [],
            agent_results={},
            current_agent=None,
            progress=0.0,
            completed_steps=[],
            errors=[],
            shared_insights={},
            final_report=None,
            success=False,
            progress_callback=None
        )
        
        # Run the workflow with configuration
        config = {"configurable": {"thread_id": f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"}}
        final_state = await self.graph.ainvoke(initial_state, config=config)
        
        # Return in the expected format
        return {
            "success": final_state["success"],
            "timestamp": datetime.utcnow().isoformat(),
            "data_sample": final_state["data_sample"],
            "user_question": final_state["user_question"],
            "selected_agents": final_state["selected_agents"],
            "agent_results": final_state["agent_results"],
            "report": final_state["final_report"]
        }