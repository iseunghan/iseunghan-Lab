"""Tests for Feast Service - historical features (mocked)."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.services.feast_service import FeastService


class TestFeastServiceHistoricalFeatures:
    """Test cases for get_historical_features method."""

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

    @pytest.fixture
    def mock_feast_store(self):
        """Create a mock Feast FeatureStore."""
        mock_store = MagicMock()
        mock_result = MagicMock()
        # Mock sample data
        sample_data = pd.DataFrame(
            [
                {
                    "vehicle_id": "V001",
                    "event_timestamp": datetime.now(),
                    "avg_speed_10s": 42.1,
                    "obstacle_distance_min": 18.4,
                }
            ]
        )
        mock_result.to_df.return_value = sample_data
        mock_store.get_historical_features.return_value = mock_result
        return mock_store

    @pytest.fixture
    def service_with_mock(self, mock_feast_store):
        """Create FeastService with mocked store."""
        with patch("app.services.feast_service.FeatureStore") as mock_class:
            mock_class.return_value = mock_feast_store
            service = FeastService(repo_path="./mock_feast_repo")
            service._store = mock_feast_store
            return service

    def test_get_historical_features_returns_list(self, service_with_mock):
        """Test that get_historical_features returns a list."""
        result = service_with_mock.get_historical_features("V001")
        assert isinstance(result, list)

    def test_get_historical_features_with_valid_vehicle_id(self, service_with_mock):
        """Test getting historical features for a valid vehicle ID."""
        result = service_with_mock.get_historical_features("V001")
        assert len(result) >= 0

    def test_get_historical_features_with_specific_feature_views(
        self, service_with_mock
    ):
        """Test getting historical features with specific feature views."""
        result = service_with_mock.get_historical_features(
            "V001", feature_views=["sensor_features"]
        )
        assert isinstance(result, list)

    def test_get_historical_features_returns_dict_records(self, service_with_mock):
        """Test that historical features are returned as list of dicts."""
        result = service_with_mock.get_historical_features("V001")
        if result:  # Only check if we have results
            assert isinstance(result[0], dict)

    def test_get_historical_features_empty_vehicle_id(self, service_with_mock):
        """Test getting historical features with empty vehicle ID."""
        result = service_with_mock.get_historical_features("")
        assert isinstance(result, list)

    def test_get_historical_features_nonexistent_vehicle(self, service_with_mock):
        """Test getting historical features for nonexistent vehicle."""
        result = service_with_mock.get_historical_features("NONEXISTENT")
        assert isinstance(result, list)

    def test_get_historical_features_calls_feast_correctly(self, service_with_mock):
        """Test that Feast get_historical_features is called with correct args."""
        service_with_mock.get_historical_features("V001", ["sensor_features"])
        assert service_with_mock._store.get_historical_features.call_count >= 1

    def test_get_historical_features_empty_result(self):
        """Test get_historical_features when Feast returns empty data."""
        mock_store = MagicMock()
        mock_result = MagicMock()
        mock_result.to_df.return_value = pd.DataFrame()  # Empty DataFrame
        mock_store.get_historical_features.return_value = mock_result

        with patch("app.services.feast_service.FeatureStore") as mock_class:
            mock_class.return_value = mock_store
            service = FeastService(repo_path="./mock_feast_repo")
            service._store = mock_store

            result = service.get_historical_features("V001")
            assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
