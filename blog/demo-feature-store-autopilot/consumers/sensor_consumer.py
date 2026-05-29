"""
Kafka Consumer for Vehicle Sensor Data

Consumes vehicle events from Kafka and stores sensor data in InfluxDB.
"""

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone

from confluent_kafka import Consumer, KafkaError, KafkaException
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import dotenv


# Load environment variables
dotenv.load_dotenv()

# Configuration
KAFKA_BROKER = os.getenv("KAFKA_HOST", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "vehicle-events")
KAFKA_GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP", "sensor-consumer-group")

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "influx-admin-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "mlops")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "features")

# Shutdown flag
shutdown_event = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_event
    print(f"\nReceived signal {signum}, shutting down...")
    shutdown_event = True
    sys.exit(0)


def create_kafka_consumer():
    """Create and configure Kafka consumer."""
    conf = {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": KAFKA_GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 5000,
    }
    return Consumer(conf)


def create_influxdb_client():
    """Create InfluxDB client."""
    return InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG,
    )


def write_sensor_data_to_influxdb(influx_client, sensor_data: dict, vehicle_id: str, timestamp: str):
    """Write sensor data to InfluxDB."""
    try:
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)

        # Parse timestamp
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            ts = datetime.now(timezone.utc)

        # Create point
        point = (
            Point("vehicle-sensors")
            .tag("vehicle_id", vehicle_id)
            .field("speed", sensor_data.get("speed", 0.0))
            .field("acceleration", sensor_data.get("acceleration", 0.0))
            .field("obstacle_distance", sensor_data.get("obstacle_distance", 0.0))
            .field("lidar_points", sensor_data.get("lidar_points", 0))
            .time(ts)
        )

        # Write to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        print(f"Written sensor data for vehicle {vehicle_id} at {ts}")
        return True

    except Exception as e:
        print(f"Error writing sensor data to InfluxDB: {e}")
        return False


def process_message(msg, influx_client):
    """Process a single Kafka message."""
    if msg is None:
        return

    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            # End of partition, just log
            print(f"Reached end of partition: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
            return
        else:
            print(f"Kafka error: {msg.error()}")
            return

    try:
        # Parse message
        value = msg.value()
        if isinstance(value, bytes):
            value = value.decode("utf-8")

        event = json.loads(value)

        # Extract sensor data
        sensor_data = event.get("sensor_data", {})
        vehicle_id = event.get("vehicle_id", "unknown")
        timestamp = event.get("timestamp", datetime.now(timezone.utc).isoformat())

        if not sensor_data:
            print("No sensor data in event, skipping")
            return

        # Write to InfluxDB
        write_sensor_data_to_influxdb(influx_client, sensor_data, vehicle_id, timestamp)

    except json.JSONDecodeError as e:
        print(f"Failed to parse message JSON: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")


def main():
    """Main consumer loop."""
    global shutdown_event

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Starting sensor consumer...")
    print(f"Kafka broker: {KAFKA_BROKER}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Group ID: {KAFKA_GROUP_ID}")
    print(f"InfluxDB URL: {INFLUXDB_URL}")
    print(f"Bucket: {INFLUXDB_BUCKET}")
    print()

    # Create consumers and clients
    consumer = create_kafka_consumer()
    influx_client = create_influxdb_client()

    try:
        # Subscribe to topic
        consumer.subscribe([KAFKA_TOPIC])
        print(f"Subscribed to topic: {KAFKA_TOPIC}")
        print("Waiting for messages...")

        while not shutdown_event:
            msg = consumer.poll(timeout=1.0)
            process_message(msg, influx_client)

    except KeyboardInterrupt:
        print("\nUser interrupted, shutting down...")
    except KafkaException as e:
        print(f"Kafka exception: {e}")
    finally:
        # Clean up
        print("Closing consumer...")
        consumer.close()
        influx_client.close()
        print("Consumer stopped.")


if __name__ == "__main__":
    main()
