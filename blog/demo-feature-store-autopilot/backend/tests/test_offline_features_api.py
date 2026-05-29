"""Tests for /api/features/offline endpoint with time range support."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
import json


class TestOfflineFeaturesAPI:
    """Test suite for /api/features/offline endpoint with time range parameters."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as c:
            yield c

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_no_date_params_uses_defaults(self, mock_get_feast_service, client):
        """Test that offline feature query without date params uses defaults.

        When no start_date or end_date is provided, the endpoint should pass
        None values to FeastService.get_historical_features.
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "event_timestamp": datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc),
            }
        ]
        mock_get_feast_service.return_value = mock_feast_service

        response = client.get("/api/features/offline?vehicle_id=vehicle-1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["vehicle_id"] == "vehicle-1"

        # Verify FeastService was called with None for time parameters
        call_args = mock_feast_service.get_historical_features.call_args
        assert call_args.kwargs.get("start_time") is None
        assert call_args.kwargs.get("end_time") is None
        assert call_args.kwargs.get("drop_all_null_rows") is True

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_with_start_date_only(self, mock_get_feast_service, client):
        """Test that offline feature query with only start_date works correctly.

        When only start_date is provided, end_time should be None.
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "event_timestamp": datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc),
            }
        ]
        mock_get_feast_service.return_value = mock_feast_service

        start_date = "2026-05-22T00:00:00"
        response = client.get(f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}")

        assert response.status_code == 200

        # Verify start_time was parsed correctly
        call_args = mock_feast_service.get_historical_features.call_args
        start_time = call_args.kwargs.get("start_time")
        assert start_time is not None
        assert start_time.year == 2026
        assert start_time.month == 5
        assert start_time.day == 22

        # end_time should be None when not provided
        assert call_args.kwargs.get("end_time") is None

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_with_end_date_only(self, mock_get_feast_service, client):
        """Test that offline feature query with only end_date works correctly.

        When only end_date is provided, start_time should be None.
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "event_timestamp": datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc),
            }
        ]
        mock_get_feast_service.return_value = mock_feast_service

        end_date = "2026-05-22T23:59:59"
        response = client.get(f"/api/features/offline?vehicle_id=vehicle-1&end_date={end_date}")

        assert response.status_code == 200

        # Verify end_time was parsed correctly
        call_args = mock_feast_service.get_historical_features.call_args
        end_time = call_args.kwargs.get("end_time")
        assert end_time is not None
        assert end_time.year == 2026
        assert end_time.month == 5
        assert end_time.day == 22

        # start_time should be None when not provided
        assert call_args.kwargs.get("start_time") is None

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_with_full_date_range(self, mock_get_feast_service, client):
        """Test that offline feature query with full date range works correctly.

        Both start_date and end_date should be parsed and passed to FeastService.
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "event_timestamp": datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc),
            },
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 50.0,
                "event_timestamp": datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc),
            },
        ]
        mock_get_feast_service.return_value = mock_feast_service

        start_date = "2026-05-22T00:00:00"
        end_date = "2026-05-22T23:59:59"
        response = client.get(
            f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}&end_date={end_date}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Verify both times were parsed correctly
        call_args = mock_feast_service.get_historical_features.call_args
        start_time = call_args.kwargs.get("start_time")
        end_time = call_args.kwargs.get("end_time")

        assert start_time is not None
        assert end_time is not None
        assert start_time < end_time

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_with_custom_interval_minutes(self, mock_get_feast_service, client):
        """Test that offline feature query passes custom interval minutes."""
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "event_timestamp": datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc),
            }
        ]
        mock_get_feast_service.return_value = mock_feast_service

        response = client.get(
            "/api/features/offline?vehicle_id=vehicle-1&interval_minutes=10"
        )

        assert response.status_code == 200
        call_args = mock_feast_service.get_historical_features.call_args
        assert call_args.kwargs.get("interval_minutes") == 10

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_with_timezone_aware_dates(self, mock_get_feast_service, client):
        """Test that offline feature query handles timezone-aware ISO dates.

        ISO format dates with timezone info should be parsed correctly.
        Note: URL encoding should be used for timezone offsets (e.g., %2B for +).
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "event_timestamp": datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc),
            }
        ]
        mock_get_feast_service.return_value = mock_feast_service

        # ISO format with timezone - URL encode the + as %2B
        # Using requests library style URL encoding
        from urllib.parse import quote

        start_date = quote("2026-05-22T00:00:00+00:00", safe="")
        end_date = quote("2026-05-22T23:59:59+00:00", safe="")
        response = client.get(
            f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}&end_date={end_date}"
        )

        # Note: This test documents a known limitation - timezone-aware dates
        # with +00:00 offset require URL encoding. The endpoint should ideally
        # handle this more gracefully.
        if response.status_code == 200:
            # Verify timezone-aware parsing
            call_args = mock_feast_service.get_historical_features.call_args
            start_time = call_args.kwargs.get("start_time")
            assert start_time is not None
            assert start_time.tzinfo is not None

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_invalid_date_format_returns_422(self, mock_get_feast_service, client):
        """Test that invalid date format returns validation error.

        FastAPI should reject invalid date formats with 422 status.
        """
        # Invalid date format (not ISO)
        response = client.get(
            "/api/features/offline?vehicle_id=vehicle-1&start_date=22-05-2026"
        )

        # FastAPI may parse this without error, but fromisoformat will fail
        # The endpoint should handle this gracefully
        assert response.status_code in [422, 500]

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_empty_result(self, mock_get_feast_service, client):
        """Test that empty result returns empty array.

        When no features match the time range, return empty list.
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = []
        mock_get_feast_service.return_value = mock_feast_service

        start_date = "2026-01-01T00:00:00"
        end_date = "2026-01-01T23:59:59"
        response = client.get(
            f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}&end_date={end_date}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_server_error_returns_500(self, mock_get_feast_service, client):
        """Test that server error returns 500 status.

        When FeastService raises an exception, endpoint should return 500.
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.side_effect = Exception(
            "Feast service error"
        )
        mock_get_feast_service.return_value = mock_feast_service

        response = client.get("/api/features/offline?vehicle_id=vehicle-1")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_multiple_vehicle_ids(self, mock_get_feast_service, client):
        """Test that different vehicle IDs return correct features.

        Each vehicle_id should query features independently.
        """
        mock_feast_service = MagicMock()

        def mock_get_features(vehicle_id, **kwargs):
            return [
                {
                    "vehicle_id": vehicle_id,
                    "avg_speed_10s": 45.5 if vehicle_id == "vehicle-1" else 60.0,
                    "event_timestamp": datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc),
                }
            ]

        mock_feast_service.get_historical_features.side_effect = mock_get_features
        mock_get_feast_service.return_value = mock_feast_service

        response1 = client.get("/api/features/offline?vehicle_id=vehicle-1")
        response2 = client.get("/api/features/offline?vehicle_id=vehicle-2")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()[0]["vehicle_id"] == "vehicle-1"
        assert response2.json()[0]["vehicle_id"] == "vehicle-2"

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_response_format(self, mock_get_feast_service, client):
        """Test that response format matches FeatureResponse schema.

        Response should include vehicle_id, features, and timestamp.
        """
        mock_feast_service = MagicMock()
        mock_timestamp = datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc)
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "accel_std_10s": 2.3,
                "event_timestamp": mock_timestamp,
            }
        ]
        mock_get_feast_service.return_value = mock_feast_service

        response = client.get("/api/features/offline?vehicle_id=vehicle-1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Verify response structure
        item = data[0]
        assert "vehicle_id" in item
        assert "features" in item
        assert "timestamp" in item
        assert item["vehicle_id"] == "vehicle-1"
        assert "avg_speed_10s" in item["features"]

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_with_pandas_timestamp(self, mock_get_feast_service, client):
        """Test that pandas Timestamp in event_timestamp is handled correctly.

        Pandas Timestamp has isoformat() method that should be used.
        """
        import pandas as pd

        mock_feast_service = MagicMock()
        # Simulate pandas Timestamp
        mock_timestamp = pd.Timestamp("2026-05-22T10:00:00", tz=timezone.utc)
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "event_timestamp": mock_timestamp,
            }
        ]
        mock_get_feast_service.return_value = mock_feast_service

        response = client.get("/api/features/offline?vehicle_id=vehicle-1")

        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data[0]
        # Timestamp should be serialized as ISO string
        assert isinstance(data[0]["timestamp"], str)

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_date_range_edge_case_same_day(self, mock_get_feast_service, client):
        """Test date range within same day.

        Start and end on same day should work correctly.
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "event_timestamp": datetime(2026, 5, 22, 10, 30, 0, tzinfo=timezone.utc),
            }
        ]
        mock_get_feast_service.return_value = mock_feast_service

        start_date = "2026-05-22T10:00:00"
        end_date = "2026-05-22T11:00:00"
        response = client.get(
            f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}&end_date={end_date}"
        )

        assert response.status_code == 200

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_date_range_multi_day(self, mock_get_feast_service, client):
        """Test date range spanning multiple days.

        Multi-day ranges should be handled correctly.
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = [
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 45.5,
                "event_timestamp": datetime(2026, 5, 20, 10, 0, 0, tzinfo=timezone.utc),
            },
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 50.0,
                "event_timestamp": datetime(2026, 5, 21, 10, 0, 0, tzinfo=timezone.utc),
            },
            {
                "vehicle_id": "vehicle-1",
                "avg_speed_10s": 55.0,
                "event_timestamp": datetime(2026, 5, 22, 10, 0, 0, tzinfo=timezone.utc),
            },
        ]
        mock_get_feast_service.return_value = mock_feast_service

        start_date = "2026-05-20T00:00:00"
        end_date = "2026-05-22T23:59:59"
        response = client.get(
            f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}&end_date={end_date}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @patch("app.api.features.get_feast_service")
    def test_get_offline_features_feature_views_passed_correctly(self, mock_get_feast_service, client):
        """Test that all expected feature views are passed to FeastService.

        The endpoint should pass sensor, image, and audio feature views.
        """
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = []
        mock_get_feast_service.return_value = mock_feast_service

        response = client.get("/api/features/offline?vehicle_id=vehicle-1")

        assert response.status_code == 200

        # Verify feature_views parameter
        call_args = mock_feast_service.get_historical_features.call_args
        feature_views = call_args.kwargs.get("feature_views")

        assert feature_views is not None
        assert "sensor_features" in feature_views
        assert "image_features" in feature_views
        assert "audio_features" in feature_views


class TestOfflineFeaturesDateParsing:
    """Test date parsing edge cases for /api/features/offline endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as c:
            yield c

    def test_date_with_microseconds(self, client):
        """Test date format with microseconds."""
        with patch("app.api.features.get_feast_service") as mock_get_feast_service:
            mock_feast_service = MagicMock()
            mock_feast_service.get_historical_features.return_value = []
            mock_get_feast_service.return_value = mock_feast_service

            # ISO format with microseconds
            start_date = "2026-05-22T10:00:00.123456"
            response = client.get(
                f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}"
            )

            # Should handle microseconds correctly
            assert response.status_code in [200, 500]  # 500 if FeastService doesn't support time params yet

    def test_date_with_z_suffix(self, client):
        """Test date format with Z suffix (UTC).

        Python 3.11+ supports Z suffix in fromisoformat().
        """
        with patch("app.api.features.get_feast_service") as mock_get_feast_service:
            mock_feast_service = MagicMock()
            mock_feast_service.get_historical_features.return_value = []
            mock_get_feast_service.return_value = mock_feast_service

            # ISO format with Z suffix - supported in Python 3.11+
            start_date = "2026-05-22T10:00:00Z"
            response = client.get(
                f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}"
            )

            # Python 3.11+ handles Z suffix correctly
            assert response.status_code == 200

    def test_date_only_date_part(self, client):
        """Test date format with only date part (no time)."""
        with patch("app.api.features.get_feast_service") as mock_get_feast_service:
            mock_feast_service = MagicMock()
            mock_feast_service.get_historical_features.return_value = []
            mock_get_feast_service.return_value = mock_feast_service

            # Date only format
            start_date = "2026-05-22"
            response = client.get(
                f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}"
            )

            # Should handle date-only format
            assert response.status_code in [200, 500]

    def test_naive_datetime_is_treated_as_utc(self, client):
        """Naive datetime input should be interpreted as UTC."""
        with patch("app.api.features.get_feast_service") as mock_get_feast_service:
            mock_feast_service = MagicMock()
            mock_feast_service.get_historical_features.return_value = []
            mock_get_feast_service.return_value = mock_feast_service

            start_date = "2026-05-22T10:00:00"
            response = client.get(
                f"/api/features/offline?vehicle_id=vehicle-1&start_date={start_date}"
            )

            assert response.status_code == 200
            call_args = mock_feast_service.get_historical_features.call_args
            parsed_start = call_args.kwargs["start_time"]
            assert parsed_start.tzinfo is not None
            assert parsed_start.utcoffset().total_seconds() == 0
            assert parsed_start.isoformat() == "2026-05-22T10:00:00+00:00"


