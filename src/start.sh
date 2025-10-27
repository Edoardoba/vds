#!/bin/bash

# Render startup script for Banta API
echo "Starting Banta API server..."

# Start the FastAPI application with uvicorn
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
