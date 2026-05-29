"""Tests for /api/predict endpoint."""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.feature_registry import (
    get_prediction_fallback_defaults,
    get_prediction_feature_names,
)


class TestPredictAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as c:
            yield c

    @patch("app.api.predict.get_feast_service")
    @patch("app.api.predict.get_risk_model")
    def test_predict_uses_registry_defaults_when_online_features_missing(
        self, mock_get_risk_model, mock_get_feast_service, client
    ):
        mock_feast_service = MagicMock()
        mock_feast_service.get_online_features.return_value = None
        mock_get_feast_service.return_value = mock_feast_service

        mock_risk_model = MagicMock()
        mock_risk_model.predict.return_value = {
            "vehicle_id": "V001",
            "risk_score": 0.42,
            "risk_level": "MEDIUM",
        }
        mock_get_risk_model.return_value = mock_risk_model

        response = client.post("/api/predict", json={"vehicle_id": "V001"})

        assert response.status_code == 200
        payload = response.json()
        expected_features = get_prediction_fallback_defaults()

        assert payload["vehicle_id"] == "V001"
        assert payload["features"] == expected_features
        assert payload["risk_score"] == 0.42
        assert payload["risk_level"] == "MEDIUM"

        mock_feast_service.get_online_features.assert_called_once_with(vehicle_id="V001")
        mock_risk_model.predict.assert_called_once_with(
            vehicle_id="V001",
            features=expected_features,
        )

    @patch("app.api.predict.get_feast_service")
    @patch("app.api.predict.get_risk_model")
    def test_predict_merges_partial_online_features_with_registry_defaults(
        self, mock_get_risk_model, mock_get_feast_service, client
    ):
        mock_feast_service = MagicMock()
        mock_feast_service.get_online_features.return_value = {
            "avg_speed_10s": 55.0,
            "pedestrian_count": 2,
            "unused_feature": 999,
            "siren_detected": None,
        }
        mock_get_feast_service.return_value = mock_feast_service

        mock_risk_model = MagicMock()
        mock_risk_model.predict.return_value = {
            "vehicle_id": "V001",
            "risk_score": 0.77,
            "risk_level": "HIGH",
        }
        mock_get_risk_model.return_value = mock_risk_model

        response = client.post("/api/predict", json={"vehicle_id": "V001"})

        assert response.status_code == 200
        payload = response.json()
        expected_features = {
            "avg_speed_10s": 55.0,
            "obstacle_distance_min": 100.0,
            "sensor_missing_rate": 0.0,
            "pedestrian_count": 2,
            "siren_detected": False,
        }

        assert payload["features"] == expected_features
        assert set(payload["features"].keys()) == set(get_prediction_feature_names())
        assert "unused_feature" not in payload["features"]

        mock_risk_model.predict.assert_called_once_with(
            vehicle_id="V001",
            features=expected_features,
        )
