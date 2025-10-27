"""
Simple test script to verify the API functionality
Run this after starting the service to test basic functionality
"""
import requests
import io
import csv


def test_health_check():
    """Test health check endpoint"""
    response = requests.get("http://localhost:8000/health")
    print(f"Health check status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def create_test_csv():
    """Create a simple test CSV file in memory"""
    csv_content = """Name,Age,City
John Doe,30,New York
Jane Smith,25,Los Angeles
Bob Johnson,35,Chicago
"""
    return io.BytesIO(csv_content.encode('utf-8'))


def test_csv_upload():
    """Test CSV file upload"""
    # Create test CSV
    csv_file = create_test_csv()
    
    # Prepare files for upload
    files = {
        'file': ('test_data.csv', csv_file, 'text/csv')
    }
    
    # Optional folder parameter
    data = {
        'folder': 'test-uploads'
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/upload-csv", 
            files=files,
            data=data
        )
        print(f"Upload status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the service is running.")
        return False


def test_list_files():
    """Test listing files"""
    try:
        response = requests.get("http://localhost:8000/list-files")
        print(f"List files status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the service is running.")
        return False


if __name__ == "__main__":
    print("Testing CSV Upload Service API")
    print("=" * 40)
    
    # Test health check
    print("\n1. Testing health check...")
    health_ok = test_health_check()
    
    if health_ok:
        # Test file upload
        print("\n2. Testing CSV upload...")
        upload_ok = test_csv_upload()
        
        # Test file listing
        print("\n3. Testing file listing...")
        list_ok = test_list_files()
        
        print("\n" + "=" * 40)
        if upload_ok and list_ok:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed. Check your S3 configuration.")
    else:
        print("\n❌ Health check failed. Check your service configuration.")
    
    print("\nNote: Make sure to:")
    print("1. Start the service: python src/main.py")
    print("2. Configure AWS credentials in .env file")
    print("3. Ensure S3 bucket exists or service can create it")
