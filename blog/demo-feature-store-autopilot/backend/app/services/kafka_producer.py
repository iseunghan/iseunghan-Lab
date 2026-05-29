"""Kafka Producer Service for publishing events to Kafka topics."""

import json
import logging
from typing import Dict, Optional

from kafka import KafkaProducer

logger = logging.getLogger(__name__)


class KafkaProducerService:
    """Service for publishing messages to Kafka topics."""

    def __init__(self, broker: str):
        """Initialize Kafka producer.

        Args:
            broker: Kafka broker address (e.g., "localhost:9092")
        """
        self.broker = broker
        self._producer = KafkaProducer(
            bootstrap_servers=[broker],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks=1,
            retries=3,
        )

    def publish(self, topic: str, message: Dict, key: Optional[str] = None) -> bool:
        """Publish a message to a Kafka topic.

        Args:
            topic: Kafka topic name
            message: Message dictionary to publish
            key: Optional partition key for message routing

        Returns:
            True if message was queued successfully, False otherwise
        """
        try:
            if key:
                future = self._producer.send(
                    topic, value=message, key=key.encode("utf-8")
                )
            else:
                future = self._producer.send(topic, value=message)

            # Wait for message to be sent (non-blocking, but wait for confirmation)
            future.get(timeout=10)
            logger.info(f"Message published to topic '{topic}' with key '{key}'")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message to topic '{topic}': {e}")
            return False

    def flush(self):
        """Flush pending messages to Kafka."""
        self._producer.flush()
        logger.info("Kafka producer flushed")

    def close(self):
        """Close the Kafka producer."""
        self._producer.close()
        logger.info("Kafka producer closed")
