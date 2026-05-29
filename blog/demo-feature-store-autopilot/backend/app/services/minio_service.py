"""MinIO Service for object storage of media files and feature Parquet files."""

import io
import json
import logging
from typing import Any, Dict, List, Optional

from minio import Minio

logger = logging.getLogger(__name__)


class MinIOService:
    """Service for interacting with MinIO object storage."""

    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = False):
        """Initialize MinIO client.

        Args:
            endpoint: MinIO endpoint (e.g., "localhost:9000")
            access_key: Access key for authentication
            secret_key: Secret key for authentication
            secure: Use HTTPS (default: False)
        """
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure

        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def create_bucket(self, bucket_name: str) -> bool:
        """Create bucket if it doesn't exist.

        Args:
            bucket_name: Name of the bucket to create

        Returns:
            True if bucket was created, False if it already exists
        """
        try:
            if self._client.bucket_exists(bucket_name):
                logger.info(f"Bucket '{bucket_name}' already exists")
                return False

            self._client.make_bucket(bucket_name)
            logger.info(f"Bucket '{bucket_name}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create bucket '{bucket_name}': {e}")
            return False

    def upload_object(self, bucket_name: str, object_name: str, file_path: str) -> bool:
        """Upload a file to MinIO.

        Args:
            bucket_name: Target bucket name
            object_name: Object name (path within bucket)
            file_path: Local file path to upload

        Returns:
            True if upload was successful, False otherwise
        """
        try:
            self._client.fput_object(bucket_name, object_name, file_path)
            logger.info(f"Uploaded '{file_path}' to '{bucket_name}/{object_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to upload object '{object_name}' to '{bucket_name}': {e}")
            return False

    def upload_bytes(self, bucket_name: str, object_name: str, data: bytes, content_type: str) -> bool:
        """Upload bytes data to MinIO.

        Args:
            bucket_name: Target bucket name
            object_name: Object name (path within bucket)
            data: Bytes data to upload
            content_type: Content type of the data

        Returns:
            True if upload was successful, False otherwise
        """
        try:
            # Wrap bytes in BytesIO to provide a file-like object
            data_io = io.BytesIO(data)
            self._client.put_object(
                bucket_name,
                object_name,
                data_io,
                len(data),
                content_type=content_type
            )
            logger.info(f"Uploaded bytes to '{bucket_name}/{object_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to upload bytes to '{bucket_name}/{object_name}': {e}")
            return False

    def list_objects(self, bucket_name: str, prefix: str = '') -> List[str]:
        """List objects in a bucket.

        Args:
            bucket_name: Target bucket name
            prefix: Optional prefix to filter objects

        Returns:
            List of object names
        """
        try:
            objects = self._client.list_objects(bucket_name, prefix=prefix, recursive=True)
            object_names = [obj.object_name for obj in objects]
            logger.info(f"Listed {len(object_names)} objects in '{bucket_name}' with prefix '{prefix}'")
            return object_names
        except Exception as e:
            logger.error(f"Failed to list objects in '{bucket_name}': {e}")
            return []

    def get_object_count(self, bucket_name: str, prefix: str = '') -> int:
        """Get count of objects in a bucket.

        Args:
            bucket_name: Target bucket name
            prefix: Optional prefix to filter objects

        Returns:
            Integer count of objects
        """
        try:
            objects = self._client.list_objects(bucket_name, prefix=prefix, recursive=True)
            count = sum(1 for _ in objects)
            logger.info(f"Found {count} objects in '{bucket_name}' with prefix '{prefix}'")
            return count
        except Exception as e:
            logger.error(f"Failed to count objects in '{bucket_name}': {e}")
            return 0

    def get_object_as_json(self, bucket_name: str, object_name: str) -> Optional[Dict[str, Any]]:
        """Read and parse a JSON file from MinIO.

        Args:
            bucket_name: Source bucket name
            object_name: Object name (path to JSON file)

        Returns:
            Parsed JSON as dictionary, or None if file not found or parse error
        """
        try:
            response = self._client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()

            parsed = json.loads(data.decode('utf-8'))
            logger.info(f"Read JSON from '{bucket_name}/{object_name}'")
            return parsed
        except Exception as e:
            logger.warning(f"Failed to read JSON object '{object_name}' from '{bucket_name}': {e}")
            return None

    def get_object_bytes(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """Read object as bytes from MinIO."""
        try:
            response = self._client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except Exception as e:
            logger.warning(
                f"Failed to read object bytes '{object_name}' from '{bucket_name}': {e}"
            )
            return None

    def close(self):
        """Close the MinIO client connection."""
        # MinIO client doesn't have explicit close method, but we can set to None
        self._client = None
        logger.info("MinIO client closed")
