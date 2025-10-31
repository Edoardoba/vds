from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
import logging
from datetime import datetime
from io import BytesIO
import json
import asyncio
from sqlalchemy.orm import Session

from config import settings
from services.s3_service import S3Service
from services.agent_service import AgentService
from services.langgraph_workflow import LangGraphMultiAgentWorkflow
from services.langgraph_websocket import LangGraphWebSocketManager
from services.database_service import DatabaseService
from utils.validators import validate_data_file
from utils.data_processor import clean_nan_values

# Import database models and initialization
from models import init_db, get_db

# Import rate limiter
try:
    from services.rate_limiter import check_rate_limit
    RATE_LIMITER_AVAILABLE = True
except ImportError:
    RATE_LIMITER_AVAILABLE = False
    logger.warning("Rate limiter not available, proceeding without it")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Upload Service", 
    description="A FastAPI service for uploading CSV and Excel files to S3",
    version="2.0.0"
)

# Add CORS middleware
import os

# Dynamic CORS origins based on environment
def get_allowed_origins():
    """Get allowed CORS origins based on environment"""
    # Base origins for development
    origins = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
    ]
    
    # Add production origins from environment variables
    vercel_url = os.getenv("VERCEL_URL")
    frontend_url = os.getenv("FRONTEND_URL") 
    custom_domain = os.getenv("CUSTOM_DOMAIN")
    
    if vercel_url:
        origins.append(f"https://{vercel_url}")
    if frontend_url:
        origins.append(frontend_url)
    if custom_domain:
        origins.append(custom_domain)
    
    # Add common Vercel patterns for Banta project
    # Note: Wildcards may not work, so we add explicit common patterns
    origins.extend([
        "https://vds-new.vercel.app",
        "https://banta-dashboard.vercel.app",
        "https://banta-frontend.vercel.app",
        "https://banta.vercel.app"
    ])
    
    # For debugging: log all origins
    # logger.info(f"CORS Origins configured: {origins}")
    
    return origins

# Configure CORS with explicit origins (production-safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add request logging middleware for debugging CORS
@app.middleware("http")
async def log_requests(request, call_next):
    origin = request.headers.get("origin")
    method = request.method
    url = str(request.url)
    
    if method == "OPTIONS":
        logger.info(f"CORS Preflight: {method} {url} - Origin: {origin}")
    
    response = await call_next(request)
    return response

# Initialize services
s3_service = S3Service()
agent_service = AgentService()
db_service = DatabaseService()

# Initialize LangGraph workflow manager (workflows will be created per request)
langgraph_workflow = None
langgraph_websocket_manager = None

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Don't fail startup - database is optional for basic functionality

# Graceful shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("Shutting down gracefully...")
    try:
        # Close any remaining WebSocket connections
        if manager:
            for connection in manager.active_connections.copy():
                try:
                    await connection.close()
                except Exception:
                    pass
        
        # Close database connections
        from models.database import engine
        engine.dispose()
        
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.subscriptions: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

    def subscribe(self, websocket: WebSocket, workflow_id: str):
        if websocket in self.subscriptions and workflow_id:
            self.subscriptions[websocket].add(workflow_id)

    async def send_progress(self, message: dict):
        """
        Send progress update to all connected WebSocket clients.
        
        NOTE: We send to all connections regardless of workflow_id because the frontend
        doesn't subscribe to specific workflows. The frontend will filter messages based
        on workflow_id internally.
        """
        target_workflow = message.get("workflow_id")
        for connection in list(self.active_connections):
            try:
                # Send to all connections - frontend handles filtering
                await connection.send_text(json.dumps(message))
            except:
                # Remove disconnected connections
                if connection in self.active_connections:
                    self.active_connections.remove(connection)
                if connection in self.subscriptions:
                    del self.subscriptions[connection]

manager = ConnectionManager()

# Initialize LangGraph WebSocket manager (workflow instances created per-request)
langgraph_websocket_manager = LangGraphWebSocketManager(manager)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "", "timestamp": datetime.utcnow().isoformat()}


