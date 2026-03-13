import uuid
import logging
from typing import Optional, BinaryIO
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from backend.config import settings

logger = logging.getLogger(__name__)


class R2Storage:
    """Cloudflare R2 storage handler."""
    
    def __init__(self):
        self.endpoint_url = settings.R2_ENDPOINT_URL
        self.access_key = settings.R2_ACCESS_KEY_ID
        self.secret_key = settings.R2_SECRET_ACCESS_KEY
        self.bucket_name = settings.R2_BUCKET_NAME
        self.public_url = settings.R2_PUBLIC_URL
        
        self.s3_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize S3-compatible client for R2."""
        if not all([self.endpoint_url, self.access_key, self.secret_key]):
            logger.warning("R2 credentials not configured. Storage will be disabled.")
            return
        
        try:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(
                    signature_version="s3v4",
                    retries={"max_attempts": 3, "mode": "standard"}
                ),
            )
            logger.info("R2 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize R2 client: {e}")
            self.s3_client = None
    
    def is_configured(self) -> bool:
        """Check if R2 storage is properly configured."""
        return self.s3_client is not None
    
    def upload_file(
        self,
        file_data: bytes,
        original_filename: str,
        content_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload a file to R2 storage.
        
        Args:
            file_data: File bytes to upload
            original_filename: Original filename for extension
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        if not self.is_configured():
            logger.warning("R2 not configured, skipping upload")
            return None
        
        # Generate unique filename
        file_ext = original_filename.split(".")[-1] if "." in original_filename else "bin"
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        key = f"uploads/{unique_filename}"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type or "application/octet-stream",
            )
            
            # Return public URL
            if self.public_url:
                return f"{self.public_url}/{key}"
            else:
                return f"{self.endpoint_url}/{self.bucket_name}/{key}"
                
        except ClientError as e:
            logger.error(f"Failed to upload file to R2: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading to R2: {e}")
            return None
    
    def upload_converted_file(
        self,
        file_data: bytes,
        image_id: str,
        output_format: str,
        content_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload a converted file to R2 storage.
        
        Args:
            file_data: File bytes to upload
            image_id: ID of the image record
            output_format: Format of the converted file
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        if not self.is_configured():
            logger.warning("R2 not configured, skipping upload")
            return None
        
        key = f"converted/{image_id}.{output_format}"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type or "application/octet-stream",
            )
            
            if self.public_url:
                return f"{self.public_url}/{key}"
            else:
                return f"{self.endpoint_url}/{self.bucket_name}/{key}"
                
        except ClientError as e:
            logger.error(f"Failed to upload converted file to R2: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading converted file: {e}")
            return None
    
    def get_file(self, key: str) -> Optional[bytes]:
        """
        Download a file from R2 storage.
        
        Args:
            key: The object key in R2
            
        Returns:
            File bytes or None if failed
        """
        if not self.is_configured():
            return None
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Failed to download file from R2: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading from R2: {e}")
            return None
    
    def delete_file(self, key: str) -> bool:
        """
        Delete a file from R2 storage.
        
        Args:
            key: The object key in R2
            
        Returns:
            True if deleted successfully
        """
        if not self.is_configured():
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file from R2: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting from R2: {e}")
            return False
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access.
        
        Args:
            key: The object key in R2
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL or None if failed
        """
        if not self.is_configured():
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {e}")
            return None


# Singleton instance
r2_storage = R2Storage()
