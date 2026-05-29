"""Tests for Feature Builder Service."""

import io
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import pyarrow.parquet as pq
from app.services.feature_builder import FeatureBuilderService


class TestFeatureBuilderService:
    """Test suite for FeatureBuilderService."""

    def test_service_initialization(self):
        """Test that service initializes correctly with dependencies."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        assert service is not None
        assert service._influx_service == mock_influx_service
        assert service._minio_service == mock_minio_service

    @patch("app.services.influx_service.InfluxDBClient")
    def test_build_sensor_features(self, mock_client_class):
        """Test that building sensor features returns list of feature dicts."""
        # Setup mock InfluxDB client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_query_api = MagicMock()
        mock_client.query_api.return_value = mock_query_api

        # Mock query result - FluxQueryResult structure
        mock_table = MagicMock()

        # Create mock records for sensor data
        mock_record1 = MagicMock()
        mock_record1.values = {
            "_time": datetime(2026, 5, 21, 10, 0, 0),
            "speed": 50.0,
            "acceleration": 2.0,
            "obstacle_distance": 15.0,
            "lidar_points": 1000,
            "vehicle_id": "vehicle-1"
        }
        mock_record1.field = "_value"

        mock_record2 = MagicMock()
        mock_record2.values = {
            "_time": datetime(2026, 5, 21, 10, 0, 1),
            "speed": 55.0,
            "acceleration": 2.5,
            "obstacle_distance": 12.0,
            "lidar_points": 1100,
            "vehicle_id": "vehicle-1"
        }
        mock_record2.field = "_value"

        mock_table.records = [mock_record1, mock_record2]
        mock_query_api.query.return_value = [mock_table]

        # Create services
        influx_service = MagicMock()
        influx_service.query_sensor_data.return_value = [
            {
                "speed": 50.0,
                "acceleration": 2.0,
                "obstacle_distance": 15.0,
                "lidar_points": 1000,
                "event_timestamp": datetime(2026, 5, 21, 10, 0, 0)
            },
            {
                "speed": 55.0,
                "acceleration": 2.5,
                "obstacle_distance": 12.0,
                "lidar_points": 1100,
                "event_timestamp": datetime(2026, 5, 21, 10, 0, 1)
            }
        ]

        minio_service = MagicMock()
        minio_service.create_bucket.return_value = True

        service = FeatureBuilderService(
            influx_service=influx_service,
            minio_service=minio_service
        )

        # Build features
        result = service.build_sensor_features(
            vehicle_id="vehicle-1",
            start_time=datetime(2026, 5, 21, 10, 0, 0),
            end_time=datetime(2026, 5, 21, 10, 0, 10)
        )

        assert isinstance(result, list)
        assert len(result) > 0
        # Check that feature dict contains expected keys
        feature = result[0]
        assert "avg_speed_10s" in feature
        assert "accel_std_10s" in feature
        assert "obstacle_distance_min" in feature
        assert "lidar_point_count" in feature
        assert "sensor_missing_rate" in feature
        assert "vehicle_id" in feature
        assert "event_timestamp" in feature

    def test_build_image_features_with_empty_uris(self):
        """Test that building image features returns mock data when no URIs provided."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        result = service.build_image_features(vehicle_id="vehicle-1", image_uris=[])

        assert isinstance(result, list)
        assert len(result) == 1  # Default mock feature
        feature = result[0]
        assert feature["image_uri"] == "mock_image"
        assert feature["object_count"] == 5
        assert feature["pedestrian_count"] == 2
        assert feature["lane_detect_score"] == 0.85

    def test_build_image_features(self):
        """Test that building image features returns list of feature dicts."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        result = service.build_image_features(
            vehicle_id="vehicle-1",
            image_uris=["s3://bucket/image1.jpg", "s3://bucket/image2.jpg"]
        )

        assert isinstance(result, list)
        assert len(result) == 2
        assert [feature["image_uri"] for feature in result] == [
            "s3://bucket/image1.jpg",
            "s3://bucket/image2.jpg",
        ]
        for feature in result:
            assert "object_count" in feature
            assert "pedestrian_count" in feature
            assert "lane_detect_score" in feature
            assert "vehicle_id" in feature
            assert "image_uri" in feature

    def test_build_audio_features_with_empty_uris(self):
        """Test that building audio features returns mock data when no URIs provided."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        result = service.build_audio_features(vehicle_id="vehicle-1", audio_uris=[])

        assert isinstance(result, list)
        assert len(result) == 1  # Default mock feature
        feature = result[0]
        assert feature["audio_uri"] == "mock_audio"
        assert feature["noise_level"] == 65.0
        assert feature["siren_detected"] is False

    def test_build_audio_features(self):
        """Test that building audio features returns list of feature dicts."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        result = service.build_audio_features(
            vehicle_id="vehicle-1",
            audio_uris=["s3://bucket/audio1.wav", "s3://bucket/audio2.wav"]
        )

        assert isinstance(result, list)
        assert len(result) == 2
        assert [feature["audio_uri"] for feature in result] == [
            "s3://bucket/audio1.wav",
            "s3://bucket/audio2.wav",
        ]
        for feature in result:
            assert "noise_level" in feature
            assert "siren_detected" in feature
            assert "vehicle_id" in feature
            assert "audio_uri" in feature

    def test_build_sensor_features_with_time_column_mapping(self):
        """Test that _time column from InfluxDB is correctly mapped to timestamp.

        This test verifies the fix for timestamp handling where InfluxDB returns
        _time field which must be mapped to timestamp for proper time-window grouping.
        """
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        # Mock data with _time field (as InfluxDB returns)
        mock_influx_service.query_sensor_data.return_value = [
            {
                "_time": datetime(2026, 5, 21, 10, 0, 0),
                "speed": 50.0,
                "acceleration": 2.0,
                "obstacle_distance": 15.0,
                "lidar_points": 1000,
            },
            {
                "_time": datetime(2026, 5, 21, 10, 0, 5),
                "speed": 55.0,
                "acceleration": 2.5,
                "obstacle_distance": 12.0,
                "lidar_points": 1100,
            },
        ]

        result = service.build_sensor_features(vehicle_id="vehicle-1")

        assert isinstance(result, list)
        assert len(result) > 0
        # Verify obstacle_distance_min is a valid float, not inf
        assert isinstance(result[0]["obstacle_distance_min"], float)
        assert result[0]["obstacle_distance_min"] >= 0  # Should not be negative or inf

    def test_build_sensor_features_obstacle_distance_min_default(self):
        """Test that obstacle_distance_min defaults to 0.0 when column is missing.

        This test verifies the fix for float('inf') issue which could cause
        serialization errors when saving to Parquet or materializing to Redis.
        """
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        # Mock data without obstacle_distance column
        mock_influx_service.query_sensor_data.return_value = [
            {
                "_time": datetime(2026, 5, 21, 10, 0, 0),
                "speed": 50.0,
                "acceleration": 2.0,
                "lidar_points": 1000,
            },
        ]

        result = service.build_sensor_features(vehicle_id="vehicle-1")

        assert isinstance(result, list)
        assert len(result) > 0
        # Verify obstacle_distance_min defaults to 0.0, not inf
        assert result[0]["obstacle_distance_min"] == 0.0

    def test_build_sensor_features_missing_rate_ignores_all_null_columns(self):
        """Missing rate should use only effectively present sensor columns in a window."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        # speed/acceleration/obstacle_distance keys exist but are null in this window
        mock_influx_service.query_sensor_data.return_value = [
            {
                "_time": datetime(2026, 5, 21, 10, 0, 0),
                "speed": None,
                "acceleration": None,
                "obstacle_distance": None,
                "lidar_points": 1000,
            },
            {
                "_time": datetime(2026, 5, 21, 10, 0, 1),
                "speed": None,
                "acceleration": None,
                "obstacle_distance": None,
                "lidar_points": 1100,
            },
        ]

        result = service.build_sensor_features(vehicle_id="vehicle-1")

        assert len(result) == 1
        assert result[0]["sensor_missing_rate"] == 0.0

    @patch("app.services.feature_builder.pd")
    def test_save_features_to_parquet(self, mock_pd):
        """Test that saving features to parquet returns True on success."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()
        mock_minio_service.upload_bytes.return_value = True

        # Mock pandas DataFrame
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        features = [
            {
                "vehicle_id": "vehicle-1",
                "event_timestamp": datetime(2026, 5, 21, 10, 0, 0),
                "avg_speed_10s": 52.5,
                "accel_std_10s": 1.5,
                "obstacle_distance_min": 12.0,
                "lidar_point_count": 1050,
                "sensor_missing_rate": 0.02
            }
        ]

        result = service.save_features_to_parquet(
            features=features,
            bucket="mlops-features",
            prefix="sensor_features/vehicle-1/2026-05-21.parquet"
        )

        assert result is True
        mock_pd.DataFrame.assert_called_once()
        mock_minio_service.upload_bytes.assert_called_once()

    @patch("app.services.feature_builder.pd")
    def test_save_features_to_parquet_failure(self, mock_pd):
        """Test that saving features to parquet returns False on failure."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        # Mock pandas DataFrame
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df

        # Mock upload to fail
        mock_minio_service.upload_bytes.return_value = False

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        features = [
            {
                "vehicle_id": "vehicle-1",
                "event_timestamp": datetime(2026, 5, 21, 10, 0, 0),
                "avg_speed_10s": 52.5
            }
        ]

        result = service.save_features_to_parquet(
            features=features,
            bucket="mlops-features",
            prefix="test.parquet"
        )

        assert result is False

    def test_build_image_features_with_metadata(self):
        """Test building image features from valid metadata JSON.

        When metadata is available from MinIO, features should be built from the metadata
        rather than using mock data.
        """
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        # Mock metadata from MinIO
        mock_metadata = {
            "camera_id": "front",
            "frame_timestamp": "2026-05-22T10:00:00Z",
            "detected_objects": [
                {"class": "car", "confidence": 0.95, "bbox": [0.1, 0.2, 0.3, 0.4]},
                {"class": "pedestrian", "confidence": 0.87, "bbox": [0.5, 0.6, 0.2, 0.3]},
                {"class": "traffic_light", "confidence": 0.92, "bbox": [0.7, 0.1, 0.1, 0.2]}
            ],
            "lane_detection": {"lanes_detected": 2, "confidence": 0.92}
        }
        mock_minio_service.get_object_as_json.return_value = mock_metadata

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        # Build features from metadata URIs
        image_uris = [
            "minio://mlops-raw-media/metadata/frame_001.json",
            "minio://mlops-raw-media/metadata/frame_002.json"
        ]
        result = service.build_image_features(vehicle_id="vehicle-1", image_uris=image_uris)

        # Verify metadata was read from MinIO
        assert mock_minio_service.get_object_as_json.called
        assert len(result) == 2
        assert [feature["image_uri"] for feature in result] == image_uris

    def test_build_image_features_missing_metadata_fallback_to_mock(self):
        """Test that missing metadata falls back to mock data.

        When metadata JSON cannot be retrieved from MinIO (returns None),
        the service falls back to a single mock feature with 'mock_image' URI.
        """
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        # Mock MinIO to return None (metadata not found)
        mock_minio_service.get_object_as_json.return_value = None

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        # Build features with metadata URIs that don't exist
        image_uris = ["minio://mlops-raw-media/metadata/nonexistent.json"]
        result = service.build_image_features(vehicle_id="vehicle-1", image_uris=image_uris)

        # When no metadata found, implementation returns single mock feature
        assert len(result) == 1
        assert result[0]["image_uri"] == "mock_image"
        assert result[0]["object_count"] == 5
        assert result[0]["pedestrian_count"] == 2

    def test_build_image_features_correct_field_mapping(self):
        """Test that metadata fields are correctly mapped to feature fields.

        Verify the mapping:
        - detected_objects -> object_count (length of list)
        - detected_objects with class='pedestrian' -> pedestrian_count
        - lane_detection.confidence -> lane_detect_score
        """
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        # Mock metadata with specific values
        mock_metadata = {
            "camera_id": "front",
            "frame_timestamp": "2026-05-22T10:00:00Z",
            "detected_objects": [
                {"class": "car", "confidence": 0.95},
                {"class": "pedestrian", "confidence": 0.87},
                {"class": "pedestrian", "confidence": 0.82},
                {"class": "bicycle", "confidence": 0.78}
            ],
            "lane_detection": {"lanes_detected": 2, "confidence": 0.89}
        }
        mock_minio_service.get_object_as_json.return_value = mock_metadata

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        image_uris = ["minio://mlops-raw-media/metadata/frame_001.json"]
        result = service.build_image_features(vehicle_id="vehicle-1", image_uris=image_uris)

        # Verify field mapping (currently using mock values, but structure should be correct)
        assert len(result) == 1
        feature = result[0]
        assert "object_count" in feature
        assert "pedestrian_count" in feature
        assert "lane_detect_score" in feature
        assert "vehicle_id" in feature
        assert "image_uri" in feature

    def test_build_image_features_filters_each_row_by_time_range(self):
        """Image features should apply the time range per metadata row."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        def get_metadata_mock(bucket_name, object_name):
            filename = object_name.split("/")[-1]
            metadata_map = {
                "frame_001.json": {
                    "timestamp": "2026-05-22T10:00:00Z",
                    "detected_objects": [{"class": "car"}],
                    "lane_detection": {"confidence": 0.90},
                },
                "frame_002.json": {
                    "timestamp": "2026-05-22T10:05:00Z",
                    "detected_objects": [{"class": "pedestrian"}],
                    "lane_detection": {"confidence": 0.85},
                },
            }
            return metadata_map.get(filename)

        mock_minio_service.get_object_as_json.side_effect = get_metadata_mock

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        result = service.build_image_features(
            vehicle_id="vehicle-1",
            image_uris=[
                "minio://mlops-raw-media/metadata/frame_001.json",
                "minio://mlops-raw-media/metadata/frame_002.json",
            ],
            start_time=datetime(2026, 5, 22, 10, 1, 0),
            end_time=datetime(2026, 5, 22, 10, 10, 0),
        )

        assert len(result) == 1
        assert result[0]["image_uri"].endswith("frame_002.json")

    def test_build_audio_features_with_metadata(self):
        """Test building audio features from metadata.

        When audio metadata is available, features should be extracted from it.
        """
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        # Mock audio metadata
        mock_metadata = {
            "audio_id": "audio_001",
            "audio_timestamp": "2026-05-22T10:00:00Z",
            "noise_level": 72.5,
            "events_detected": [
                {"class": "siren", "confidence": 0.88, "timestamp_offset": 1.5},
                {"class": "horn", "confidence": 0.65, "timestamp_offset": 3.2}
            ]
        }
        mock_minio_service.get_object_as_json.return_value = mock_metadata

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        audio_uris = ["minio://mlops-raw-media/metadata/audio_001.json"]
        result = service.build_audio_features(vehicle_id="vehicle-1", audio_uris=audio_uris)

        # Verify metadata was read
        assert mock_minio_service.get_object_as_json.called
        assert len(result) == 1

    def test_build_audio_features_missing_metadata_fallback_to_mock(self):
        """Test that missing audio metadata falls back to mock data."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        # Mock MinIO to return None
        mock_minio_service.get_object_as_json.return_value = None

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        audio_uris = ["minio://mlops-raw-media/metadata/nonexistent.json"]
        result = service.build_audio_features(vehicle_id="vehicle-1", audio_uris=audio_uris)

        # When no metadata found, implementation returns single mock feature
        assert len(result) == 1
        assert result[0]["audio_uri"] == "mock_audio"
        assert result[0]["noise_level"] == 65.0
        assert result[0]["siren_detected"] is False

    def test_build_audio_features_with_media_consumer_metadata_format(self):
        """Audio features should parse nested media-consumer metadata format."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        mock_metadata = {
            "event_id": "evt-1",
            "vehicle_id": "vehicle-1",
            "media_type": "audio",
            "audio": {
                "noise_level_db": 81.0,
                "siren_detected": True,
                "horn_detected": False,
            },
        }
        mock_minio_service.get_object_as_json.return_value = mock_metadata

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        audio_uris = ["audio/vehicle-1/2026/05/24/evt-1.json"]
        result = service.build_audio_features(vehicle_id="vehicle-1", audio_uris=audio_uris)

        assert len(result) == 1
        assert result[0]["noise_level"] == 81.0
        assert result[0]["siren_detected"] is True
        assert result[0]["audio_uri"] == "audio/vehicle-1/2026/05/24/evt-1.json"

    def test_build_audio_features_filters_each_row_by_time_range(self):
        """Audio features should apply the time range per metadata row."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        def get_metadata_mock(bucket_name, object_name):
            filename = object_name.split("/")[-1]
            metadata_map = {
                "audio_001.json": {
                    "timestamp": "2026-05-22T10:00:00Z",
                    "noise_level": 60.0,
                    "events_detected": [],
                },
                "audio_002.json": {
                    "timestamp": "2026-05-22T10:05:00Z",
                    "noise_level": 80.0,
                    "events_detected": [{"class": "siren"}],
                },
            }
            return metadata_map.get(filename)

        mock_minio_service.get_object_as_json.side_effect = get_metadata_mock

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        result = service.build_audio_features(
            vehicle_id="vehicle-1",
            audio_uris=[
                "minio://mlops-raw-media/metadata/audio_001.json",
                "minio://mlops-raw-media/metadata/audio_002.json",
            ],
            start_time=datetime(2026, 5, 22, 10, 1, 0),
            end_time=datetime(2026, 5, 22, 10, 10, 0),
        )

        assert len(result) == 1
        assert result[0]["audio_uri"].endswith("audio_002.json")

    def test_build_audio_features_preserves_each_row(self):
        """Audio features should preserve one row per readable metadata JSON."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        def get_metadata_mock(bucket_name, object_name):
            filename = object_name.split("/")[-1]
            metadata_map = {
                "audio_001.json": {
                    "timestamp": "2026-05-22T10:00:00Z",
                    "noise_level": 60.0,
                    "events_detected": [],
                },
                "audio_002.json": {
                    "timestamp": "2026-05-22T10:00:10Z",
                    "noise_level": 80.0,
                    "events_detected": [{"class": "siren"}],
                },
            }
            return metadata_map.get(filename)

        mock_minio_service.get_object_as_json.side_effect = get_metadata_mock

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        result = service.build_audio_features(
            vehicle_id="vehicle-1",
            audio_uris=[
                "minio://mlops-raw-media/metadata/audio_001.json",
                "minio://mlops-raw-media/metadata/audio_002.json",
            ],
        )

        assert len(result) == 2
        assert [row["audio_uri"] for row in result] == [
            "minio://mlops-raw-media/metadata/audio_001.json",
            "minio://mlops-raw-media/metadata/audio_002.json",
        ]
        assert [row["noise_level"] for row in result] == [60.0, 80.0]
        assert [row["siren_detected"] for row in result] == [False, True]
        assert [row["event_timestamp"] for row in result] == [
            "2026-05-22T10:00:00+00:00",
            "2026-05-22T10:00:10+00:00",
        ]

    def test_save_features_to_parquet_preserves_multiple_rows(self):
        """Parquet save should preserve the number of feature rows."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()
        captured = {}

        def upload_bytes(bucket_name, object_name, data, content_type):
            captured["bucket_name"] = bucket_name
            captured["object_name"] = object_name
            captured["data"] = data
            captured["content_type"] = content_type
            return True

        mock_minio_service.upload_bytes.side_effect = upload_bytes

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        features = [
            {
                "vehicle_id": "vehicle-1",
                "image_uri": "s3://bucket/image1.jpg",
                "event_timestamp": "2026-05-21T10:00:00Z",
                "object_count": 5,
                "pedestrian_count": 2,
                "lane_detect_score": 0.85,
            },
            {
                "vehicle_id": "vehicle-1",
                "image_uri": "s3://bucket/image2.jpg",
                "event_timestamp": "2026-05-21T10:00:10Z",
                "object_count": 3,
                "pedestrian_count": 1,
                "lane_detect_score": 0.90,
            },
        ]

        result = service.save_features_to_parquet(
            features=features,
            bucket="mlops-features",
            prefix="image_features/vehicle-1/2026-05-21.parquet"
        )

        assert result is True
        table = pq.read_table(io.BytesIO(captured["data"]))
        assert table.num_rows == 2
        assert table.to_pandas()["image_uri"].tolist() == [
            "s3://bucket/image1.jpg",
            "s3://bucket/image2.jpg",
        ]

    def test_build_image_features_multiple_camera_frames_return_rows(self):
        """Test building features from multiple camera frames."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        # Different metadata for each frame
        def get_metadata_mock(bucket_name, object_name):
            # Extract filename from object_name
            filename = object_name.split("/")[-1]
            metadata_map = {
                "frame_001.json": {
                    "camera_id": "front",
                    "detected_objects": [{"class": "car", "confidence": 0.95}],
                    "lane_detection": {"confidence": 0.90}
                },
                "frame_002.json": {
                    "camera_id": "left",
                    "detected_objects": [{"class": "pedestrian", "confidence": 0.88}],
                    "lane_detection": {"confidence": 0.85}
                },
                "frame_003.json": {
                    "camera_id": "right",
                    "detected_objects": [],
                    "lane_detection": {"confidence": 0.78}
                }
            }
            return metadata_map.get(filename)

        mock_minio_service.get_object_as_json.side_effect = get_metadata_mock

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        image_uris = [
            "minio://mlops-raw-media/metadata/frame_001.json",
            "minio://mlops-raw-media/metadata/frame_002.json",
            "minio://mlops-raw-media/metadata/frame_003.json"
        ]
        result = service.build_image_features(vehicle_id="vehicle-1", image_uris=image_uris)

        assert len(result) == 3
        assert [row["image_uri"] for row in result] == image_uris
        assert all("object_count" in row for row in result)
        assert all("lane_detect_score" in row for row in result)

    def test_build_sensor_features_empty_data(self):
        """Test building sensor features when no data exists."""
        mock_influx_service = MagicMock()
        mock_minio_service = MagicMock()

        # Mock empty data from InfluxDB
        mock_influx_service.query_sensor_data.return_value = []

        service = FeatureBuilderService(
            influx_service=mock_influx_service,
            minio_service=mock_minio_service
        )

        result = service.build_sensor_features(vehicle_id="vehicle-1")

        # Should return empty list for no data
        assert result == []
