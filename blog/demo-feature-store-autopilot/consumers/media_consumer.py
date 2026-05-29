"""
Kafka Consumer for Vehicle Media Metadata

Consumes vehicle events from Kafka and stores media metadata in MinIO.
"""

import io
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone

from confluent_kafka import Consumer, KafkaError, KafkaException
from minio import Minio
from minio.error import S3Error
import dotenv


# Load environment variables
dotenv.load_dotenv()

# Configuration
KAFKA_BROKER = os.getenv("KAFKA_HOST", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "vehicle-events")
KAFKA_GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP", "media-consumer-group")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "mlops-raw-media")

# Validate required environment variables
if not MINIO_ENDPOINT or not MINIO_ACCESS_KEY or not MINIO_SECRET_KEY:
    raise ValueError(
        "Missing required environment variables: "
        "MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY must be set"
    )

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


def create_minio_client():
    """Create MinIO client."""
    return Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )


def ensure_bucket_exists(minio_client, bucket_name: str):
    """Ensure the bucket exists, create if not."""
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Created bucket: {bucket_name}")
    except S3Error as e:
        print(f"Error checking/creating bucket: {e}")
        raise


def _get_date_str(timestamp: str) -> str:
    """Extract date string from timestamp for hierarchical storage."""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y/%m/%d")
    except (ValueError, AttributeError):
        return datetime.now(timezone.utc).strftime("%Y/%m/%d")


def _upload_metadata(minio_client, object_key: str, metadata: dict) -> bool:
    """Upload metadata JSON to MinIO."""
    try:
        data = json.dumps(metadata, indent=2).encode("utf-8")
        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_key,
            data=io.BytesIO(data),
            length=len(data),
            content_type="application/json",
        )
        print(f"Stored metadata: {object_key}")
        return True
    except S3Error as e:
        print(f"S3 error storing metadata: {e}")
        return False
    except Exception as e:
        print(f"Error storing metadata: {e}")
        return False


def store_camera_metadata(minio_client, media_data: dict, vehicle_id: str, event_id: str):
    """Extract camera_frames from media_data and store to images/ prefix in MinIO."""
    camera_frames = media_data.get("camera_frames")
    if not camera_frames:
        return False

    timestamp = media_data.get("timestamp", datetime.now(timezone.utc).isoformat())
    date_str = _get_date_str(timestamp)
    object_key = f"images/{vehicle_id}/{date_str}/{event_id}.json"

    metadata_to_store = {
        "event_id": event_id,
        "vehicle_id": vehicle_id,
        "timestamp": timestamp,
        "media_type": "images",
        "camera_frames": camera_frames,
    }

    return _upload_metadata(minio_client, object_key, metadata_to_store)


def store_audio_metadata(minio_client, media_data: dict, vehicle_id: str, event_id: str):
    """Extract audio from media_data and store to audio/ prefix in MinIO."""
    audio_data = media_data.get("audio")
    if not audio_data:
        return False

    timestamp = media_data.get("timestamp", datetime.now(timezone.utc).isoformat())
    date_str = _get_date_str(timestamp)
    object_key = f"audio/{vehicle_id}/{date_str}/{event_id}.json"

    metadata_to_store = {
        "event_id": event_id,
        "vehicle_id": vehicle_id,
        "timestamp": timestamp,
        "media_type": "audio",
        "audio": audio_data,
    }

    return _upload_metadata(minio_client, object_key, metadata_to_store)


def process_message(msg, minio_client):
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

        # Extract event metadata
        event_id = event.get("event_id", "unknown")
        vehicle_id = event.get("vehicle_id", "unknown")
        timestamp = event.get("timestamp", datetime.now(timezone.utc).isoformat())
        scenario = event.get("scenario", "normal")

        # Extract media data if present
        media_data = event.get("media_data", {})

        if not media_data:
            # No media data in this event, skip
            return

        # Add event context to media data
        media_data["event_id"] = event_id
        media_data["vehicle_id"] = vehicle_id
        media_data["timestamp"] = timestamp
        media_data["scenario"] = scenario

        # Store camera metadata if present
        if "camera_frames" in media_data:
            store_camera_metadata(minio_client, media_data, vehicle_id, event_id)

        # Store audio metadata if present
        if "audio" in media_data:
            store_audio_metadata(minio_client, media_data, vehicle_id, event_id)

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

    print(f"Starting media consumer...")
    print(f"Kafka broker: {KAFKA_BROKER}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"Group ID: {KAFKA_GROUP_ID}")
    print(f"MinIO endpoint: {MINIO_ENDPOINT}")
    print(f"Bucket: {MINIO_BUCKET}")
    print()

    # Create consumers and clients
    consumer = create_kafka_consumer()
    minio_client = create_minio_client()

    try:
        # Ensure bucket exists
        ensure_bucket_exists(minio_client, MINIO_BUCKET)

        # Subscribe to topic
        consumer.subscribe([KAFKA_TOPIC])
        print(f"Subscribed to topic: {KAFKA_TOPIC}")
        print("Waiting for messages...")

        while not shutdown_event:
            msg = consumer.poll(timeout=1.0)
            process_message(msg, minio_client)

    except KeyboardInterrupt:
        print("\nUser interrupted, shutting down...")
    except KafkaException as e:
        print(f"Kafka exception: {e}")
    except S3Error as e:
        print(f"MinIO error: {e}")
    finally:
        # Clean up
        print("Closing consumer...")
        consumer.close()
        print("Consumer stopped.")


if __name__ == "__main__":
    main()
