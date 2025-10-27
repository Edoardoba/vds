from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
import logging
from datetime import datetime

from config import settings
from services.s3_service import S3Service
from utils.validators import validate_csv_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CSV Upload Service",
    description="A FastAPI service for uploading CSV files to S3",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize S3 service
s3_service = S3Service()


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
        return {
            "status": "healthy",
            "services": {
                "s3": "connected" if s3_status else "disconnected"
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


@app.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    folder: Optional[str] = None
):
    """
    Upload a CSV file to S3 bucket
    
    Args:
        file: CSV file to upload
        folder: Optional folder path in S3 bucket
    
    Returns:
        Success message with file details
    """
    try:
        # Validate file
        await validate_csv_file(file)
        
        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        original_filename = file.filename
        file_extension = original_filename.split('.')[-1] if '.' in original_filename else 'csv'
        unique_filename = f"{timestamp}_{original_filename}"
        
        # Construct S3 key
        s3_key = f"{folder}/{unique_filename}" if folder else unique_filename
        
        # Reset file pointer to beginning
        await file.seek(0)
        
        # Upload to S3
        upload_result = await s3_service.upload_file(
            file_obj=file.file,
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
                "file_size": file.size if hasattr(file, 'size') else None,
                "content_type": file.content_type
            },
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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
