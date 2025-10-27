#!/usr/bin/env python3
"""
Quick Launch Script for Banta Dashboard
Fixes common issues and launches the service
"""
import os
import sys
import subprocess
from pathlib import Path

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_content = """# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# AWS S3 Configuration (Update these with your actual values!)
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=csv-upload-bucket

# Optional: For LocalStack or MinIO (local development)
# S3_ENDPOINT_URL=http://localhost:4566

# File Upload Settings  
MAX_FILE_SIZE=52428800"""

    env_file = Path('.env')
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  IMPORTANT: Edit .env with your AWS credentials!")
        return False
    else:
        print("✅ .env file already exists")
        return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        os.chdir('src')
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed")
        os.chdir('..')
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        os.chdir('..')
        return False

def launch_backend():
    """Launch the backend service"""
    print("🚀 Starting backend...")
    try:
        os.chdir('src')
        subprocess.run([sys.executable, 'start_server.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server failed: {e}")
    finally:
        os.chdir('..')

def main():
    print("=" * 50)
    print("🚀 BANTA DASHBOARD QUICK LAUNCHER")
    print("=" * 50)
    
    # Create .env if needed
    env_exists = create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    if not env_exists:
        print("\n" + "=" * 50)
        print("⚠️  SETUP REQUIRED")
        print("=" * 50)
        print("1. Edit the .env file with your AWS credentials")
        print("2. Run this script again")
        print("\nRequired in .env file:")
        print("- AWS_ACCESS_KEY_ID")
        print("- AWS_SECRET_ACCESS_KEY") 
        print("- S3_BUCKET_NAME")
        return 1
    
    # Launch backend
    print("\n" + "=" * 50)
    print("🚀 LAUNCHING BACKEND")
    print("=" * 50)
    launch_backend()

if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nPress Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Launch cancelled")
        sys.exit(1)
