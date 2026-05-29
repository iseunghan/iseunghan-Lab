"""Tests for MinIO Service."""

import json
import pytest
from unittest.mock import MagicMock, patch
from app.services.minio_service import MinIOService


class TestMinIOService:
    """Test suite for MinIOService."""

    @patch("app.services.minio_service.Minio")
    def test_service_initialization(self, mock_minio_class):
        """Test that service initializes correctly with connection params."""
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        endpoint = "localhost:9000"
        access_key = "test-access-key"
        secret_key = "test-secret-key"
        secure = False

        service = MinIOService(endpoint=endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

        assert service is not None
        assert service.endpoint == endpoint
        assert service.access_key == access_key
        assert service.secret_key == secret_key
        assert service.secure == secure
        mock_minio_class.assert_called_once()

    @patch("app.services.minio_service.Minio")
    def test_create_bucket_exists(self, mock_minio_class):
        """Test that bucket creation returns False when bucket already exists."""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.create_bucket(bucket_name="test-bucket")

        assert result is False
        mock_client.make_bucket.assert_not_called()

    @patch("app.services.minio_service.Minio")
    def test_create_bucket_new(self, mock_minio_class):
        """Test that creating a new bucket returns True."""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = False
        mock_minio_class.return_value = mock_client

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.create_bucket(bucket_name="new-bucket")

        assert result is True
        mock_client.make_bucket.assert_called_once_with("new-bucket")

    @patch("app.services.minio_service.Minio")
    def test_upload_object_success(self, mock_minio_class):
        """Test that uploading a file returns True on success."""
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.upload_object(bucket_name="test-bucket", object_name="test.txt", file_path="/tmp/test.txt")

        assert result is True
        mock_client.fput_object.assert_called_once_with("test-bucket", "test.txt", "/tmp/test.txt")

    @patch("app.services.minio_service.Minio")
    def test_upload_object_failure(self, mock_minio_class):
        """Test that uploading a file returns False on failure."""
        mock_client = MagicMock()
        mock_client.fput_object.side_effect = Exception("Upload failed")
        mock_minio_class.return_value = mock_client

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.upload_object(bucket_name="test-bucket", object_name="test.txt", file_path="/tmp/test.txt")

        assert result is False

    @patch("app.services.minio_service.Minio")
    def test_upload_bytes_success(self, mock_minio_class):
        """Test that uploading bytes returns True on success."""
        import io

        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        data = b"test data content"
        result = service.upload_bytes(bucket_name="test-bucket", object_name="data.bin", data=data, content_type="application/octet-stream")

        assert result is True
        # Verify put_object was called with BytesIO wrapper (as implementation does)
        call_args = mock_client.put_object.call_args
        assert call_args.args[0] == "test-bucket"
        assert call_args.args[1] == "data.bin"
        assert isinstance(call_args.args[2], io.BytesIO)
        assert call_args.args[3] == len(data)
        assert call_args.kwargs.get("content_type") == "application/octet-stream"

    @patch("app.services.minio_service.Minio")
    def test_upload_bytes_failure(self, mock_minio_class):
        """Test that uploading bytes returns False on failure."""
        mock_client = MagicMock()
        mock_client.put_object.side_effect = Exception("Upload failed")
        mock_minio_class.return_value = mock_client

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.upload_bytes(bucket_name="test-bucket", object_name="data.bin", data=b"test", content_type="text/plain")

        assert result is False

    @patch("app.services.minio_service.Minio")
    def test_list_objects(self, mock_minio_class):
        """Test that listing objects returns a list of object names."""
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        # Mock list_objects to return iterable of mock objects
        mock_obj1 = MagicMock()
        mock_obj1.object_name = "file1.txt"
        mock_obj2 = MagicMock()
        mock_obj2.object_name = "file2.txt"
        mock_client.list_objects.return_value = [mock_obj1, mock_obj2]

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.list_objects(bucket_name="test-bucket", prefix="data/")

        assert isinstance(result, list)
        assert len(result) == 2
        assert "file1.txt" in result
        assert "file2.txt" in result
        mock_client.list_objects.assert_called_once_with("test-bucket", prefix="data/", recursive=True)

    @patch("app.services.minio_service.Minio")
    def test_list_objects_empty(self, mock_minio_class):
        """Test that listing objects returns empty list when no objects exist."""
        mock_client = MagicMock()
        mock_client.list_objects.return_value = []
        mock_minio_class.return_value = mock_client

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.list_objects(bucket_name="test-bucket")

        assert result == []

    @patch("app.services.minio_service.Minio")
    def test_get_object_count(self, mock_minio_class):
        """Test that getting object count returns integer."""
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        mock_obj1 = MagicMock()
        mock_obj1.object_name = "file1.txt"
        mock_obj2 = MagicMock()
        mock_obj2.object_name = "file2.txt"
        mock_client.list_objects.return_value = [mock_obj1, mock_obj2]

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.get_object_count(bucket_name="test-bucket", prefix="data/")

        assert isinstance(result, int)
        assert result == 2

    @patch("app.services.minio_service.Minio")
    def test_close(self, mock_minio_class):
        """Test that close method works without error."""
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")
        service.close()

        # Close sets client to None
        assert service._client is None

    @patch("app.services.minio_service.Minio")
    def test_get_object_as_json_valid_json(self, mock_minio_class):
        """Test that get_object_as_json() successfully parses valid JSON.

        When MinIO returns valid JSON content, it should be parsed and returned as dict.
        """
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        # Mock get_object to return a file-like object with JSON content
        mock_json_data = json.dumps({
            "camera_id": "front",
            "frame_timestamp": "2026-05-22T10:00:00Z",
            "detected_objects": [
                {"class": "car", "confidence": 0.95, "bbox": [0.1, 0.2, 0.3, 0.4]},
                {"class": "pedestrian", "confidence": 0.87, "bbox": [0.5, 0.6, 0.2, 0.3]}
            ],
            "lane_detection": {"lanes_detected": 2, "confidence": 0.92}
        })
        mock_response = MagicMock()
        mock_response.read.return_value = mock_json_data.encode('utf-8')
        mock_client.get_object.return_value = mock_response

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.get_object_as_json(bucket_name="mlops-raw-media", object_name="metadata/frame_001.json")

        assert isinstance(result, dict)
        assert result["camera_id"] == "front"
        assert len(result["detected_objects"]) == 2
        assert result["detected_objects"][0]["class"] == "car"
        mock_client.get_object.assert_called_once_with("mlops-raw-media", "metadata/frame_001.json")
        mock_response.read.assert_called_once()

    @patch("app.services.minio_service.Minio")
    def test_get_object_as_json_invalid_json(self, mock_minio_class):
        """Test that get_object_as_json() returns None for invalid JSON.

        When MinIO returns non-JSON content, the method should handle the JSON decode error gracefully.
        """
        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        # Mock get_object to return invalid JSON content
        mock_response = MagicMock()
        mock_response.read.return_value = b"This is not JSON content"
        mock_client.get_object.return_value = mock_response

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.get_object_as_json(bucket_name="mlops-raw-media", object_name="metadata/invalid.json")

        assert result is None

    @patch("app.services.minio_service.Minio")
    def test_get_object_as_json_file_not_found(self, mock_minio_class):
        """Test that get_object_as_json() returns None when file not found.

        When MinIO raises an exception (e.g., file not found), the method should handle it gracefully.
        """
        from minio.error import S3Error

        mock_client = MagicMock()
        # Mock S3Error for file not found (code 404)
        mock_error = MagicMock(spec=S3Error)
        mock_error.code = "NoSuchKey"
        mock_error.status_code = 404
        mock_client.get_object.side_effect = mock_error
        mock_minio_class.return_value = mock_client

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.get_object_as_json(bucket_name="mlops-raw-media", object_name="metadata/nonexistent.json")

        assert result is None

    @patch("app.services.minio_service.Minio")
    def test_get_object_as_json_empty_object(self, mock_minio_class):
        """Test that get_object_as_json() handles empty JSON object correctly."""
        import json

        mock_client = MagicMock()
        mock_minio_class.return_value = mock_client

        # Mock get_object to return empty JSON object
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({}).encode('utf-8')
        mock_client.get_object.return_value = mock_response

        service = MinIOService(endpoint="localhost:9000", access_key="key", secret_key="secret")

        result = service.get_object_as_json(bucket_name="mlops-raw-media", object_name="metadata/empty.json")

        assert result == {}
