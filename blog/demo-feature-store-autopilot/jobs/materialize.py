#!/usr/bin/env python3
"""
Materialization Job: materialize.py

This job materializes latest offline features into the online store (Redis).
It uses Feast registry state for incremental materialization.

Usage:
    python jobs/materialize.py [--end-date 2026-05-24T12:00:00Z]

Arguments:
    --end-date: Optional ISO-8601 UTC timestamp. Defaults to now UTC.
"""

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.feast_service import FeastService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
FEAST_REPO_PATH = "./feast_repo"


def _parse_end_date(end_date_text: str) -> datetime:
    normalized = end_date_text.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Materialize Feast features incrementally")
    parser.add_argument(
        "--end-date",
        default=None,
        help="Optional ISO-8601 UTC timestamp. Defaults to now UTC.",
    )
    return parser.parse_args()


def main():
    """Main entry point for the materialization job."""
    args = parse_arguments()

    logger.info("=" * 60)
    logger.info("Starting Materialization Job")
    logger.info("=" * 60)

    # Initialize Feast service
    logger.info(f"Initializing Feast service with repo path: {FEAST_REPO_PATH}")

    try:
        feast_service = FeastService(repo_path=FEAST_REPO_PATH)
        logger.info("Feast service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Feast service: {e}")
        logger.error("Make sure Feast repository is set up and feature_store.yaml exists")
        return 1

    try:
        end_time = _parse_end_date(args.end_date) if args.end_date else datetime.now(timezone.utc)
    except ValueError as e:
        logger.error("Invalid --end-date format: %s", e)
        return 1

    logger.info(
        "Materialization end_date=%s (incremental range determined by Feast registry state)",
        end_time.isoformat(),
    )

    # Perform materialization
    logger.info("Starting incremental materialization...")

    success = feast_service.materialize_incremental(end_date=end_time)

    # Report results
    logger.info("\n" + "=" * 60)
    logger.info("Materialization Job Summary")
    logger.info("=" * 60)

    if success:
        logger.info("Status: SUCCESS")
        logger.info(f"Materialized features up to end_date: {end_time.isoformat()}")
        logger.info("Features are now available in Redis for online serving")
    else:
        logger.info("Status: FAILED")
        logger.error("Materialization failed - check logs for details")
        logger.error("Ensure offline store (Parquet files) has data to materialize")

    logger.info("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
