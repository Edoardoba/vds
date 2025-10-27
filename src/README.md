# CSV Upload Service

A FastAPI-based backend service for uploading CSV files to Amazon S3.

## Features

- **CSV File Upload**: Upload CSV files with validation
- **S3 Integration**: Store files securely in Amazon S3
- **File Validation**: Comprehensive CSV format and content validation
- **Health Checks**: Monitor service and S3 connectivity
- **File Management**: List and manage uploaded files
- **CORS Support**: Ready for frontend integration
- **Async Operations**: Non-blocking file operations

## Quick Start

### Prerequisites

- Python 3.8 or higher
- AWS Account with S3 access
- AWS credentials configured

### Installation

1. **Clone the repository and navigate to the project directory**

2. **Install dependencies**:
   ```bash
   pip install -r src/requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=true

   # AWS S3 Configuration
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=csv-upload-bucket

   # Optional: For LocalStack or MinIO (local development)
   # S3_ENDPOINT_URL=http://localhost:4566
   ```

4. **Run the application**:
   
   **Option 1: Using the startup script (recommended)**:
   ```bash
   cd src
   python start_server.py
   ```
   
   **Option 2: Direct execution**:
   ```bash
   cd src
   python main.py
   ```

   **Option 3: Using uvicorn directly**:
   ```bash
   cd src
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Detailed health check including S3 connectivity

### File Upload
- **POST** `/upload-csv` - Upload a CSV file
  - **Parameters**: 
    - `file`: CSV file (required)
    - `folder`: Optional S3 folder path
  - **Response**: Upload confirmation with file details

### File Management
- **GET** `/list-files` - List uploaded files
  - **Parameters**: 
    - `folder`: Optional folder path to filter files

## API Usage Examples

### Upload a CSV file
```bash
curl -X POST "http://localhost:8000/upload-csv" \
     -F "file=@your_file.csv" \
     -F "folder=data/2024"
```

### List files
```bash
curl "http://localhost:8000/list-files?folder=data"
```

### Check service health
```bash
curl "http://localhost:8000/health"
```

## Configuration

The service can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Enable debug mode | `true` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `AWS_REGION` | AWS region | `us-east-1` |
| `S3_BUCKET_NAME` | S3 bucket name | `csv-upload-bucket` |
| `S3_ENDPOINT_URL` | Custom S3 endpoint (optional) | None |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `52428800` (50MB) |

## File Validation

The service validates uploaded files for:

- **File extension**: Must be `.csv`
- **File size**: Must not exceed `MAX_FILE_SIZE`
- **Content type**: Must be CSV-compatible MIME type
- **CSV format**: Valid CSV structure with proper delimiters
- **File encoding**: UTF-8 or Latin-1 encoding
- **Security**: Filename validation to prevent directory traversal

## Development

### Local Development with LocalStack

For local development, you can use LocalStack to simulate S3:

1. **Install LocalStack**:
   ```bash
   pip install localstack
   ```

2. **Start LocalStack**:
   ```bash
   localstack start
   ```

3. **Update environment variables**:
   ```env
   S3_ENDPOINT_URL=http://localhost:4566
   AWS_ACCESS_KEY_ID=test
   AWS_SECRET_ACCESS_KEY=test
   ```

### Running Tests

Run the test script to verify API functionality:
```bash
cd src
python test_api.py
```

Or use pytest for unit tests:
```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```

## Docker Support

Create a `Dockerfile` for containerization:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Production Deployment

For production deployment:

1. **Set `DEBUG=false`**
2. **Configure CORS origins** appropriately in `main.py`
3. **Use environment-specific AWS credentials**
4. **Set up proper logging and monitoring**
5. **Use a production WSGI server** like Gunicorn with Uvicorn workers
6. **Implement rate limiting** and authentication as needed

## Security Considerations

- AWS credentials should be managed securely (IAM roles, AWS Secrets Manager)
- Implement authentication and authorization for production use
- Configure CORS origins restrictively for production
- Consider implementing file scanning for malicious content
- Use HTTPS in production
- Implement rate limiting to prevent abuse

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid file or validation errors
- `500 Internal Server Error`: S3 or server errors
- `503 Service Unavailable`: S3 connection issues

## License

This project is licensed under the MIT License.
