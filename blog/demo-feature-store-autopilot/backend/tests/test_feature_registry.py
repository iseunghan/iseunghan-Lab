"""Tests for the shared feature registry."""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.feature_registry import (
    get_buildable_feature_view_specs,
    get_catalog_items,
    get_feature_refs,
    get_feature_view_names,
    get_feature_view_spec,
    get_prediction_fallback_defaults,
    get_prediction_feature_names,
    get_training_feature_columns,
)


def test_registry_exposes_expected_feature_views():
    assert get_feature_view_names() == [
        "sensor_features",
        "image_features",
        "audio_features",
    ]


def test_registry_exposes_expected_feature_refs():
    assert get_feature_refs(["sensor_features"]) == [
        "sensor_features:avg_speed_10s",
        "sensor_features:accel_std_10s",
        "sensor_features:obstacle_distance_min",
        "sensor_features:lidar_point_count",
        "sensor_features:sensor_missing_rate",
    ]


def test_registry_training_columns_are_feature_only():
    assert get_training_feature_columns() == [
        "avg_speed_10s",
        "accel_std_10s",
        "obstacle_distance_min",
        "lidar_point_count",
        "sensor_missing_rate",
        "object_count",
        "pedestrian_count",
        "lane_detect_score",
        "noise_level",
        "siren_detected",
    ]


def test_registry_catalog_matches_feature_views():
    items = get_catalog_items()
    assert [item["name"] for item in items] == get_feature_view_names()

    sensor = items[0]
    assert sensor["source"].endswith("/sensor_features/*/*.parquet")
    assert sensor["ttl_hours"] == 168
    assert sensor["online"] is True
    assert sensor["features"] == get_feature_view_spec("sensor_features").feature_names
    assert "vehicle_id" not in sensor["features"]
    assert "event_timestamp" not in sensor["features"]


def test_registry_exposes_buildable_feature_views():
    assert [spec.name for spec in get_buildable_feature_view_specs()] == [
        "sensor_features",
        "image_features",
        "audio_features",
    ]


def test_registry_prediction_defaults_match_expected_subset():
    assert get_prediction_feature_names() == [
        "avg_speed_10s",
        "obstacle_distance_min",
        "sensor_missing_rate",
        "pedestrian_count",
        "siren_detected",
    ]
    assert get_prediction_fallback_defaults() == {
        "avg_speed_10s": 0.0,
        "obstacle_distance_min": 100.0,
        "sensor_missing_rate": 0.0,
        "pedestrian_count": 0,
        "siren_detected": False,
    }
