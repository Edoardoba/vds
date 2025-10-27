#!/usr/bin/env python3
"""
Fix and Run - Solves common issues and starts the server
Run this instead of start_server.py if you're having issues
"""
import subprocess
import sys

def main():
    print("🔧 Installing/updating dependencies...")
    
    # Install/update dependencies to fix pydantic issue
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies updated")
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return 1
    
    print("\n🚀 Starting server...")
    
    # Start the server directly with uvicorn
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server failed: {e}")
        print("\nTry running:")
        print("pip install -r requirements.txt")
        print("python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
