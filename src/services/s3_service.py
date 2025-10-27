import boto3
import asyncio
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Any, BinaryIO
import logging
from concurrent.futures import ThreadPoolExecutor

from config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service for handling S3 operations"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # Create S3 client
        self.s3_client = self.session.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL
        )
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def check_connection(self) -> bool:
        """
        Check if S3 connection is working
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self.s3_client.head_bucket,
                {'Bucket': settings.S3_BUCKET_NAME}
            )
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.warning(f"Bucket {settings.S3_BUCKET_NAME} does not exist")
            else:
                logger.error(f"S3 connection error: {str(e)}")
            return False
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking S3 connection: {str(e)}")
            return False
    
    async def create_bucket_if_not_exists(self) -> bool:
        """
        Create S3 bucket if it doesn't exist
        
        Returns:
            True if bucket exists or was created successfully
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Check if bucket exists
            try:
                await loop.run_in_executor(
                    self.executor,
                    self.s3_client.head_bucket,
                    {'Bucket': settings.S3_BUCKET_NAME}
                )
                logger.info(f"Bucket {settings.S3_BUCKET_NAME} already exists")
                return True
            except ClientError as e:
                if e.response['Error']['Code'] != '404':
                    raise e
            
            # Create bucket if it doesn't exist
            create_bucket_kwargs = {'Bucket': settings.S3_BUCKET_NAME}
            
            # Add location constraint if not in us-east-1
            if settings.AWS_REGION != 'us-east-1':
                create_bucket_kwargs['CreateBucketConfiguration'] = {
                    'LocationConstraint': settings.AWS_REGION
                }
            
            await loop.run_in_executor(
                self.executor,
                self.s3_client.create_bucket,
                create_bucket_kwargs
            )
            
            logger.info(f"Created bucket {settings.S3_BUCKET_NAME}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create bucket: {str(e)}")
            return False
    
    async def upload_file(
        self, 
        file_obj: BinaryIO, 
        key: str, 
        content_type: str = "text/csv"
    ) -> Dict[str, Any]:
        """
        Upload file to S3 bucket
        
        Args:
            file_obj: File object to upload
            key: S3 key (path) for the file
            content_type: MIME type of the file
            
        Returns:
            Upload response from S3
        """
        try:
            # Ensure bucket exists
            await self.create_bucket_if_not_exists()
            
            # Prepare upload parameters
            extra_args = {
                'ContentType': content_type,
                'Metadata': {
                    'upload-service': 'csv-upload-service',
                    'upload-timestamp': str(asyncio.get_event_loop().time())
                }
            }
            
            loop = asyncio.get_event_loop()
            
            # Upload file
            response = await loop.run_in_executor(
                self.executor,
                lambda: self.s3_client.upload_fileobj(
                    file_obj,
                    settings.S3_BUCKET_NAME,
                    key,
                    ExtraArgs=extra_args
                )
            )
            
            # Get file URL
            file_url = f"s3://{settings.S3_BUCKET_NAME}/{key}"
            if settings.S3_ENDPOINT_URL:
                file_url = f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{key}"
            
            return {
                "success": True,
                "key": key,
                "bucket": settings.S3_BUCKET_NAME,
                "url": file_url,
                "size": file_obj.tell() if hasattr(file_obj, 'tell') else None
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file {key}: {str(e)}")
            raise Exception(f"S3 upload failed: {str(e)}")
    
    async def list_files(self, prefix: str = None, max_keys: int = 100) -> List[Dict[str, Any]]:
        """
        List files in S3 bucket
        
        Args:
            prefix: Optional prefix to filter files
            max_keys: Maximum number of keys to return
            
        Returns:
            List of file information dictionaries
        """
        try:
            loop = asyncio.get_event_loop()
            
            list_params = {
                'Bucket': settings.S3_BUCKET_NAME,
                'MaxKeys': max_keys
            }
            
            if prefix:
                list_params['Prefix'] = prefix
            
            response = await loop.run_in_executor(
                self.executor,
                lambda: self.s3_client.list_objects_v2(**list_params)
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag'].strip('"'),
                        'storage_class': obj.get('StorageClass', 'STANDARD')
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            raise Exception(f"Failed to list S3 files: {str(e)}")
    
    async def delete_file(self, key: str) -> bool:
        """
        Delete file from S3 bucket
        
        Args:
            key: S3 key of the file to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                self.executor,
                lambda: self.s3_client.delete_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=key
                )
            )
            
            logger.info(f"Successfully deleted file: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {key}: {str(e)}")
            raise Exception(f"Failed to delete file: {str(e)}")
    
    def __del__(self):
        """Cleanup thread pool executor"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
