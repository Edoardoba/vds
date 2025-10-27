# Dockerfile for Render deployment (optional)
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Start command
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
