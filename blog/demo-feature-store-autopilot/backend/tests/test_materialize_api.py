"""Tests for /api/features/materialize endpoint."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.services.feature_registry import get_feature_view_names


class TestMaterializeAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as c:
            yield c

    @patch("app.api.features.get_feast_service")
    def test_materialize_uses_now_when_end_date_missing(self, mock_get_feast_service, client):
        mock_feast_service = MagicMock()
        mock_feast_service.materialize_incremental.return_value = True
        mock_get_feast_service.return_value = mock_feast_service

        response = client.post("/api/features/materialize", json={})

        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert payload["message"] == "Materialization completed successfully"
        assert payload["materialized_feature_views"] == get_feature_view_names()

        call_args = mock_feast_service.materialize_incremental.call_args
        passed_end_date = call_args.kwargs.get("end_date")
        assert passed_end_date is not None
        assert passed_end_date.tzinfo is not None

    @patch("app.api.features.get_feast_service")
    def test_materialize_parses_end_date_and_passes_utc(
        self, mock_get_feast_service, client
    ):
        mock_feast_service = MagicMock()
        mock_feast_service.materialize_incremental.return_value = True
        mock_get_feast_service.return_value = mock_feast_service

        response = client.post(
            "/api/features/materialize",
            json={"end_date": "2026-05-24T12:00:00Z"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["end_date"] == "2026-05-24T12:00:00Z"

        call_args = mock_feast_service.materialize_incremental.call_args
        passed_end_date = call_args.kwargs.get("end_date")
        assert passed_end_date == datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)

    @patch("app.api.features.get_feast_service")
    def test_materialize_invalid_end_date_returns_422(
        self, mock_get_feast_service, client
    ):
        mock_feast_service = MagicMock()
        mock_get_feast_service.return_value = mock_feast_service

        response = client.post(
            "/api/features/materialize",
            json={"end_date": "not-a-date"},
        )

        assert response.status_code == 422
        assert "invalid end_date" in response.json()["detail"].lower()
