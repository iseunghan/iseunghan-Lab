"""Tests for /api/features/training-dataset endpoint."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.services.feature_registry import get_training_feature_columns


class TestTrainingDatasetAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as c:
            yield c

    @patch("app.api.features.get_feast_service")
    def test_training_dataset_endpoint_uses_historical_features(
        self, mock_get_feast_service, client, tmp_path
    ):
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.side_effect = [
            [
                {
                    "vehicle_id": "V001",
                    "event_timestamp": datetime(
                        2026, 5, 20, 10, 0, tzinfo=timezone.utc
                    ),
                    "avg_speed_10s": 42.0,
                    "accel_std_10s": 1.2,
                    "obstacle_distance_min": 18.0,
                    "lidar_point_count": 1100,
                    "sensor_missing_rate": 0.01,
                    "object_count": 2,
                    "pedestrian_count": 1,
                    "lane_detect_score": 0.8,
                    "noise_level": 64.0,
                    "siren_detected": False,
                }
            ],
            [],
        ]
        mock_feast_service.get_online_features = MagicMock()
        mock_get_feast_service.return_value = mock_feast_service

        output_path = tmp_path / "training_dataset.csv"
        response = client.post(
            "/api/features/training-dataset",
            json={
                "output_path": str(output_path),
                "hours": 24,
                "interval_minutes": 60,
                "vehicle_ids": ["V001", "V002"],
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert payload["output_path"] == str(output_path)
        assert payload["row_count"] == 1
        assert payload["feature_count"] == len(get_training_feature_columns())
        assert set(payload["label_distribution"].keys()) <= {"LOW", "MEDIUM", "HIGH"}

        assert mock_feast_service.get_historical_features.call_count == 2
        mock_feast_service.get_online_features.assert_not_called()

        call_args = mock_feast_service.get_historical_features.call_args
        assert call_args.kwargs.get("start_time") is not None
        assert call_args.kwargs.get("end_time") is not None
        assert call_args.kwargs.get("interval_minutes") == 60

        df = pd.read_csv(output_path)
        assert "label_source" in df.columns
        assert set(df["label_source"]) == {"synthetic_rule_v1"}

    @patch("app.api.features.get_feast_service")
    def test_training_dataset_endpoint_returns_500_on_empty_historical(
        self, mock_get_feast_service, client
    ):
        mock_feast_service = MagicMock()
        mock_feast_service.get_historical_features.return_value = []
        mock_get_feast_service.return_value = mock_feast_service

        response = client.post(
            "/api/features/training-dataset",
            json={
                "output_path": "./data/training_dataset.csv",
                "hours": 24,
                "interval_minutes": 60,
                "vehicle_ids": ["V001"],
            },
        )

        assert response.status_code == 500
        assert "no historical features found" in response.json()["detail"].lower()
