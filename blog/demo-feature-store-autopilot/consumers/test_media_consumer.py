"""
Tests for media consumer separate storage functions.
"""

import io
import pytest
from datetime import datetime, timezone
from media_consumer import store_camera_metadata, store_audio_metadata, _get_date_str
from unittest.mock import MagicMock, patch


class TestStoreCameraMetadata:
    """Test store_camera_metadata function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_minio_client = MagicMock()
        self.vehicle_id = "test-vehicle-001"
        self.event_id = "event-123"

    def test_stores_camera_frames_to_images_prefix(self):
        """When camera_frames exist, store to images/ prefix."""
        media_data = {
            "camera_frames": {"path": "/path/to/frame.jpg", "count": 5},
            "timestamp": "2026-05-22T10:00:00Z"
        }

        result = store_camera_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is True
        # Verify the object key uses images/ prefix
        call_args = self.mock_minio_client.put_object.call_args
        object_key = call_args.kwargs["object_name"]
        assert object_key.startswith("images/test-vehicle-001/")

    def test_returns_false_when_camera_frames_missing(self):
        """When camera_frames is missing, return False without storing."""
        media_data = {
            "audio": {"path": "/path/to/audio.mp3"},
            "timestamp": "2026-05-22T10:00:00Z"
        }

        result = store_camera_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is False
        # put_object should not be called
        self.mock_minio_client.put_object.assert_not_called()

    def test_returns_false_when_camera_frames_empty(self):
        """When camera_frames is empty, return False without storing."""
        media_data = {
            "camera_frames": [],
            "timestamp": "2026-05-22T10:00:00Z"
        }

        result = store_camera_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is False
        self.mock_minio_client.put_object.assert_not_called()

    def test_stored_metadata_contains_camera_frames_only(self):
        """Verify the stored JSON contains only camera_frames data."""
        media_data = {
            "camera_frames": {"path": "/path/to/frame.jpg", "count": 5},
            "timestamp": "2026-05-22T10:00:00Z"
        }

        result = store_camera_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is True
        call_args = self.mock_minio_client.put_object.call_args
        data = call_args.kwargs["data"]
        content_type = call_args.kwargs["content_type"]

        assert content_type == "application/json"
        assert isinstance(data, io.BytesIO)

        # Read the actual data
        data.seek(0)
        import json
        stored_json = json.load(data)

        assert stored_json["media_type"] == "images"
        assert stored_json["camera_frames"] == {"path": "/path/to/frame.jpg", "count": 5}
        assert "audio" not in stored_json

    def test_missing_timestamp_uses_current_time(self):
        """When timestamp is missing, use current UTC time."""
        media_data = {
            "camera_frames": {"path": "/path/to/frame.jpg"}
        }

        result = store_camera_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is True
        call_args = self.mock_minio_client.put_object.call_args
        object_key = call_args.kwargs["object_name"]
        assert "images/test-vehicle-001/" in object_key


class TestStoreAudioMetadata:
    """Test store_audio_metadata function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_minio_client = MagicMock()
        self.vehicle_id = "test-vehicle-001"
        self.event_id = "event-456"

    def test_stores_audio_to_audio_prefix(self):
        """When audio exists, store to audio/ prefix."""
        media_data = {
            "audio": {"path": "/path/to/audio.mp3", "duration": 30},
            "timestamp": "2026-05-22T10:00:00Z"
        }

        result = store_audio_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is True
        # Verify the object key uses audio/ prefix
        call_args = self.mock_minio_client.put_object.call_args
        object_key = call_args.kwargs["object_name"]
        assert object_key.startswith("audio/test-vehicle-001/")

    def test_returns_false_when_audio_missing(self):
        """When audio is missing, return False without storing."""
        media_data = {
            "camera_frames": {"path": "/path/to/frame.jpg"},
            "timestamp": "2026-05-22T10:00:00Z"
        }

        result = store_audio_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is False
        self.mock_minio_client.put_object.assert_not_called()

    def test_returns_false_when_audio_empty(self):
        """When audio is empty, return False without storing."""
        media_data = {
            "audio": {},
            "timestamp": "2026-05-22T10:00:00Z"
        }

        result = store_audio_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is False
        self.mock_minio_client.put_object.assert_not_called()

    def test_stored_metadata_contains_audio_only(self):
        """Verify the stored JSON contains only audio data."""
        media_data = {
            "audio": {"path": "/path/to/audio.mp3", "duration": 30},
            "timestamp": "2026-05-22T10:00:00Z"
        }

        result = store_audio_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is True
        call_args = self.mock_minio_client.put_object.call_args
        data = call_args.kwargs["data"]
        content_type = call_args.kwargs["content_type"]

        assert content_type == "application/json"
        assert isinstance(data, io.BytesIO)

        # Read the actual data
        data.seek(0)
        import json
        stored_json = json.load(data)

        assert stored_json["media_type"] == "audio"
        assert stored_json["audio"] == {"path": "/path/to/audio.mp3", "duration": 30}
        assert "camera_frames" not in stored_json

    def test_missing_timestamp_uses_current_time(self):
        """When timestamp is missing, use current UTC time."""
        media_data = {
            "audio": {"path": "/path/to/audio.mp3"}
        }

        result = store_audio_metadata(
            self.mock_minio_client, media_data, self.vehicle_id, self.event_id
        )

        assert result is True
        call_args = self.mock_minio_client.put_object.call_args
        object_key = call_args.kwargs["object_name"]
        assert "audio/test-vehicle-001/" in object_key


class TestGetDateStr:
    """Test _get_date_str helper function."""

    def test_parses_iso_timestamp_with_z(self):
        """Parse ISO timestamp with Z suffix."""
        result = _get_date_str("2026-05-22T10:00:00Z")
        assert result == "2026/05/22"

    def test_parses_iso_timestamp_without_z(self):
        """Parse ISO timestamp without Z suffix."""
        result = _get_date_str("2026-05-22T10:00:00")
        assert result == "2026/05/22"

    def test_handles_invalid_timestamp(self):
        """Return current date when timestamp is invalid."""
        result = _get_date_str("invalid-timestamp")
        expected = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        assert result == expected

    def test_handles_none_timestamp(self):
        """Return current date when timestamp is None."""
        result = _get_date_str(None)
        expected = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
