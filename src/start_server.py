#!/usr/bin/env python3
"""
Startup script for CSV Upload Service
This script helps set up and start the FastAPI service
"""
import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import boto3
        print("✅ Required dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def check_env_file():
    """Check if .env file exists and has required variables"""
    # Look for .env file in both current directory and parent directory
    env_file_current = Path(".env")
    env_file_parent = Path("../.env")
    
    env_file = None
    if env_file_current.exists():
        env_file = env_file_current
    elif env_file_parent.exists():
        env_file = env_file_parent
    
    if env_file is None:
        print("⚠️  .env file not found")
        print("Please create a .env file with your AWS configuration:")
        print("You can place it in the current directory or parent directory")
        print("""
# Example .env file content:
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=csv-upload-bucket
DEBUG=true
        """)
        return False
    
    print(f"✅ .env file found at: {env_file}")
    return True


def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting CSV Upload Service...")
    print("API will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        # Start server from current directory (should be src/)
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start server")
        return False
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return True


def main():
    """Main startup function"""
    print("CSV Upload Service - Startup Script")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    if not check_dependencies():
        return 1
    
    if not check_env_file():
        print("\nSetup incomplete. Please configure your environment first.")
        return 1
    
    # Start server
    start_server()
    return 0


if __name__ == "__main__":
    exit(main())