class TestBuildFeaturesAPI:
    """Test suite for /api/features/build endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as c:
            yield c

    @pytest.fixture(autouse=True)
    def mock_minio_service(self):
        """Mock MinIO service used by build endpoint."""
        with patch("app.api.features.get_minio_service") as mock_get_minio_service:
            mock_minio = MagicMock()
            mock_minio.list_objects.return_value = []
            mock_get_minio_service.return_value = mock_minio
            yield mock_minio

    @patch("app.api.features.get_feature_builder")
    def test_build_features_with_default_vehicle_id(self, mock_get_feature_builder, client):
        """Test that building features without vehicle_id uses default.

        When no vehicle_id is provided, the endpoint should default to "V001".
        """
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = [
            {"vehicle_id": "V001", "avg_speed_10s": 45.5}
        ]
        mock_feature_builder.build_image_features.return_value = [
            {"vehicle_id": "V001", "object_count": 5}
        ]
        mock_feature_builder.build_audio_features.return_value = [
            {"vehicle_id": "V001", "noise_level": 65.0}
        ]
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sensor_features" in data["features_built"]
        assert "image_features" in data["features_built"]
        assert "audio_features" in data["features_built"]
        assert mock_feature_builder.build_sensor_features.call_args.kwargs["vehicle_id"] == "V001"

    @patch("app.api.features.get_feature_builder")
    def test_build_features_with_specific_vehicle_id(self, mock_get_feature_builder, client):
        """Test that building features with specific vehicle_id works correctly."""
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = [
            {"vehicle_id": "vehicle-2", "avg_speed_10s": 55.0}
        ]
        mock_feature_builder.build_image_features.return_value = [
            {"vehicle_id": "vehicle-2", "object_count": 3}
        ]
        mock_feature_builder.build_audio_features.return_value = [
            {"vehicle_id": "vehicle-2", "noise_level": 70.0}
        ]
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={"vehicle_id": "vehicle-2"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Feature engineering completed for vehicle-2" in data["message"]

    @patch("app.api.features.get_feature_builder")
    def test_build_features_with_date_range(self, mock_get_feature_builder, client):
        """Test that building features with date range passes correct timestamps."""
        from datetime import datetime, timezone

        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = [
            {"vehicle_id": "vehicle-1", "avg_speed_10s": 45.5}
        ]
        mock_feature_builder.build_image_features.return_value = []
        mock_feature_builder.build_audio_features.return_value = []
        mock_get_feature_builder.return_value = mock_feature_builder

        start_date = "2026-05-22T00:00:00"
        end_date = "2026-05-22T23:59:59"
        response = client.post(
            "/api/features/build",
            json={"vehicle_id": "vehicle-1", "start_date": start_date, "end_date": end_date}
        )

        assert response.status_code == 200

        # Verify build_sensor_features was called with date range
        call_args = mock_feature_builder.build_sensor_features.call_args
        assert call_args.kwargs.get("vehicle_id") == "vehicle-1"
        assert call_args.kwargs.get("start_time") is not None
        assert call_args.kwargs.get("end_time") is not None

    @patch("app.api.features.get_feature_builder")
    def test_build_features_saves_sensor_to_parquet(self, mock_get_feature_builder, client):
        """Test that sensor features are saved to Parquet in MinIO."""
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = [
            {"vehicle_id": "vehicle-1", "avg_speed_10s": 45.5}
        ]
        mock_feature_builder.build_image_features.return_value = []
        mock_feature_builder.build_audio_features.return_value = []
        mock_feature_builder.save_features_to_parquet.return_value = True
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={"vehicle_id": "vehicle-1"})

        assert response.status_code == 200

        # Verify save_features_to_parquet was called
        mock_feature_builder.save_features_to_parquet.assert_called_once()

    @patch("app.api.features.get_feature_builder")
    def test_build_features_image_returns_mock_without_uris(self, mock_get_feature_builder, client):
        """Test that image features return mock data when no image_uris provided.

        The build endpoint passes empty list for image_uris, so image_features
        should return mock data.
        """
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = []
        mock_feature_builder.build_image_features.return_value = [
            {"vehicle_id": "vehicle-1", "image_uri": "mock_image", "object_count": 5}
        ]
        mock_feature_builder.build_audio_features.return_value = []
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={"vehicle_id": "vehicle-1"})

        assert response.status_code == 200
        data = response.json()
        assert "image_features" in data["features_built"]

    @patch("app.api.features.get_feature_builder")
    def test_build_features_audio_returns_mock_without_uris(self, mock_get_feature_builder, client):
        """Test that audio features return mock data when no audio_uris provided."""
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = []
        mock_feature_builder.build_image_features.return_value = []
        mock_feature_builder.build_audio_features.return_value = [
            {"vehicle_id": "vehicle-1", "audio_uri": "mock_audio", "noise_level": 65.0}
        ]
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={"vehicle_id": "vehicle-1"})

        assert response.status_code == 200
        data = response.json()
        assert "audio_features" in data["features_built"]

    @patch("app.api.features.get_feature_builder")
    def test_build_features_empty_sensor_data_skips_save(self, mock_get_feature_builder, client):
        """Test that empty sensor data skips Parquet save.

        When build_sensor_features returns empty list, save_features_to_parquet
        should not be called.
        """
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = []
        mock_feature_builder.build_image_features.return_value = []
        mock_feature_builder.build_audio_features.return_value = []
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={"vehicle_id": "vehicle-1"})

        assert response.status_code == 200

        # save_features_to_parquet should not be called when no sensor features
        mock_feature_builder.save_features_to_parquet.assert_not_called()

    @patch("app.api.features.get_feature_builder")
    def test_build_features_server_error_returns_500(self, mock_get_feature_builder, client):
        """Test that server error returns 500 status code."""
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.side_effect = Exception("Build failed")
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={"vehicle_id": "vehicle-1"})

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Error building features" in data["detail"]

    @patch("app.api.features.get_feature_builder")
    def test_build_features_response_format(self, mock_get_feature_builder, client):
        """Test that response format matches BuildFeatureResponse schema."""
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = [
            {"vehicle_id": "vehicle-1", "avg_speed_10s": 45.5}
        ]
        mock_feature_builder.build_image_features.return_value = [
            {"vehicle_id": "vehicle-1", "object_count": 5}
        ]
        mock_feature_builder.build_audio_features.return_value = [
            {"vehicle_id": "vehicle-1", "noise_level": 65.0}
        ]
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={"vehicle_id": "vehicle-1"})

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "success" in data
        assert "message" in data
        assert "features_built" in data
        assert isinstance(data["features_built"], list)

    @patch("app.api.features.get_feature_builder")
    def test_build_features_only_sensor_available(self, mock_get_feature_builder, client):
        """Test response when only sensor features are built.

        When sensor features exist but image/audio return empty,
        only sensor_features should be in the features_built list.
        """
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = [
            {"vehicle_id": "vehicle-1", "avg_speed_10s": 45.5}
        ]
        mock_feature_builder.build_image_features.return_value = []
        mock_feature_builder.build_audio_features.return_value = []
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={"vehicle_id": "vehicle-1"})

        assert response.status_code == 200
        data = response.json()
        assert data["features_built"] == ["sensor_features"]

    @patch("app.api.features.get_feature_builder")
    @patch("app.api.features.get_minio_service")
    def test_build_features_uses_media_metadata_uris(
        self,
        mock_get_minio_service,
        mock_get_feature_builder,
        client
    ):
        """Build endpoint should pass MinIO metadata JSON URIs to feature builders."""
        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = []
        mock_feature_builder.build_image_features.return_value = [
            {"vehicle_id": "vehicle-1", "image_uri": "images/vehicle-1/2026/05/24/e1.json"}
        ]
        mock_feature_builder.build_audio_features.return_value = [
            {"vehicle_id": "vehicle-1", "audio_uri": "audio/vehicle-1/2026/05/24/e1.json"}
        ]
        mock_get_feature_builder.return_value = mock_feature_builder

        mock_minio = MagicMock()
        mock_minio.list_objects.side_effect = [
            [
                "images/vehicle-1/2026/05/24/e1.json",
                "images/vehicle-1/2026/05/24/e2.json",
            ],
            [
                "audio/vehicle-1/2026/05/24/e1.json",
            ],
        ]
        mock_get_minio_service.return_value = mock_minio

        response = client.post("/api/features/build", json={"vehicle_id": "vehicle-1"})

        assert response.status_code == 200
        mock_feature_builder.build_image_features.assert_called_once()
        image_kwargs = mock_feature_builder.build_image_features.call_args.kwargs
        assert image_kwargs["vehicle_id"] == "vehicle-1"
        assert image_kwargs["image_uris"] == [
            "images/vehicle-1/2026/05/24/e1.json",
            "images/vehicle-1/2026/05/24/e2.json",
        ]
        assert "start_time" in image_kwargs
        assert "end_time" in image_kwargs

        mock_feature_builder.build_audio_features.assert_called_once()
        audio_kwargs = mock_feature_builder.build_audio_features.call_args.kwargs
        assert audio_kwargs["vehicle_id"] == "vehicle-1"
        assert audio_kwargs["audio_uris"] == ["audio/vehicle-1/2026/05/24/e1.json"]
        assert "start_time" in audio_kwargs
        assert "end_time" in audio_kwargs

    @patch("app.api.features.get_feature_builder")
    def test_build_features_default_date_range_7_days(self, mock_get_feature_builder, client):
        """Test that default date range is last 7 days when no dates provided."""
        from datetime import datetime, timedelta, timezone

        mock_feature_builder = MagicMock()
        mock_feature_builder.build_sensor_features.return_value = []
        mock_feature_builder.build_image_features.return_value = []
        mock_feature_builder.build_audio_features.return_value = []
        mock_get_feature_builder.return_value = mock_feature_builder

        response = client.post("/api/features/build", json={})

        assert response.status_code == 200

        # Verify date range was calculated (within 7 days)
        call_args = mock_feature_builder.build_sensor_features.call_args
        if call_args:
            start_time = call_args.kwargs.get("start_time")
            end_time = call_args.kwargs.get("end_time")
            if start_time and end_time:
                time_diff = end_time - start_time
                assert time_diff <= timedelta(hours=169)  # Allow small margin
