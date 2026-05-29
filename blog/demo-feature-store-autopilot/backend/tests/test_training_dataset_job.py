"""Tests for jobs/generate_training_dataset.py Step 1 contracts."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock
import sys

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from jobs import generate_training_dataset as dataset_job


def test_generate_from_feast_uses_historical_only(monkeypatch):
    feast_service = MagicMock()
    feast_service.get_historical_features.side_effect = [
        [
            {
                "vehicle_id": "V001",
                "event_timestamp": datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc),
                "avg_speed_10s": 40.0,
                "accel_std_10s": 1.0,
                "obstacle_distance_min": 20.0,
                "lidar_point_count": 1200,
                "sensor_missing_rate": 0.01,
                "object_count": 2,
                "pedestrian_count": 1,
                "lane_detect_score": 0.9,
                "noise_level": 61.0,
                "siren_detected": False,
            }
        ],
        [],
    ]
    feast_service.get_online_features = MagicMock()

    saved = {}

    def _capture_save(df: pd.DataFrame, _output_path: str):
        saved["df"] = df.copy()

    monkeypatch.setattr(dataset_job, "_save_dataset", _capture_save)

    success = dataset_job.generate_from_feast(
        feast_service=feast_service,
        vehicle_ids=["V001", "V002"],
        output_path="./data/test.parquet",
        hours=24,
        interval_minutes=60,
    )

    assert success is True
    assert feast_service.get_historical_features.call_count == 2
    feast_service.get_online_features.assert_not_called()
    assert "df" in saved
    assert set(["risk_score", "risk_level", "label_source"]).issubset(saved["df"].columns)
    assert set(saved["df"]["label_source"]) == {"synthetic_rule_v1"}


def test_generate_from_feast_preserves_historical_event_timestamp(monkeypatch):
    historical_ts = datetime(2026, 5, 19, 8, 30, tzinfo=timezone.utc)
    feast_service = MagicMock()
    feast_service.get_historical_features.return_value = [
        {
            "vehicle_id": "V001",
            "event_timestamp": historical_ts,
            "avg_speed_10s": 35.0,
            "accel_std_10s": 1.1,
            "obstacle_distance_min": 45.0,
            "lidar_point_count": 1300,
            "sensor_missing_rate": 0.02,
            "object_count": 1,
            "pedestrian_count": 0,
            "lane_detect_score": 0.95,
            "noise_level": 55.0,
            "siren_detected": False,
        }
    ]

    saved = {}

    def _capture_save(df: pd.DataFrame, _output_path: str):
        saved["df"] = df.copy()

    monkeypatch.setattr(dataset_job, "_save_dataset", _capture_save)

    success = dataset_job.generate_from_feast(
        feast_service=feast_service,
        vehicle_ids=["V001"],
        output_path="./data/test.parquet",
        hours=24,
        interval_minutes=60,
    )

    assert success is True
    assert "df" in saved
    ts_value = saved["df"].iloc[0]["event_timestamp"]
    assert pd.Timestamp(ts_value).tz_convert("UTC") == pd.Timestamp(historical_ts)


def test_generate_from_feast_returns_false_when_all_historical_results_empty(monkeypatch):
    feast_service = MagicMock()
    feast_service.get_historical_features.return_value = []
    feast_service.get_online_features = MagicMock()

    monkeypatch.setattr(dataset_job, "_save_dataset", lambda _df, _output_path: None)

    success = dataset_job.generate_from_feast(
        feast_service=feast_service,
        vehicle_ids=["V001", "V002", "V003"],
        output_path="./data/test.parquet",
        hours=24,
        interval_minutes=60,
    )

    assert success is False
    feast_service.get_online_features.assert_not_called()
