"""Tests for /api/events endpoints."""

from unittest.mock import MagicMock, patch

import pytest


class TestEventsAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as c:
            yield c

    @patch("app.api.events.get_kafka_producer")
    def test_simulate_event_uses_provided_timestamp(self, mock_get_kafka_producer, client):
        mock_producer = MagicMock()
        mock_producer.publish.return_value = True
        mock_get_kafka_producer.return_value = mock_producer

        response = client.post(
            "/api/events/simulate",
            json={
                "vehicle_id": "V001",
                "scenario": "normal",
                "timestamp": "2026-05-24T05:35:56.674Z",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["vehicle_id"] == "V001"
        assert payload["timestamp"] == "2026-05-24T05:35:56.674000+00:00"
        assert payload["payload"]["timestamp"] == "2026-05-24T05:35:56.674000+00:00"

    @patch("app.api.events.get_kafka_producer")
    def test_simulate_event_invalid_timestamp_returns_422(self, mock_get_kafka_producer, client):
        mock_get_kafka_producer.return_value = MagicMock()

        response = client.post(
            "/api/events/simulate",
            json={"vehicle_id": "V001", "timestamp": "not-a-time"},
        )

        assert response.status_code == 422
        assert "invalid iso datetime" in response.json()["detail"].lower()

    @patch("app.api.events.get_kafka_producer")
    def test_simulate_event_naive_timestamp_is_treated_as_utc(
        self, mock_get_kafka_producer, client
    ):
        mock_producer = MagicMock()
        mock_producer.publish.return_value = True
        mock_get_kafka_producer.return_value = mock_producer

        response = client.post(
            "/api/events/simulate",
            json={
                "vehicle_id": "V001",
                "scenario": "normal",
                "timestamp": "2026-05-24T05:35:56",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["timestamp"] == "2026-05-24T05:35:56+00:00"

    @patch("app.api.events.get_kafka_producer")
    def test_backfill_24h_generates_expected_event_count(self, mock_get_kafka_producer, client):
        mock_producer = MagicMock()
        mock_producer.publish.return_value = True
        mock_get_kafka_producer.return_value = mock_producer

        response = client.post(
            "/api/events/backfill-24h",
            json={
                "vehicle_ids": ["V001", "V002"],
                "interval_minutes": 720,
                "end_time": "2026-05-25T00:00:00Z",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        # 24h window with 12h step => 3 timestamps (start, +12h, end) * 2 vehicles
        assert payload["planned_events"] == 6
        assert payload["published_events"] == 6
        assert payload["failed_events"] == 0
        assert payload["success"] is True
        assert mock_producer.publish.call_count == 6

    @patch("app.api.events.get_kafka_producer")
    def test_backfill_24h_partial_failures_are_reported(self, mock_get_kafka_producer, client):
        mock_producer = MagicMock()
        publish_results = [True, False, True, False]
        mock_producer.publish.side_effect = publish_results
        mock_get_kafka_producer.return_value = mock_producer

        response = client.post(
            "/api/events/backfill-24h",
            json={
                "vehicle_ids": ["V001"],
                "interval_minutes": 1440,
                "end_time": "2026-05-25T00:00:00Z",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["planned_events"] == 2
        assert payload["published_events"] == 1
        assert payload["failed_events"] == 1
        assert payload["success"] is False
