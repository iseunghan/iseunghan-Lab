#!/usr/bin/env python3
"""
Training Dataset Generation Job: generate_training_dataset.py

This job generates a training dataset from Feast historical features.
Production mode is the canonical path and only uses historical retrieval.

Usage:
    python jobs/generate_training_dataset.py --demo --output <path>
    python jobs/generate_training_dataset.py --output <path> [--hours 168] [--interval-minutes 60] [--vehicle-ids V001,V002,V003]

Arguments:
    --demo: Run demo mode with mock data
    --output: Output path (default: ./data/training_dataset.parquet)
    --hours: Historical lookback in hours (default: 168)
    --interval-minutes: Interval between entity rows in minutes (default: 60)
    --vehicle-ids: Comma-separated vehicle IDs (default: V001,V002,V003)
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pandas as pd
from app.services.feast_service import FeastService
from app.services.risk_model import RiskModelService
from app.services.feature_registry import (
    get_feature_view_names,
    get_training_feature_columns,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
FEAST_REPO_PATH = "./feast_repo"
DEFAULT_OUTPUT_PATH = "./data/training_dataset.parquet"
DEFAULT_HOURS = 168  # 7 days of historical data
DEFAULT_INTERVAL_MINUTES = 60
DEFAULT_VEHICLE_IDS = ["V001", "V002", "V003"]
DEFAULT_FEATURE_VIEWS = get_feature_view_names()
LABEL_SOURCE = "synthetic_rule_v1"
FEATURE_COLUMNS = get_training_feature_columns()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate training dataset from Feast")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output path for dataset (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=DEFAULT_HOURS,
        help=f"Historical lookback in hours (default: {DEFAULT_HOURS})",
    )
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=DEFAULT_INTERVAL_MINUTES,
        help=f"Interval minutes between entity rows (default: {DEFAULT_INTERVAL_MINUTES})",
    )
    parser.add_argument(
        "--vehicle-ids",
        default=",".join(DEFAULT_VEHICLE_IDS),
        help=f"Comma-separated vehicle IDs (default: {','.join(DEFAULT_VEHICLE_IDS)})",
    )
    return parser.parse_args()


def _parse_vehicle_ids(vehicle_ids_text: str) -> List[str]:
    vehicle_ids = [vehicle_id.strip() for vehicle_id in vehicle_ids_text.split(",")]
    return [vehicle_id for vehicle_id in vehicle_ids if vehicle_id]


def _save_dataset(df: pd.DataFrame, output_path: str) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    suffix = output.suffix.lower()
    if suffix == ".csv":
        df.to_csv(output, index=False)
    else:
        df.to_parquet(output, index=False)


def _append_synthetic_labels(df: pd.DataFrame) -> pd.DataFrame:
    risk_model = RiskModelService()

    risk_scores = []
    risk_levels = []
    for record in df.to_dict(orient="records"):
        score, level = risk_model.calculate_risk_score(record)
        risk_scores.append(score)
        risk_levels.append(level)

    df["risk_score"] = risk_scores
    df["risk_level"] = risk_levels
    df["label_source"] = LABEL_SOURCE
    return df


def _build_historical_dataframe(
    feast_service: FeastService,
    vehicle_ids: List[str],
    hours: int,
    interval_minutes: int,
) -> pd.DataFrame:
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)
    logger.info(
        "Starting historical retrieval for training dataset "
        "(start_time=%s, end_time=%s, vehicle_count=%d, interval_minutes=%d)",
        start_time.isoformat(),
        end_time.isoformat(),
        len(vehicle_ids),
        interval_minutes,
    )

    all_rows = []
    for vehicle_id in vehicle_ids:
        logger.info("Retrieving historical features for vehicle_id=%s", vehicle_id)
        rows = feast_service.get_historical_features(
            vehicle_id=vehicle_id,
            feature_views=DEFAULT_FEATURE_VIEWS,
            start_time=start_time,
            end_time=end_time,
            interval_minutes=interval_minutes,
        )
        if not rows:
            logger.warning("No historical rows found for vehicle_id=%s", vehicle_id)
            continue
        all_rows.extend(rows)
        logger.info(
            "Retrieved %d historical rows for vehicle_id=%s", len(rows), vehicle_id
        )

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)

    if "event_timestamp" in df.columns:
        df["event_timestamp"] = pd.to_datetime(
            df["event_timestamp"], errors="coerce", utc=True
        )
        invalid_count = int(df["event_timestamp"].isna().sum())
        if invalid_count > 0:
            logger.warning("Dropping %d rows with invalid event_timestamp", invalid_count)
            df = df[df["event_timestamp"].notna()]

    for column in FEATURE_COLUMNS:
        if column not in df.columns:
            df[column] = None

    ordered_columns = ["vehicle_id", "event_timestamp"] + FEATURE_COLUMNS
    return df[ordered_columns]


def generate_demo_dataset(output_path: str) -> bool:
    """
    Generate a demo training dataset with mock data.

    This is useful for testing the pipeline without real feature data.

    Args:
        output_path: Path to save the training dataset

    Returns:
        True if dataset was generated successfully, False otherwise
    """
    logger.info("Generating demo training dataset...")

    # Create mock training data
    demo_data = {
        "vehicle_id": ["V001", "V001", "V002", "V002", "V003", "V003"],
        "event_timestamp": [
            datetime.now(timezone.utc) - timedelta(hours=1),
            datetime.now(timezone.utc) - timedelta(hours=2),
            datetime.now(timezone.utc) - timedelta(hours=1),
            datetime.now(timezone.utc) - timedelta(hours=2),
            datetime.now(timezone.utc) - timedelta(hours=1),
            datetime.now(timezone.utc) - timedelta(hours=2),
        ],
        "avg_speed_10s": [45.5, 52.3, 38.7, 41.2, 55.8, 48.9],
        "accel_std_10s": [2.1, 3.5, 1.8, 2.2, 4.1, 2.8],
        "obstacle_distance_min": [15.2, 8.5, 25.3, 18.7, 5.2, 12.1],
        "lidar_point_count": [1250, 1180, 1320, 1290, 1100, 1220],
        "sensor_missing_rate": [0.02, 0.05, 0.01, 0.03, 0.08, 0.04],
        "object_count": [5, 7, 3, 4, 8, 6],
        "pedestrian_count": [2, 3, 1, 1, 4, 2],
        "lane_detect_score": [0.85, 0.72, 0.91, 0.88, 0.65, 0.79],
        "noise_level": [65.0, 72.0, 58.0, 62.0, 78.0, 68.0],
        "siren_detected": [False, True, False, False, True, False],
        "risk_score": [0.35, 0.72, 0.25, 0.30, 0.85, 0.55],  # Target variable
    }

    try:
        df = pd.DataFrame(demo_data)
        df = _append_synthetic_labels(df)
        _save_dataset(df, output_path)
        logger.info(f"Demo training dataset saved to: {output_path}")
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"Dataset columns: {list(df.columns)}")

        return True

    except Exception as e:
        logger.error(f"Failed to generate demo dataset: {e}")
        return False


def generate_from_feast(
    feast_service: FeastService,
    vehicle_ids: List[str],
    output_path: str,
    hours: int = DEFAULT_HOURS,
    interval_minutes: int = DEFAULT_INTERVAL_MINUTES,
) -> bool:
    """
    Generate training dataset from Feast feature store.

    Args:
        feast_service: FeastService instance for retrieving features
        vehicle_ids: Vehicle IDs for historical retrieval
        output_path: Path to save the training dataset
        hours: Number of hours of historical data to include
        interval_minutes: Interval in minutes for entity rows

    Returns:
        True if dataset was generated successfully, False otherwise
    """
    logger.info(
        "Generating training dataset from Feast historical features "
        "(hours=%d, interval_minutes=%d, vehicle_ids=%s)",
        hours,
        interval_minutes,
        vehicle_ids,
    )

    try:
        df = _build_historical_dataframe(
            feast_service=feast_service,
            vehicle_ids=vehicle_ids,
            hours=hours,
            interval_minutes=interval_minutes,
        )

        if df.empty:
            logger.warning("No historical features retrieved for any requested vehicle")
            return False

        df = _append_synthetic_labels(df)
        _save_dataset(df, output_path)

        label_distribution = df["risk_level"].value_counts(dropna=False).to_dict()
        feature_count = len([column for column in FEATURE_COLUMNS if column in df.columns])

        logger.info("Training dataset saved to: %s", output_path)
        logger.info(
            "Training dataset summary: rows=%d, feature_count=%d, label_distribution=%s",
            len(df),
            feature_count,
            label_distribution,
        )

        return True

    except Exception as e:
        logger.error(f"Failed to generate dataset from Feast: {e}")
        return False


def main():
    """Main entry point for the training dataset generation job."""
    args = parse_arguments()
    vehicle_ids = _parse_vehicle_ids(args.vehicle_ids)

    logger.info("=" * 60)
    logger.info("Starting Training Dataset Generation Job")
    logger.info("=" * 60)

    if args.demo:
        logger.info("Running in DEMO mode")
        logger.info("Generating training dataset with mock data...")

        success = generate_demo_dataset(args.output)
    else:
        logger.info("Running in PRODUCTION mode")
        logger.info("Generating training dataset from Feast historical features...")

        # Initialize Feast service
        logger.info(f"Initializing Feast service with repo path: {FEAST_REPO_PATH}")

        try:
            feast_service = FeastService(repo_path=FEAST_REPO_PATH)
            logger.info("Feast service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Feast service: {e}")
            logger.error("Make sure Feast repository is set up and feature_store.yaml exists")
            return 1

        # Generate dataset from Feast
        success = generate_from_feast(
            feast_service=feast_service,
            vehicle_ids=vehicle_ids or DEFAULT_VEHICLE_IDS,
            output_path=args.output,
            hours=args.hours,
            interval_minutes=args.interval_minutes,
        )

    # Report results
    logger.info("\n" + "=" * 60)
    logger.info("Training Dataset Generation Job Summary")
    logger.info("=" * 60)

    if success:
        logger.info("Status: SUCCESS")
        logger.info(f"Output file: {args.output}")
        logger.info("Dataset is ready for model training")
    else:
        logger.info("Status: FAILED")
        logger.error("Dataset generation failed - check logs for details")

    logger.info("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
