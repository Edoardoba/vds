"""
LangGraph WebSocket Integration
Handles real-time progress updates for LangGraph workflows
"""

from typing import Dict, Any, Optional, Callable
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LangGraphWebSocketManager:
    """Manages WebSocket connections and progress updates for LangGraph workflows"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.active_workflows = {}
        
    async def send_progress(self, message: Dict[str, Any]):
        """Send progress update via WebSocket"""
        try:
            if self.websocket_manager:
                await self.websocket_manager.send_progress(message)
                logger.debug(f"Sent progress update: {message.get('type', 'unknown')}")
            else:
                logger.warning("WebSocket manager is None, cannot send progress update")
        except Exception as e:
            logger.error(f"Error sending progress update: {e}")
    
    async def send_workflow_started(self, workflow_id: str, filename: str, user_question: str):
        """Send workflow started notification"""
        await self.send_progress({
            "type": "workflow_started",
            "workflow_id": workflow_id,
            "filename": filename,
            "user_question": user_question,
            "progress": 0.0,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_workflow_progress(self, step: str, progress: float, message: str, 
                                   completed_steps: list, current_agent: Optional[str] = None):
        """Send workflow progress update"""
        await self.send_progress({
            "type": "workflow_progress",
            "step": step,
            "progress": progress,
            "message": message,
            "completed_steps": completed_steps,
            "current_agent": current_agent,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_agent_started(self, agent_name: str, progress: float):
        """Send agent started notification"""
        await self.send_progress({
            "type": "agent_started",
            "agent_name": agent_name,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_agent_completed(self, agent_name: str, result: Dict[str, Any], progress: float):
        """Send agent completed notification"""
        await self.send_progress({
            "type": "agent_completed",
            "agent_name": agent_name,
            "progress": progress,
            "result": result,
            "success": result.get("success", False),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_agent_error(self, agent_name: str, error: str, progress: float):
        """Send agent error notification"""
        await self.send_progress({
            "type": "agent_error",
            "agent_name": agent_name,
            "error": error,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_workflow_error(self, step: str, error: str, progress: float):
        """Send workflow error notification"""
        await self.send_progress({
            "type": "workflow_error",
            "step": step,
            "error": error,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_workflow_completed(self, success: bool, final_report: Optional[Dict[str, Any]] = None):
        """Send workflow completed notification"""
        await self.send_progress({
            "type": "workflow_completed",
            "progress": 100.0,
            "success": success,
            "final_report": final_report,
            "timestamp": datetime.utcnow().isoformat()
        })

class LangGraphProgressTracker:
    """Track and manage progress for LangGraph workflows"""
    
    def __init__(self, websocket_manager: LangGraphWebSocketManager):
        self.websocket_manager = websocket_manager
        self.workflow_states = {}
    
    async def track_workflow_start(self, workflow_id: str, filename: str, user_question: str):
        """Track workflow start"""
        self.workflow_states[workflow_id] = {
            "filename": filename,
            "user_question": user_question,
            "progress": 0.0,
            "completed_steps": [],
            "current_agent": None,
            "start_time": datetime.utcnow(),
            "agent_results": {}
        }
        
        await self.websocket_manager.send_workflow_started(workflow_id, filename, user_question)
    
    async def track_step_progress(self, workflow_id: str, step: str, progress: float, 
                                message: str, current_agent: Optional[str] = None):
        """Track step progress"""
        if workflow_id in self.workflow_states:
            state = self.workflow_states[workflow_id]
            state["progress"] = progress
            state["current_agent"] = current_agent
            
            if step not in state["completed_steps"]:
                state["completed_steps"].append(step)
            
            await self.websocket_manager.send_workflow_progress(
                step, progress, message, state["completed_steps"], current_agent
            )
    
    async def track_agent_start(self, workflow_id: str, agent_name: str):
        """Track agent start"""
        if workflow_id in self.workflow_states:
            state = self.workflow_states[workflow_id]
            state["current_agent"] = agent_name
            
            await self.websocket_manager.send_agent_started(agent_name, state["progress"])
    
    async def track_agent_complete(self, workflow_id: str, agent_name: str, result: Dict[str, Any]):
        """Track agent completion"""
        if workflow_id in self.workflow_states:
            state = self.workflow_states[workflow_id]
            state["agent_results"][agent_name] = result
            
            await self.websocket_manager.send_agent_completed(agent_name, result, state["progress"])
    
    async def track_agent_error(self, workflow_id: str, agent_name: str, error: str):
        """Track agent error"""
        if workflow_id in self.workflow_states:
            state = self.workflow_states[workflow_id]
            
            await self.websocket_manager.send_agent_error(agent_name, error, state["progress"])
    
    async def track_workflow_complete(self, workflow_id: str, success: bool, 
                                    final_report: Optional[Dict[str, Any]] = None):
        """Track workflow completion"""
        if workflow_id in self.workflow_states:
            state = self.workflow_states[workflow_id]
            state["success"] = success
            state["end_time"] = datetime.utcnow()
            
            await self.websocket_manager.send_workflow_completed(success, final_report)
            
            # Clean up workflow state
            del self.workflow_states[workflow_id]

class LangGraphWorkflowExecutor:
    """Execute LangGraph workflows with WebSocket progress tracking"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.progress_tracker = LangGraphProgressTracker(websocket_manager)
    
    async def execute_workflow(self, workflow, initial_state: Dict[str, Any], 
                             workflow_id: str) -> Dict[str, Any]:
        """Execute LangGraph workflow with progress tracking"""
        
        try:
            # Track workflow start
            await self.progress_tracker.track_workflow_start(
                workflow_id, 
                initial_state.get("filename", "unknown"), 
                initial_state.get("user_question", "")
            )
            
            # Execute the workflow with configuration
            config = {"configurable": {"thread_id": workflow_id}}
            result = await workflow.ainvoke(initial_state, config=config)
            
            # Track workflow completion
            await self.progress_tracker.track_workflow_complete(
                workflow_id, 
                result.get("success", False), 
                result.get("final_report")
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            
            # Track workflow error
            await self.progress_tracker.track_workflow_complete(
                workflow_id, 
                False, 
                {"error": str(e)}
            )
            
            raise e

# Enhanced workflow with integrated WebSocket progress tracking
class WebSocketEnabledLangGraphWorkflow:
    """LangGraph workflow with integrated WebSocket progress tracking"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.progress_tracker = LangGraphProgressTracker(websocket_manager)
        self.workflow_executor = LangGraphWorkflowExecutor(websocket_manager)
        
        # Import and initialize the main workflow
        from .langgraph_workflow import LangGraphMultiAgentWorkflow
        self.workflow = LangGraphMultiAgentWorkflow(websocket_manager)
    
    async def run_analysis(self, file_content: bytes, filename: str, user_question: str) -> Dict[str, Any]:
        """Run analysis with WebSocket progress tracking"""
        
        # Generate unique workflow ID
        workflow_id = f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize state
        initial_state = {
            "file_content": file_content,
            "filename": filename,
            "user_question": user_question,
            "data_sample": {},
            "processed_data": None,
            "selected_agents": [],
            "agent_results": {},
            "current_agent": None,
            "progress": 0.0,
            "completed_steps": [],
            "errors": [],
            "shared_insights": {},
            "final_report": None,
            "success": False,
            "progress_callback": None
        }
        
        # Execute workflow with progress tracking
        result = await self.workflow_executor.execute_workflow(
            self.workflow.graph, 
            initial_state, 
            workflow_id
        )
        
        return result

# Utility functions for frontend integration
def create_websocket_manager(websocket_manager):
    """Create WebSocket manager for LangGraph workflows"""
    return LangGraphWebSocketManager(websocket_manager)

def create_workflow_executor(websocket_manager):
    """Create workflow executor with WebSocket integration"""
    return WebSocketEnabledLangGraphWorkflow(websocket_manager)