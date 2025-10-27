from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
import logging
from datetime import datetime
from io import BytesIO

from config import settings
from services.s3_service import S3Service
from services.agent_service import AgentService
from utils.validators import validate_data_file
from utils.data_processor import clean_nan_values

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
    logger.info(f"CORS Origins configured: {origins}")
    
    return origins

# Temporarily allow all origins for debugging CORS issues
# TODO: Restrict this once we identify the correct Vercel URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily permissive for debugging
    allow_credentials=False,  # Must be False when allow_origins=["*"]
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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "CSV Upload Service is running", "timestamp": datetime.utcnow().isoformat()}


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
    question: str = Form(...)
):
    """
    Analyze uploaded data using AI agents based on user question
    
    Args:
        file: Data file to analyze (CSV, XLSX, or XLS)
        question: User's analysis question/request
        
    Returns:
        Complete analysis results with agent outputs and report
    """
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
        
        # Process analysis request through agent workflow
        analysis_result = await agent_service.analyze_request(
            file_content=file_content,
            filename=file.filename,
            user_question=question.strip()
        )
        
        # Add validation metadata
        analysis_result["file_validation"] = validation_result
        
        # Clean any NaN values to ensure JSON serializability
        cleaned_result = clean_nan_values(analysis_result)
        
        logger.info(f"Analysis completed for: {file.filename}")
        
        return cleaned_result
        
    except ValueError as ve:
        logger.error(f"Validation error in analyze_data: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