@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time analysis progress updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Clients may send subscription messages: {"subscribe": "<analysis_id>"}
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
                if isinstance(msg, dict) and "subscribe" in msg:
                    manager.subscribe(websocket, str(msg.get("subscribe")))
            except Exception:
                # Ignore non-JSON keepalive
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    try:
        # Check S3 connection
        s3_status = await s3_service.check_connection()
        
        # Check environment variables
        env_status = {
            "aws_access_key": "✓" if settings.AWS_ACCESS_KEY_ID else "✗",
            "aws_secret_key": "✓" if settings.AWS_SECRET_ACCESS_KEY else "✗", 
            "s3_bucket": settings.S3_BUCKET_NAME or "not_set",
            "aws_region": settings.AWS_REGION
        }
        
        return {
            "status": "healthy",
            "services": {
                "s3": "connected" if s3_status else "disconnected",
                "environment": env_status
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = None
):
    """
    Upload a data file (CSV, XLSX, XLS) to S3 bucket
    
    Args:
        file: Data file to upload (CSV, XLSX, or XLS)
        folder: Optional folder path in S3 bucket
    
    Returns:
        Success message with file details and validation metadata
    """
    try:
        # Read file content first (to preserve it before validation consumes it)
        await file.seek(0)
        file_content = await file.read()
        
        if not file_content:
            raise ValueError("File is empty")
        
        # Reset file pointer for validation
        await file.seek(0)
        
        # Validate file and get metadata
        validation_result = await validate_data_file(file)
        
        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        original_filename = file.filename
        file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'csv'
        unique_filename = f"{timestamp}_{original_filename}"
        
        # Construct S3 key
        s3_key = f"{folder}/{unique_filename}" if folder else unique_filename
        
        # Create a new BytesIO object with the file content for S3 upload
        file_for_upload = BytesIO(file_content)
        
        # Upload to S3
        upload_result = await s3_service.upload_file(
            file_obj=file_for_upload,
            key=s3_key,
            content_type=file.content_type or "text/csv"
        )
        
        logger.info(f"Successfully uploaded file: {s3_key}")
        
        return {
            "message": "File uploaded successfully",
            "file_details": {
                "original_filename": original_filename,
                "s3_key": s3_key,
                "bucket": settings.S3_BUCKET_NAME,
                "upload_timestamp": datetime.utcnow().isoformat(),
                "file_size": len(file_content),
                "content_type": file.content_type
            },
            "validation_result": validation_result,
            "s3_response": upload_result
        }
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


# Backward compatibility endpoint
@app.post("/upload-csv")
async def upload_csv_legacy(
    file: UploadFile = File(...),
    folder: Optional[str] = None
):
    """
    Legacy CSV upload endpoint (redirects to /upload-file)
    Maintained for backward compatibility
    """
    return await upload_file(file, folder)


@app.get("/list-files")
async def list_files(folder: Optional[str] = None):
    """
    List files in the S3 bucket
    
    Args:
        folder: Optional folder path to list files from
    
    Returns:
        List of files in the bucket/folder
    """
    try:
        files = await s3_service.list_files(prefix=folder)
        return {
            "files": files,
            "count": len(files),
            "folder": folder or "root"
        }
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@app.post("/analyze-data")
async def analyze_data(
    file: UploadFile = File(...),
    question: str = Form(...),
    selected_agents: Optional[str] = Form(None),
    bypass_cache: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Analyze uploaded data using AI agents based on user question
    WITH CACHING AND DATABASE TRACKING

    Args:
        file: Data file to analyze (CSV, XLSX, or XLS)
        question: User's analysis question/request
        selected_agents: Optional JSON string of selected agent names

    Returns:
        Complete analysis results with agent outputs and report
    """
    analysis_record = None
    start_time = datetime.utcnow()

    try:
        # Validate inputs
        if not question or question.strip() == "":
            raise ValueError("Analysis question is required")

        # Read file content
        await file.seek(0)
        file_content = await file.read()

        if not file_content:
            raise ValueError("File is empty")

        # Reset file pointer for validation
        await file.seek(0)

        # Validate file type
        validation_result = await validate_data_file(file)
        logger.info(f"File validation passed: {file.filename}")

        # Parse optional selected_agents JSON string into list
        selected_agents_list = None
        if selected_agents:
            try:
                import json as _json
                parsed = _json.loads(selected_agents)
                if isinstance(parsed, list) and len(parsed) > 0:
                    selected_agents_list = [str(a) for a in parsed]
                    logger.info(f"Parsed selected_agents from frontend: {selected_agents_list}")
                else:
                    logger.warning(f"Selected agents is empty list or not a list: {parsed}")
            except Exception as e:
                logger.warning(f"Failed to parse selected_agents JSON: {e}, raw value: {selected_agents}")
                selected_agents_list = None
        else:
            logger.info("No selected_agents provided in request, will use smart selection")

        # ========== CACHING LOGIC ==========
        # Compute data hash
        data_hash = db_service.generate_data_hash(file_content)
        # Parse bypass flag and global setting
        bypass = False
        if bypass_cache is not None:
            bypass = str(bypass_cache).lower() in ["true", "1", "yes"]
        if not settings.CACHE_ENABLED:
            bypass = True

        # Build execution config signature to separate caches when plan changes
        exec_signature = ""
        try:
            from services.claude_service import ClaudeService as _CS
            _tmp = _CS()
            import yaml as _yaml, hashlib as _hashlib
            exec_signature = _hashlib.sha256(_yaml.safe_dump(_tmp.execution_config).encode()).hexdigest() if _tmp.execution_config else ""
        except Exception:
            exec_signature = ""

        cache_key = None
        if not bypass:
            if selected_agents_list:
                cache_key = db_service.generate_analysis_cache_key(data_hash, question.strip(), selected_agents_list, exec_signature)
            else:
                cache_key = db_service.generate_cache_key(data_hash, question.strip())

            # Check cache first
            cached_result = db_service.get_cached_analysis(db, cache_key)
            if cached_result:
                logger.info(f"✅ CACHE HIT - Returning cached result (saved ~{cached_result.time_saved_ms}ms)")
                result = cached_result.cached_result
                result["is_cached"] = True
                result["cache_info"] = {
                    "cached_at": cached_result.created_at.isoformat(),
                    "cache_hits": cached_result.access_count,
                    "time_saved_ms": cached_result.time_saved_ms
                }

                # Mark analysis as cached in database
                if not selected_agents_list:
                    selected_agents_list = result.get("selected_agents", [])

                analysis_record = db_service.create_analysis(
                    db=db,
                    filename=file.filename,
                    user_question=question.strip(),
                    selected_agents=selected_agents_list,
                    cache_key=cache_key
                )
                analysis_record.is_cached = True
                analysis_record.status = "cached"
                db_service.save_analysis_results(
                    db=db,
                    analysis_id=analysis_record.id,
                    data_sample=result.get("data_sample", {}),
                    agent_results=result.get("agent_results", {}),
                    report=result.get("report", {}),
                    errors=result.get("errors", [])
                )

                # Emit cached result via WebSocket so frontend can display it
                try:
                    await manager.send_progress({
                        "type": "workflow_started",
                        "workflow_id": analysis_record.id,
                        "filename": file.filename,
                        "user_question": question.strip(),
                        "progress": 0.0,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    # Send agent completed events for cached agents so UI can display them
                    agent_results = result.get("agent_results", {})
                    if agent_results:
                        # Calculate progress increment per agent
                        total_agents = len(agent_results)
                        progress_per_agent = 90.0 / max(total_agents, 1) if total_agents > 0 else 0
                        current_progress = 10.0
                        
                        for agent_name, agent_result in agent_results.items():
                            current_progress = min(100.0, current_progress + progress_per_agent)
                            
                            # Send agent completed event
                            await manager.send_progress({
                                "type": "agent_completed",
                                "agent_name": agent_name,
                                "progress": current_progress,
                                "result": agent_result,
                                "success": agent_result.get("success", True),
                                "timestamp": datetime.utcnow().isoformat()
                            })
                    
                    # Immediately mark as completed for cache hits
                    # Ensure final_report exists
                    final_report = result.get("report")
                    if not final_report:
                        final_report = {
                            "content": "Cached analysis result",
                            "summary": "Analysis from cache",
                            "user_question": question.strip(),
                            "data_overview": result.get("data_sample", {}),
                            "agents_executed": result.get("selected_agents", []),
                            "success": True,
                            "generated_at": datetime.utcnow().isoformat(),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    
                    await manager.send_progress({
                        "type": "workflow_completed",
                        "workflow_id": analysis_record.id,
                        "progress": 100.0,
                        "success": True,
                        "final_report": final_report,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as ws_err:
                    logger.warning(f"Failed to emit cache hit events: {ws_err}")

                return clean_nan_values(result)

        # ========== NEW ANALYSIS ==========
        logger.info(f"❌ CACHE MISS - Running new analysis")

        # Create analysis record in database
        analysis_record = db_service.create_analysis(
            db=db,
            filename=file.filename,
            user_question=question.strip(),
            selected_agents=selected_agents_list or [],
            cache_key=cache_key
        )

        # Update status to running
        db_service.update_analysis_status(db, analysis_record.id, "running")

        # Create a new workflow instance per request to avoid cross-request state
        local_workflow = LangGraphMultiAgentWorkflow(langgraph_websocket_manager)
        # Use LangGraph workflow for analysis (workflow_started emitted inside workflow)
        analysis_result = await local_workflow.run_analysis(
            file_content=file_content,
            filename=file.filename,
            user_question=question.strip(),
            selected_agents=selected_agents_list,
            analysis_id=analysis_record.id,  # Pass for tracking
            db_session=db  # Pass for agent tracking
        )

        # Add validation metadata
        analysis_result["file_validation"] = validation_result
        analysis_result["is_cached"] = False
        analysis_result["analysis_id"] = analysis_record.id

        # Clean any NaN values to ensure JSON serializability
        cleaned_result = clean_nan_values(analysis_result)

        # Save results to database
        db_service.save_analysis_results(
            db=db,
            analysis_id=analysis_record.id,
            data_sample=cleaned_result.get("data_sample", {}),
            agent_results=cleaned_result.get("agent_results", {}),
            report=cleaned_result.get("report", {}),
            errors=[]
        )

        # Save to cache for future use
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        if settings.CACHE_ENABLED:
            final_cache_key = cache_key or db_service.generate_analysis_cache_key(
                data_hash,
                question.strip(),
                cleaned_result.get("selected_agents"),
                exec_signature
            )
            db_service.save_to_cache(
                db=db,
                cache_key=final_cache_key,
                data_hash=data_hash,
                user_question=question.strip(),
                analysis_id=analysis_record.id,
                result=cleaned_result,
                ttl_hours=24,
                execution_time_ms=int(execution_time)
            )

        logger.info(f"✅ Analysis completed for: {file.filename} in {execution_time:.0f}ms")

        return cleaned_result

    except ValueError as ve:
        logger.error(f"Validation error in analyze_data: {str(ve)}")
        if analysis_record:
            db_service.update_analysis_status(db, analysis_record.id, "failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        if analysis_record:
            db_service.update_analysis_status(db, analysis_record.id, "failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/plan-analysis")
async def plan_analysis(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    """
    Returns the data sample and the list of selected agents (in order) for preview.
    """
    try:
        if not question or question.strip() == "":
            raise ValueError("Analysis question is required")

        await file.seek(0)
        file_content = await file.read()
        if not file_content:
            raise ValueError("File is empty")

        await file.seek(0)
        # Validate file type
        _ = await validate_data_file(file)

        plan = await agent_service.plan_request(
            file_content=file_content,
            filename=file.filename,
            user_question=question.strip()
        )
        return clean_nan_values(plan)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Plan analysis failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Plan analysis failed: {str(e)}")

@app.post("/preview-data")
async def preview_data(
    file: UploadFile = File(...)
):
    """
    Get a preview of uploaded data (first 5 rows) without full analysis
    
    Args:
        file: Data file to preview
        
    Returns:
        Data sample with basic information
    """
    try:
        # Read file content
        await file.seek(0)
        file_content = await file.read()
        
        if not file_content:
            raise ValueError("File is empty")
        
        # Reset file pointer for validation
        await file.seek(0)
        
        # Validate file
        validation_result = await validate_data_file(file)
        
        # Get data preview
        from utils.data_processor import DataProcessor
        data_processor = DataProcessor()
        
        preview_data = data_processor.read_file_sample(
            file_content, file.filename, sample_rows=5
        )
        
        # Add validation metadata
        preview_data["file_validation"] = validation_result
        
        # Clean any NaN values to ensure JSON serializability
        cleaned_preview = clean_nan_values(preview_data)
        
        logger.info(f"Data preview generated for: {file.filename}")
        
        return {
            "success": True,
            "preview": cleaned_preview,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as ve:
        logger.error(f"Validation error in preview_data: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Preview failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview data: {str(e)}"
        )


@app.get("/agents/available")
async def get_available_agents():
    """
    Get list of available analysis agents and their capabilities

    Returns:
        List of agents with descriptions and specialties
    """
    try:
        available_agents = []
        for agent_name, agent in agent_service.agents.items():
            available_agents.append({
                "name": agent.name,
                "display_name": agent.display_name,
                "description": agent.description,
                "specialties": agent.specialties,
                "keywords": agent.keywords,
                "output_type": agent.output_type
            })

        return {
            "agents": available_agents,
            "total_count": len(available_agents),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting available agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available agents: {str(e)}"
        )


# ========== NEW ENDPOINTS FOR HISTORY & ANALYTICS ==========

@app.get("/history/recent")
async def get_recent_history(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get recent analysis history

    Args:
        limit: Number of recent analyses to return (default 10)

    Returns:
        List of recent analyses
    """
    try:
        analyses = db_service.get_recent_analyses(db, limit=limit)
        return {
            "success": True,
            "count": len(analyses),
            "analyses": [a.to_dict() for a in analyses],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recent history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent history: {str(e)}"
        )


@app.get("/history/{analysis_id}")
async def get_analysis_by_id(analysis_id: str, db: Session = Depends(get_db)):
    """
    Get a specific analysis by ID

    Args:
        analysis_id: Analysis ID

    Returns:
        Analysis details
    """
    try:
        analysis = db_service.get_analysis(db, analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )

        return {
            "success": True,
            "analysis": analysis.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}"
        )


@app.get("/analytics/statistics")
async def get_analytics_statistics(db: Session = Depends(get_db)):
    """
    Get overall analytics and statistics

    Returns:
        Statistics about analyses, caching, and performance
    """
    try:
        stats = db_service.get_analysis_statistics(db)
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@app.get("/analytics/agent-performance")
async def get_agent_performance_stats(db: Session = Depends(get_db)):
    """
    Get performance statistics for all agents

    Returns:
        Performance metrics for each agent
    """
    try:
        performance = db_service.get_all_agent_performance(db)
        return {
            "success": True,
            "count": len(performance),
            "agent_performance": [p.to_dict() for p in performance],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agent performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent performance: {str(e)}"
        )


@app.delete("/cache/clear-expired")
async def clear_expired_cache(db: Session = Depends(get_db)):
    """
    Clear all expired cache entries

    Returns:
        Number of cache entries cleared
    """
    try:
        cleared_count = db_service.clear_expired_cache(db)
        return {
            "success": True,
            "cleared_count": cleared_count,
            "message": f"Cleared {cleared_count} expired cache entries",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing expired cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear expired cache: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
