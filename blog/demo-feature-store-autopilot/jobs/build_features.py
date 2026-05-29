#!/usr/bin/env python3
"""
Feature Engineering Job: build_features.py

This job builds features from raw sensor/media data and saves them as Parquet files to MinIO.
It initializes the necessary services and processes demo vehicles (V001, V002, V003).

Usage:
    python jobs/build_features.py
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.influx_service import InfluxService
from app.services.minio_service import MinIOService
from app.services.feature_builder import FeatureBuilderService
from app.services.feature_registry import get_buildable_feature_view_specs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "mytoken")
INFLUX_ORG = os.getenv("INFLUX_ORG", "myorg")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "features")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin123")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Demo vehicles
DEMO_VEHICLES = ["V001", "V002", "V003"]

DEFAULT_LOOKBACK_HOURS = 168
RAW_INPUT_KIND_TO_MEDIA_TYPE: Dict[str, str] = {
    "image_metadata": "images",
    "audio_metadata": "audio",
}


def _parse_iso_datetime_to_utc(dt_text: str) -> datetime:
    normalized = dt_text.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Build feature parquet files from raw data (supports backfill windows)."
    )
    parser.add_argument(
        "--vehicle-ids",
        default=",".join(DEMO_VEHICLES),
        help=f"Comma-separated vehicle ids (default: {','.join(DEMO_VEHICLES)})",
    )
    parser.add_argument(
        "--start-date",
        default=None,
        help="Optional ISO-8601 UTC start datetime for backfill window.",
    )
    parser.add_argument(
        "--end-date",
        default=None,
        help="Optional ISO-8601 UTC end datetime for backfill window.",
    )
    return parser.parse_args()


def _parse_vehicle_ids(vehicle_ids_text: str) -> List[str]:
    vehicle_ids = [vehicle_id.strip() for vehicle_id in vehicle_ids_text.split(",")]
    parsed = [vehicle_id for vehicle_id in vehicle_ids if vehicle_id]
    return parsed or DEMO_VEHICLES


def _resolve_time_window(
    start_date_text: Optional[str], end_date_text: Optional[str]
) -> Tuple[datetime, datetime]:
    end_time = _parse_iso_datetime_to_utc(end_date_text) if end_date_text else datetime.now(timezone.utc)
    if start_date_text:
        start_time = _parse_iso_datetime_to_utc(start_date_text)
    else:
        lookback_hours = int(os.getenv("FEATURE_BUILD_LOOKBACK_HOURS", str(DEFAULT_LOOKBACK_HOURS)))
        start_time = end_time - timedelta(hours=lookback_hours)

    if start_time > end_time:
        raise ValueError("start-date must be less than or equal to end-date")

    return start_time, end_time


def _get_raw_media_bucket_name() -> str:
    return (
        os.getenv("MINIO_RAW_MEDIA_BUCKET")
        or os.getenv("MINIO_BUCKET")
        or "mlops-raw-media"
    )


def _get_media_metadata_uris(
    minio_service: MinIOService,
    vehicle_id: str,
    media_type: str,
) -> List[str]:
    if media_type not in {"images", "audio"}:
        return []

    bucket = _get_raw_media_bucket_name()
    prefix = f"{media_type}/{vehicle_id}/"
    object_names = minio_service.list_objects(bucket_name=bucket, prefix=prefix)
    return [name for name in object_names if name.endswith(".json")]


def _build_feature_rows(
    feature_builder: FeatureBuilderService,
    minio_service: MinIOService,
    feature_view_spec,
    vehicle_id: str,
    start_time: datetime,
    end_time: datetime,
) -> bool:
    """Build and save a feature view using the registry spec."""
    logger.info(
        "Processing feature view=%s for vehicle=%s",
        feature_view_spec.name,
        vehicle_id,
    )

    if feature_view_spec.raw_input_kind == "sensor_timeseries":
        features = feature_builder.build_sensor_features(
            vehicle_id=vehicle_id,
            start_time=start_time,
            end_time=end_time,
        )
    else:
        media_type = RAW_INPUT_KIND_TO_MEDIA_TYPE.get(feature_view_spec.raw_input_kind)
        if media_type == "images":
            uris = _get_media_metadata_uris(minio_service, vehicle_id, media_type)
            features = feature_builder.build_image_features(
                vehicle_id=vehicle_id,
                image_uris=uris,
                start_time=start_time,
                end_time=end_time,
            )
        elif media_type == "audio":
            uris = _get_media_metadata_uris(minio_service, vehicle_id, media_type)
            features = feature_builder.build_audio_features(
                vehicle_id=vehicle_id,
                audio_uris=uris,
                start_time=start_time,
                end_time=end_time,
            )
        else:
            logger.warning(
                "Unsupported raw_input_kind for feature view=%s raw_input_kind=%s",
                feature_view_spec.name,
                feature_view_spec.raw_input_kind,
            )
            return False

    if not features:
        logger.warning(
            "No features built for feature view=%s vehicle=%s",
            feature_view_spec.name,
            vehicle_id,
        )
        return False

    built_at = datetime.now(timezone.utc)
    prefix = feature_view_spec.resolve_build_prefix(vehicle_id=vehicle_id, built_at=built_at)
    success = feature_builder.save_features_to_parquet(
        features=features,
        bucket=feature_view_spec.build_bucket,
        prefix=prefix,
    )

    if success:
        logger.info(
            "Successfully saved %d %s feature rows for vehicle=%s bucket=%s prefix=%s",
            len(features),
            feature_view_spec.name,
            vehicle_id,
            feature_view_spec.build_bucket,
            prefix,
        )
    else:
        logger.error(
            "Failed to save %s features for vehicle=%s",
            feature_view_spec.name,
            vehicle_id,
        )

    return success


def build_and_store_feature_view(
    feature_builder: FeatureBuilderService,
    minio_service: MinIOService,
    feature_view_spec,
    vehicle_id: str,
    start_time: datetime,
    end_time: datetime,
) -> bool:
    """Build and persist one registry-defined feature view."""
    return _build_feature_rows(
        feature_builder=feature_builder,
        minio_service=minio_service,
        feature_view_spec=feature_view_spec,
        vehicle_id=vehicle_id,
        start_time=start_time,
        end_time=end_time,
    )


def main():
    """Main entry point for the feature engineering job."""
    args = parse_arguments()

    vehicle_ids = _parse_vehicle_ids(args.vehicle_ids)
    try:
        start_time, end_time = _resolve_time_window(args.start_date, args.end_date)
    except ValueError as error:
        logger.error("Invalid time window: %s", error)
        return 1

    logger.info("=" * 60)
    logger.info("Starting Feature Engineering Job")
    logger.info("=" * 60)
    logger.info(
        "Configured build window: start=%s, end=%s, vehicles=%s",
        start_time.isoformat(),
        end_time.isoformat(),
        vehicle_ids,
    )

    # Initialize services
    logger.info("Initializing services...")

    influx_service = InfluxService(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
        bucket=INFLUX_BUCKET
    )

    minio_service = MinIOService(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )

    feature_builder = FeatureBuilderService(
        influx_service=influx_service,
        minio_service=minio_service
    )

    build_specs = get_buildable_feature_view_specs()

    # Ensure buckets exist
    logger.info("Ensuring MinIO buckets exist...")
    bucket_names = []
    seen_buckets = set()
    for spec in build_specs:
        if spec.build_bucket in seen_buckets:
            continue
        seen_buckets.add(spec.build_bucket)
        bucket_names.append(spec.build_bucket)
    for bucket_name in bucket_names:
        minio_service.create_bucket(bucket_name)

    # Process each vehicle
    logger.info(f"Processing vehicles: {vehicle_ids}")

    success_count = 0
    fail_count = 0

    for vehicle_id in vehicle_ids:
        logger.info(f"\n--- Processing vehicle: {vehicle_id} ---")

        vehicle_success = True

        for feature_view_spec in build_specs:
            if not build_and_store_feature_view(
                feature_builder=feature_builder,
                minio_service=minio_service,
                feature_view_spec=feature_view_spec,
                vehicle_id=vehicle_id,
                start_time=start_time,
                end_time=end_time,
            ):
                vehicle_success = False
                fail_count += 1
            else:
                success_count += 1

        if vehicle_success:
            logger.info(f"Vehicle {vehicle_id}: All features built successfully")
        else:
            logger.warning(f"Vehicle {vehicle_id}: Some features failed to build")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Feature Engineering Job Summary")
    logger.info("=" * 60)
    logger.info(f"Vehicles processed: {len(vehicle_ids)}")
    logger.info(f"Successful feature builds: {success_count}")
    logger.info(f"Failed feature builds: {fail_count}")
    logger.info("=" * 60)

    # Cleanup
    influx_service.close()
    minio_service.close()

    logger.info("Feature Engineering Job completed")

    # Return exit code based on success
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
