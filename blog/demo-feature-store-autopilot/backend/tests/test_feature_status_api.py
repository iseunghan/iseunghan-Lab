"""Tests for /api/features/status endpoint."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest


class TestFeatureStatusAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as c:
            yield c

    @patch("app.api.features.get_feast_service")
    def test_status_returns_materialization_and_freshness(
        self, mock_get_feast_service, client
    ):
        now = datetime.now(timezone.utc)
        latest_ts = now - timedelta(minutes=5)

        mock_feast_service = MagicMock()
        mock_feast_service.get_materialization_state.return_value = {
            "last_materialization_end_date": "2026-05-24T12:00:00Z"
        }
        mock_feast_service.get_historical_features.return_value = [
            {"vehicle_id": "V001", "event_timestamp": latest_ts.isoformat()}
        ]
        mock_feast_service.get_online_features.return_value = {
            "avg_speed_10s": 42.0,
            "siren_detected": False,
        }
        mock_get_feast_service.return_value = mock_feast_service

        response = client.get("/api/features/status?vehicle_id=V001&lookback_hours=24")

        assert response.status_code == 200
        payload = response.json()
        assert payload["vehicle_id"] == "V001"
        assert payload["lookback_hours"] == 24
        assert payload["last_materialization_end_date"] == "2026-05-24T12:00:00Z"
        assert payload["offline_latest_feature_timestamp"] is not None
        assert payload["offline_feature_age_seconds"] is not None
        assert payload["offline_feature_age_seconds"] >= 0
        assert payload["online_feature_available"] is True

    @patch("app.api.features.get_feast_service")
    def test_status_handles_empty_historical_and_online(
        self, mock_get_feast_service, client
    ):
        mock_feast_service = MagicMock()
        mock_feast_service.get_materialization_state.return_value = {
            "last_materialization_end_date": None
        }
        mock_feast_service.get_historical_features.return_value = []
        mock_feast_service.get_online_features.return_value = {}
        mock_get_feast_service.return_value = mock_feast_service

        response = client.get("/api/features/status?vehicle_id=V001")

        assert response.status_code == 200
        payload = response.json()
        assert payload["last_materialization_end_date"] is None
        assert payload["offline_latest_feature_timestamp"] is None
        assert payload["offline_feature_age_seconds"] is None
        assert payload["online_feature_available"] is False

