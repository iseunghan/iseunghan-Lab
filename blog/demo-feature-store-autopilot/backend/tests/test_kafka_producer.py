"""Tests for Kafka Producer Service."""

import pytest
from unittest.mock import MagicMock, patch
from app.services.kafka_producer import KafkaProducerService


class TestKafkaProducerService:
    """Test suite for KafkaProducerService."""

    @patch("app.services.kafka_producer.KafkaProducer")
    def test_producer_initialization(self, mock_producer_class):
        """Test that producer initializes correctly with broker address."""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer

        broker = "localhost:9092"
        producer = KafkaProducerService(broker=broker)

        assert producer is not None
        assert producer.broker == broker
        mock_producer_class.assert_called_once()

    @patch("app.services.kafka_producer.KafkaProducer")
    def test_message_publish_success(self, mock_producer_class):
        """Test that message publishing returns True on success."""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer

        producer_service = KafkaProducerService(broker="localhost:9092")
        message = {"event_type": "vehicle_movement", "speed": 50}
        topic = "vehicle-events"

        result = producer_service.publish(topic=topic, message=message, key="vehicle-1")

        assert result is True
        mock_producer.send.assert_called_once()

    @patch("app.services.kafka_producer.KafkaProducer")
    def test_message_publish_without_key(self, mock_producer_class):
        """Test that message publishing works without key."""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer

        producer_service = KafkaProducerService(broker="localhost:9092")
        message = {"event_type": "sensor_data", "value": 123}
        topic = "sensor-data"

        result = producer_service.publish(topic=topic, message=message)

        assert result is True

    @patch("app.services.kafka_producer.KafkaProducer")
    def test_message_publish_failure(self, mock_producer_class):
        """Test that message publishing returns False on failure."""
        mock_producer = MagicMock()
        mock_producer.send.side_effect = Exception("Kafka connection failed")
        mock_producer_class.return_value = mock_producer

        producer_service = KafkaProducerService(broker="localhost:9092")
        message = {"event_type": "error_event"}
        topic = "vehicle-events"

        result = producer_service.publish(topic=topic, message=message)

        assert result is False

    @patch("app.services.kafka_producer.KafkaProducer")
    def test_flush(self, mock_producer_class):
        """Test that flush method calls producer.flush()."""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer

        producer_service = KafkaProducerService(broker="localhost:9092")
        producer_service.flush()

        mock_producer.flush.assert_called_once()

    @patch("app.services.kafka_producer.KafkaProducer")
    def test_close(self, mock_producer_class):
        """Test that close method calls producer.close()."""
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer

        producer_service = KafkaProducerService(broker="localhost:9092")
        producer_service.close()

        mock_producer.close.assert_called_once()
