from minio import Minio
from minio.error import S3Error
import os
import io
from typing import BinaryIO
import logging

logger = logging.getLogger(__name__)

class MinIOClient:
    def __init__(self):
        self.client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "sgd_minio"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "sgd_minio_password"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true"
        )
    
    async def create_bucket_if_not_exists(self, bucket_name: str):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            else:
                logger.info(f"Bucket already exists: {bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket {bucket_name}: {e}")
            raise
    
    async def upload_file(
        self,
        bucket: str,
        object_name: str,
        file_data: BinaryIO,
        content_type: str,
        metadata: dict = None
    ) -> str:
        """Upload file to MinIO"""
        try:
            # Read file data
            file_content = file_data.read()
            file_size = len(file_content)
            
            # Upload file
            self.client.put_object(
                bucket,
                object_name,
                io.BytesIO(file_content),
                file_size,
                content_type=content_type,
                metadata=metadata
            )
            
            # Generate file URL
            file_url = f"http://{os.getenv('MINIO_ENDPOINT', 'localhost:9000')}/{bucket}/{object_name}"
            
            logger.info(f"Uploaded file: {object_name} to bucket: {bucket}")
            return file_url
            
        except S3Error as e:
            logger.error(f"Error uploading file {object_name}: {e}")
            raise
    
    async def download_file(self, bucket: str, object_name: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(bucket, object_name)
            return response.read()
        except S3Error as e:
            logger.error(f"Error downloading file {object_name}: {e}")
            raise
    
    async def delete_file(self, bucket: str, object_name: str):
        """Delete file from MinIO"""
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted file: {object_name} from bucket: {bucket}")
        except S3Error as e:
            logger.error(f"Error deleting file {object_name}: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if MinIO is healthy"""
        try:
            # List buckets to test connection
            self.client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"MinIO health check failed: {e}")
            return False