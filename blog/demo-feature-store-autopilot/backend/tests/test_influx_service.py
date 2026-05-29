"""Tests for InfluxDB Service."""

import pytest
from unittest.mock import MagicMock, patch
from app.services.influx_service import InfluxService


class TestInfluxService:
    """Test suite for InfluxService."""

    @patch("app.services.influx_service.InfluxDBClient")
    def test_service_initialization(self, mock_client_class):
        """Test that service initializes correctly with connection params."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        url = "http://localhost:8086"
        token = "test-token"
        org = "test-org"
        bucket = "test-bucket"

        service = InfluxService(url=url, token=token, org=org, bucket=bucket)

        assert service is not None
        assert service.url == url
        assert service.token == token
        assert service.org == org
        assert service.bucket == bucket
        mock_client_class.assert_called_once()

    @patch("app.services.influx_service.InfluxDBClient")
    def test_write_sensor_data_success(self, mock_client_class):
        """Test that writing sensor data returns True on success."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        service = InfluxService(url="http://localhost:8086", token="token", org="org")

        measurement = "vehicle-sensors"
        data = {
            "speed": 50.5,
            "acceleration": 2.3,
            "obstacle_distance": 15.0
        }
        tags = {"vehicle_id": "vehicle-1"}

        result = service.write_sensor_data(measurement=measurement, data=data, tags=tags)

        assert result is True

    @patch("app.services.influx_service.InfluxDBClient")
    def test_write_sensor_data_failure(self, mock_client_class):
        """Test that writing sensor data returns False on failure."""
        mock_client = MagicMock()
        mock_write_api = MagicMock()
        mock_write_api.write.side_effect = Exception("Connection failed")
        mock_client.write_api.return_value = mock_write_api
        mock_client_class.return_value = mock_client

        service = InfluxService(url="http://localhost:8086", token="token", org="org")

        result = service.write_sensor_data(measurement="test", data={"value": 1})

        assert result is False

    @patch("app.services.influx_service.InfluxDBClient")
    def test_query_sensor_data(self, mock_client_class):
        """Test that querying sensor data returns list of records."""
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_client.query_api.return_value = mock_query_api

        # Mock the query result - FluxQueryResult structure
        mock_table = MagicMock()
        mock_table.records = []
        mock_table.result = "test_result"

        # Mock record with proper structure
        mock_record = MagicMock()
        mock_record.values = {"speed": 50.0, "acceleration": 2.0, "vehicle_id": "vehicle-1"}
        mock_record.field = "_value"
        mock_table.records.append(mock_record)

        mock_query_api.query.return_value = [mock_table]
        mock_client_class.return_value = mock_client

        service = InfluxService(url="http://localhost:8086", token="token", org="org")

        result = service.query_sensor_data(vehicle_id="vehicle-1", limit=100)

        assert isinstance(result, list)
        assert len(result) >= 1

    @patch("app.services.influx_service.InfluxDBClient")
    def test_get_sensor_count(self, mock_client_class):
        """Test that getting sensor count returns integer."""
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_client.query_api.return_value = mock_query_api

        # Mock the count query result
        mock_table = MagicMock()
        mock_record = MagicMock()
        mock_record.value = 42
        mock_table.records = [mock_record]
        mock_query_api.query.return_value = [mock_table]

        mock_client_class.return_value = mock_client

        service = InfluxService(url="http://localhost:8086", token="token", org="org")

        result = service.get_sensor_count()

        assert isinstance(result, int)
        assert result == 42

    @patch("app.services.influx_service.InfluxDBClient")
    def test_close(self, mock_client_class):
        """Test that close method closes the client."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        service = InfluxService(url="http://localhost:8086", token="token", org="org")
        service.close()

        mock_client.close.assert_called_once()
