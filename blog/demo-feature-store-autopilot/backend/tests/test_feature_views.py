"""Tests for Feast feature view schema definitions."""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
FEAST_REPO_DIR = ROOT_DIR / "feast_repo"

if str(FEAST_REPO_DIR) not in sys.path:
    sys.path.insert(0, str(FEAST_REPO_DIR))

from feature_views import audio_features, image_features, sensor_features
from app.services.feature_registry import get_feature_view_spec


def _schema_names(feature_view):
    return [field.name for field in feature_view.schema]


def test_sensor_feature_view_schema_contains_only_features():
    names = _schema_names(sensor_features)
    spec = get_feature_view_spec("sensor_features")
    assert spec is not None
    assert set(names) == set(spec.feature_names)
    assert len(names) == len(spec.feature_names)


def test_image_feature_view_schema_excludes_raw_uri_and_entity_timestamp():
    names = _schema_names(image_features)
    spec = get_feature_view_spec("image_features")
    assert spec is not None
    assert "vehicle_id" not in names
    assert "event_timestamp" not in names
    assert "image_uri" not in names
    assert set(names) == set(spec.feature_names)
    assert len(names) == len(spec.feature_names)


def test_audio_feature_view_schema_excludes_raw_uri_and_entity_timestamp():
    names = _schema_names(audio_features)
    spec = get_feature_view_spec("audio_features")
    assert spec is not None
    assert "vehicle_id" not in names
    assert "event_timestamp" not in names
    assert "audio_uri" not in names
    assert set(names) == set(spec.feature_names)
    assert len(names) == len(spec.feature_names)
