"""Tests for Feast Service."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.services.feast_service import FeastService, HistoricalFeatureLookupError
from app.services.feature_registry import get_feature_refs


class TestFeastService:
    """Test suite for FeastService."""

    @pytest.fixture(autouse=True)
    def _mock_view_loader(self, monkeypatch):
        def _load_view_entity_df(
            _self,
            vehicle_id,
            feature_view,
            start_time,
            end_time,
        ):
            return pd.DataFrame(
                [
                    {"vehicle_id": vehicle_id, "event_timestamp": start_time},
                    {"vehicle_id": vehicle_id, "event_timestamp": end_time},
                ]
            )

        monkeypatch.setattr(
            FeastService, "_load_view_entity_df", _load_view_entity_df
        )

    @patch("app.services.feast_service.FeatureStore")
    def test_service_initialization(self, mock_feature_store_class):
        """Test that service initializes correctly with repo path."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        repo_path = "./feast_repo"
        service = FeastService(repo_path=repo_path)

        assert service is not None
        assert service.repo_path == repo_path
        mock_feature_store_class.assert_called_once_with(repo_path=repo_path)

    @patch("app.services.feast_service.FeatureStore")
    def test_get_online_features_success(self, mock_feature_store_class):
        """Test that online feature retrieval returns features on success."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        # Mock the get_online_features response
        expected_features = {
            "vehicle_id": "vehicle-1",
            "avg_speed_10s": 45.5,
            "accel_std_10s": 2.3,
            "obstacle_distance_min": 15.0,
        }
        mock_feature_store.get_online_features.return_value = expected_features

        service = FeastService(repo_path="./feast_repo")
        features = service.get_online_features(
            vehicle_id="vehicle-1",
            features=["avg_speed_10s", "accel_std_10s", "obstacle_distance_min"],
        )

        assert features is not None
        assert features["vehicle_id"] == "vehicle-1"
        assert features["avg_speed_10s"] == 45.5
        mock_feature_store.get_online_features.assert_called_once()

    @patch("app.services.feast_service.FeatureStore")
    def test_get_online_features_with_default_features(self, mock_feature_store_class):
        """Test that online feature retrieval works with default feature list."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        expected_features = {"vehicle_id": "vehicle-1", "avg_speed_10s": 45.5}
        mock_feature_store.get_online_features.return_value = expected_features

        service = FeastService(repo_path="./feast_repo")
        features = service.get_online_features(vehicle_id="vehicle-1")

        assert features is not None
        # Verify default features were actually passed to Feast
        call_args = mock_feature_store.get_online_features.call_args
        passed_features = call_args.kwargs.get("features") or call_args[1].get("features")
        assert passed_features == get_feature_refs()

    @patch("app.services.feast_service.FeatureStore")
    def test_get_online_features_failure(self, mock_feature_store_class):
        """Test that online feature retrieval returns None on failure."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store
        mock_feature_store.get_online_features.side_effect = Exception(
            "Feature store connection failed"
        )

        service = FeastService(repo_path="./feast_repo")
        features = service.get_online_features(vehicle_id="vehicle-1")

        assert features is None

    @patch("app.services.feast_service.FeatureStore")
    def test_get_online_features_with_empty_list_values(self, mock_feature_store_class):
        """Test that online feature retrieval handles empty list values without index error.

        This test verifies the fix for: 'list index out of range' error
        when Feast returns empty lists for feature values.
        """
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        # Mock response with empty list values (simulating Feast ResultSet behavior)
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "vehicle_id": ["vehicle-1"],
            "avg_speed_10s": [],  # Empty list - this caused the index error
            "accel_std_10s": [2.3],
            "obstacle_distance_min": [],  # Empty list
        }
        mock_feature_store.get_online_features.return_value = mock_result

        service = FeastService(repo_path="./feast_repo")

        # Verify the method completes without raising IndexError
        # This is the critical assertion - the original bug caused an exception
        features = service.get_online_features(vehicle_id="vehicle-1")

        assert features is not None
        assert features["vehicle_id"] == "vehicle-1"
        assert features["avg_speed_10s"] is None  # Empty list should become None
        assert features["accel_std_10s"] == 2.3
        assert features["obstacle_distance_min"] is None  # Empty list should become None

    @patch("app.services.feast_service.FeatureStore")
    def test_get_online_features_converts_short_names_to_feature_refs(self, mock_feature_store_class):
        """Short feature names should be converted to Feast's feature ref format."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store
        mock_feature_store.get_online_features.return_value = {"avg_speed_10s": 45.5}

        service = FeastService(repo_path="./feast_repo")
        service.get_online_features(
            vehicle_id="vehicle-1",
            features=["avg_speed_10s", "sensor_features:accel_std_10s"],
        )

        call_args = mock_feature_store.get_online_features.call_args
        passed_features = call_args.kwargs.get("features") or call_args[1].get("features")
        assert passed_features == [
            "sensor_features:avg_speed_10s",
            "sensor_features:accel_std_10s",
        ]

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_returns_dataframe(self, mock_feature_store_class):
        """Test that historical feature retrieval properly handles DataFrame conversion.

        This test verifies the fix for: 'not enough values to unpack (expected 2, got 1)'
        error when processing Feast retrieval results.
        """
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        # Mock the retrieval result with proper to_df() chain
        mock_retrieval_result = MagicMock()
        mock_df = MagicMock()
        mock_reset_df = MagicMock()
        mock_retrieval_result.to_df.return_value = mock_df
        mock_df.reset_index.return_value = mock_reset_df
        mock_reset_df.to_dict.return_value = [
            {"vehicle_id": "V001", "avg_speed_10s": 45.5, "event_timestamp": "2026-05-23T10:00:00"},
            {"vehicle_id": "V001", "avg_speed_10s": 47.2, "event_timestamp": "2026-05-23T10:00:10"},
        ]
        mock_feature_store.get_historical_features.return_value = mock_retrieval_result

        service = FeastService(repo_path="./feast_repo")
        features = service.get_historical_features(
            vehicle_id="V001",
            feature_views=["sensor_features"],
        )

        assert features is not None
        assert len(features) == 2
        assert features[0]["vehicle_id"] == "V001"
        assert features[0]["avg_speed_10s"] == 45.5
        # Verify the proper call chain: get_historical_features().to_df().reset_index().to_dict()
        assert mock_feature_store.get_historical_features.call_count >= 1
        assert mock_retrieval_result.to_df.call_count >= 1
        mock_df.reset_index.assert_called_once_with(drop=True)

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_uses_correct_feature_refs_format(self, mock_feature_store_class):
        """Test that historical feature retrieval uses 'feature_view:feature' format.

        This verifies the fix for Feast API requiring feature refs in the format
        'feature_view:feature' (e.g., 'sensor_features:avg_speed_10s').
        """
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        # Mock the retrieval result
        mock_retrieval_result = MagicMock()
        mock_df = MagicMock()
        mock_retrieval_result.to_df.return_value = mock_df
        mock_df.to_dict.return_value = [
            {"sensor_features__avg_speed_10s": 45.5, "sensor_features__obstacle_distance_min": 15.0},
        ]
        mock_feature_store.get_historical_features.return_value = mock_retrieval_result

        service = FeastService(repo_path="./feast_repo")
        features = service.get_historical_features(
            vehicle_id="V001",
            feature_views=["sensor_features"],
        )

        # Verify get_historical_features was called with correct feature_refs format
        call_args = mock_feature_store.get_historical_features.call_args
        feature_refs = call_args.kwargs.get("features") or call_args[1].get("features")

        assert feature_refs is not None
        # Check that feature refs use the correct format
        # Note: vehicle_id is entity, event_timestamp is timestamp field - not features
        assert "sensor_features:avg_speed_10s" in feature_refs
        assert "sensor_features:obstacle_distance_min" in feature_refs
        assert "sensor_features:vehicle_id" not in feature_refs  # entity, not feature
        assert "sensor_features:event_timestamp" not in feature_refs  # timestamp, not feature
        assert "image_features:image_uri" not in feature_refs
        assert "audio_features:audio_uri" not in feature_refs

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_multiple_feature_views(self, mock_feature_store_class):
        """Test that multiple feature views are properly combined in feature refs."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        mock_retrieval_result = MagicMock()
        mock_df = MagicMock()
        mock_retrieval_result.to_df.return_value = mock_df
        mock_df.to_dict.return_value = []
        mock_feature_store.get_historical_features.return_value = mock_retrieval_result

        service = FeastService(repo_path="./feast_repo")
        service.get_historical_features(
            vehicle_id="V001",
            feature_views=["sensor_features", "image_features", "audio_features"],
        )

        call_args = mock_feature_store.get_historical_features.call_args
        feature_refs = call_args.kwargs.get("features") or call_args[1].get("features")

        # Verify all three feature views are included
        assert any("sensor_features:" in ref for ref in feature_refs)
        assert any("image_features:" in ref for ref in feature_refs)
        assert any("audio_features:" in ref for ref in feature_refs)

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_drops_all_null_rows_by_default(self, mock_feature_store_class):
        """Rows with all requested feature columns null should be dropped."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        mock_retrieval_result = MagicMock()
        mock_retrieval_result.to_df.return_value = pd.DataFrame(
            [
                {
                    "vehicle_id": "V001",
                    "event_timestamp": datetime(2026, 5, 23, 10, 0, tzinfo=timezone.utc),
                    "avg_speed_10s": None,
                    "accel_std_10s": None,
                    "obstacle_distance_min": None,
                    "lidar_point_count": None,
                    "sensor_missing_rate": None,
                },
                {
                    "vehicle_id": "V001",
                    "event_timestamp": datetime(2026, 5, 23, 10, 10, tzinfo=timezone.utc),
                    "avg_speed_10s": 42.5,
                    "accel_std_10s": 0.2,
                    "obstacle_distance_min": 10.0,
                    "lidar_point_count": 1200,
                    "sensor_missing_rate": 0.01,
                },
            ]
        )
        mock_feature_store.get_historical_features.return_value = mock_retrieval_result

        service = FeastService(repo_path="./feast_repo")
        rows = service.get_historical_features(
            vehicle_id="V001",
            feature_views=["sensor_features"],
        )

        assert len(rows) == 1
        assert rows[0]["avg_speed_10s"] == 42.5

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_keeps_all_null_rows_when_disabled(self, mock_feature_store_class):
        """Rows should be preserved when null-only filtering is disabled."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        mock_retrieval_result = MagicMock()
        mock_retrieval_result.to_df.return_value = pd.DataFrame(
            [
                {
                    "vehicle_id": "V001",
                    "event_timestamp": datetime(2026, 5, 23, 10, 0, tzinfo=timezone.utc),
                    "avg_speed_10s": None,
                    "accel_std_10s": None,
                    "obstacle_distance_min": None,
                    "lidar_point_count": None,
                    "sensor_missing_rate": None,
                }
            ]
        )
        mock_feature_store.get_historical_features.return_value = mock_retrieval_result

        service = FeastService(repo_path="./feast_repo")
        rows = service.get_historical_features(
            vehicle_id="V001",
            feature_views=["sensor_features"],
            drop_all_null_rows=False,
        )

        assert len(rows) == 1

    @patch("app.services.feast_service.FeatureStore")
    def test_materialize_incremental_with_times(self, mock_feature_store_class):
        """Test that materialization works with specific time range."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        end_time = datetime(2026, 5, 21, 0, 0, 0)
        expected_end_time = end_time.replace(tzinfo=timezone.utc)

        service = FeastService(repo_path="./feast_repo")
        result = service.materialize_incremental(end_date=end_time)

        assert result is True
        mock_feature_store.materialize_incremental.assert_called_once_with(
            end_date=expected_end_time
        )

    @patch("app.services.feast_service.FeatureStore")
    def test_materialize_persists_state_file(self, mock_feature_store_class, tmp_path):
        """Successful materialization should persist last end_date for status API."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        repo_path = tmp_path / "feast_repo"
        end_time = datetime(2026, 5, 24, 12, 0, 0, tzinfo=timezone.utc)

        service = FeastService(repo_path=str(repo_path))
        result = service.materialize_incremental(end_date=end_time)

        assert result is True
        state = service.get_materialization_state()
        assert state["last_materialization_end_date"] == end_time.isoformat()

    @patch("app.services.feast_service.FeatureStore")
    def test_get_materialization_state_when_file_missing(self, mock_feature_store_class, tmp_path):
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        repo_path = tmp_path / "feast_repo"
        service = FeastService(repo_path=str(repo_path))

        state = service.get_materialization_state()
        assert state["last_materialization_end_date"] is None

    @patch("app.services.feast_service.FeatureStore")
    def test_materialize_incremental_without_times(self, mock_feature_store_class):
        """Test that materialization works without time arguments."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        service = FeastService(repo_path="./feast_repo")
        result = service.materialize_incremental()

        assert result is True
        mock_feature_store.materialize_incremental.assert_called_once()

    @patch("app.services.feast_service.FeatureStore")
    def test_materialize_incremental_failure(self, mock_feature_store_class):
        """Test that materialization returns False on failure."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store
        mock_feature_store.materialize_incremental.side_effect = Exception(
            "Materialization failed"
        )

        service = FeastService(repo_path="./feast_repo")
        result = service.materialize_incremental()

        assert result is False

    @patch("app.services.feast_service.FeatureStore")
    def test_apply_success(self, mock_feature_store_class):
        """Test that apply returns True on success."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        service = FeastService(repo_path="./feast_repo")
        result = service.apply()

        assert result is True
        mock_feature_store.apply.assert_called_once()

    @patch("app.services.feast_service.FeatureStore")
    def test_apply_failure(self, mock_feature_store_class):
        """Test that apply returns False on failure."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store
        mock_feature_store.apply.side_effect = Exception("Apply failed")

        service = FeastService(repo_path="./feast_repo")
        result = service.apply()

        assert result is False

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_failure(self, mock_feature_store_class):
        """Test that historical feature retrieval raises on failure."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store
        mock_feature_store.get_historical_features.side_effect = Exception(
            "Feature store connection failed"
        )

        service = FeastService(repo_path="./feast_repo")
        with pytest.raises(HistoricalFeatureLookupError):
            service.get_historical_features(
                vehicle_id="V001",
                feature_views=["sensor_features"],
            )

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_with_start_time(self, mock_feature_store_class):
        """Test that historical feature retrieval uses start_time parameter.

        When start_time is provided, it should be used in the entity_df.
        """
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        mock_retrieval_result = MagicMock()
        mock_df = MagicMock()
        mock_retrieval_result.to_df.return_value = mock_df
        mock_df.to_dict.return_value = []
        mock_feature_store.get_historical_features.return_value = mock_retrieval_result

        service = FeastService(repo_path="./feast_repo")
        start_time = datetime(2026, 5, 20, 0, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2026, 5, 22, 0, 0, 0, tzinfo=timezone.utc)

        service.get_historical_features(
            vehicle_id="V001",
            feature_views=["sensor_features"],
            start_time=start_time,
            end_time=end_time,
        )

        # Verify entity_df contains a point-in-time row series from start to end.
        call_args = mock_feature_store.get_historical_features.call_args
        entity_df = call_args.kwargs.get("entity_df")

        assert entity_df is not None
        assert "event_timestamp" in entity_df.columns
        assert "event_timestamp_end" not in entity_df.columns
        assert len(entity_df) > 1
        assert entity_df["event_timestamp"].min() == start_time
        assert entity_df["event_timestamp"].max() == end_time

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_with_end_time_only(self, mock_feature_store_class):
        """Test that historical feature retrieval calculates start_time from end_time.

        When only end_time is provided, start_time should default to end_time - 7 days.
        """
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        mock_retrieval_result = MagicMock()
        mock_df = MagicMock()
        mock_retrieval_result.to_df.return_value = mock_df
        mock_df.to_dict.return_value = []
        mock_feature_store.get_historical_features.return_value = mock_retrieval_result

        service = FeastService(repo_path="./feast_repo")
        end_time = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)

        service.get_historical_features(
            vehicle_id="V001",
            end_time=end_time,
        )

        # Verify entity_df was generated for an interval series.
        call_args = mock_feature_store.get_historical_features.call_args
        entity_df = call_args.kwargs.get("entity_df")

        assert entity_df is not None
        assert len(entity_df) > 1

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_without_time_params_uses_defaults(self, mock_feature_store_class):
        """Test that historical feature retrieval uses default time range.

        When no time params provided, should use default lookback window.
        """
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        mock_retrieval_result = MagicMock()
        mock_df = MagicMock()
        mock_retrieval_result.to_df.return_value = mock_df
        mock_df.to_dict.return_value = []
        mock_feature_store.get_historical_features.return_value = mock_retrieval_result

        service = FeastService(repo_path="./feast_repo")

        service.get_historical_features(
            vehicle_id="V001",
        )

        # Verify entity_df was called with default time range series.
        call_args = mock_feature_store.get_historical_features.call_args
        entity_df = call_args.kwargs.get("entity_df")

        assert entity_df is not None
        assert len(entity_df) > 1

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_without_time_params_aligns_to_latest(self, mock_feature_store_class):
        """Default query should align window to latest non-null feature timestamp when available."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        main_result = MagicMock()
        main_result.to_df.return_value = pd.DataFrame(
            [
                {
                    "vehicle_id": "V001",
                    "event_timestamp": datetime(2026, 5, 24, 15, 0, 0, tzinfo=timezone.utc),
                    "avg_speed_10s": 42.0,
                    "accel_std_10s": 0.2,
                    "obstacle_distance_min": 8.0,
                    "lidar_point_count": 1000,
                    "sensor_missing_rate": 0.01,
                }
            ]
        )
        mock_feature_store.get_historical_features.return_value = main_result

        service = FeastService(repo_path="./feast_repo")
        with patch.object(
            service,
            "_find_latest_feature_timestamp",
            return_value=datetime(2026, 5, 24, 15, 0, 0, tzinfo=timezone.utc),
        ):
            service.get_historical_features(
                vehicle_id="V001",
                feature_views=["sensor_features"],
            )

        assert mock_feature_store.get_historical_features.call_count == 1
        main_call = mock_feature_store.get_historical_features.call_args
        entity_df = main_call.kwargs.get("entity_df")
        assert entity_df is not None
        assert entity_df["event_timestamp"].max() == datetime(2026, 5, 24, 15, 0, 0, tzinfo=timezone.utc)
        assert entity_df["event_timestamp"].min() == datetime(2026, 5, 23, 15, 0, 0, tzinfo=timezone.utc)

    @patch("app.services.feast_service.FeatureStore")
    def test_get_historical_features_time_range_multi_day(self, mock_feature_store_class):
        """Test that multi-day time range is handled correctly."""
        mock_feature_store = MagicMock()
        mock_feature_store_class.return_value = mock_feature_store

        mock_retrieval_result = MagicMock()
        mock_df = MagicMock()
        mock_reset_df = MagicMock()
        mock_retrieval_result.to_df.return_value = mock_df
        mock_df.reset_index.return_value = mock_reset_df
        mock_reset_df.to_dict.return_value = [
            {"vehicle_id": "V001", "avg_speed_10s": 45.5, "event_timestamp": "2026-05-20T10:00:00"},
            {"vehicle_id": "V001", "avg_speed_10s": 50.0, "event_timestamp": "2026-05-21T10:00:00"},
            {"vehicle_id": "V001", "avg_speed_10s": 55.0, "event_timestamp": "2026-05-22T10:00:00"},
        ]
        mock_feature_store.get_historical_features.return_value = mock_retrieval_result

        service = FeastService(repo_path="./feast_repo")
        start_time = datetime(2026, 5, 20, 0, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2026, 5, 22, 23, 59, 59, tzinfo=timezone.utc)

        features = service.get_historical_features(
            vehicle_id="V001",
            start_time=start_time,
            end_time=end_time,
        )

        assert len(features) == 3

    @patch("app.services.feast_service.FeatureStore")
    def test_build_entity_df_unions_multiple_views(self, mock_feature_store_class):
        mock_feature_store_class.return_value = MagicMock()
        service = FeastService(repo_path="./feast_repo")

        start_time = datetime(2026, 5, 24, 0, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2026, 5, 24, 23, 59, 59, tzinfo=timezone.utc)

        sensor_df = pd.DataFrame(
            [
                {"vehicle_id": "V001", "event_timestamp": datetime(2026, 5, 24, 10, 0, tzinfo=timezone.utc)},
                {"vehicle_id": "V001", "event_timestamp": datetime(2026, 5, 24, 11, 0, tzinfo=timezone.utc)},
            ]
        )
        image_df = pd.DataFrame(
            [
                {"vehicle_id": "V001", "event_timestamp": datetime(2026, 5, 24, 11, 0, tzinfo=timezone.utc)},
                {"vehicle_id": "V001", "event_timestamp": datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)},
            ]
        )

        with patch.object(service, "_load_view_entity_df", side_effect=[sensor_df, image_df]):
            entity_df = service._build_entity_df_from_feature_views(
                vehicle_id="V001",
                feature_views=["sensor_features", "image_features"],
                start_time=start_time,
                end_time=end_time,
                interval_minutes=60,
            )

        assert len(entity_df) == 3
        assert entity_df["event_timestamp"].tolist() == [
            datetime(2026, 5, 24, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 5, 24, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc),
        ]

    @patch("app.services.feast_service.FeatureStore")
    def test_build_entity_df_downsamples_when_exceeds_max_rows(self, mock_feature_store_class, monkeypatch):
        mock_feature_store_class.return_value = MagicMock()
        service = FeastService(repo_path="./feast_repo")
        monkeypatch.setattr("app.services.feast_service.MAX_ENTITY_ROWS", 3)

        start_time = datetime(2026, 5, 24, 10, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2026, 5, 24, 10, 3, 0, tzinfo=timezone.utc)
        raw_df = pd.DataFrame(
            [
                {"vehicle_id": "V001", "event_timestamp": datetime(2026, 5, 24, 10, 0, 10, tzinfo=timezone.utc)},
                {"vehicle_id": "V001", "event_timestamp": datetime(2026, 5, 24, 10, 0, 20, tzinfo=timezone.utc)},
                {"vehicle_id": "V001", "event_timestamp": datetime(2026, 5, 24, 10, 1, 10, tzinfo=timezone.utc)},
                {"vehicle_id": "V001", "event_timestamp": datetime(2026, 5, 24, 10, 2, 10, tzinfo=timezone.utc)},
                {"vehicle_id": "V001", "event_timestamp": datetime(2026, 5, 24, 10, 3, 10, tzinfo=timezone.utc)},
            ]
        )

        with patch.object(service, "_load_view_entity_df", return_value=raw_df):
            entity_df = service._build_entity_df_from_feature_views(
                vehicle_id="V001",
                feature_views=["sensor_features"],
                start_time=start_time,
                end_time=end_time,
                interval_minutes=1,
            )

        assert len(entity_df) == 4
        assert entity_df["event_timestamp"].tolist()[0] == datetime(
            2026, 5, 24, 10, 0, 20, tzinfo=timezone.utc
        )
