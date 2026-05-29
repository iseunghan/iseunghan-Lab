"""Feast feature views generated from the shared feature registry."""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
PATH_CANDIDATES = (ROOT_DIR / "backend", ROOT_DIR)
for candidate in PATH_CANDIDATES:
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from feast import FeatureView, Field, FileSource
from feast.data_format import ParquetFormat
from feast.types import Bool, Float32, Int64

from app.services.feature_registry import get_feature_view_specs
from entities import vehicle

FEAST_DTYPE_MAP = {
    "Float32": Float32,
    "Int64": Int64,
    "Bool": Bool,
}


def _to_feast_field(field_spec):
    return Field(name=field_spec.name, dtype=FEAST_DTYPE_MAP[field_spec.dtype])


def _build_feature_view(feature_view_spec):
    source = FileSource(
        name=f"{feature_view_spec.name}_source",
        path=feature_view_spec.resolve_source_path(),
        timestamp_field=feature_view_spec.timestamp_field,
        file_format=ParquetFormat(),
    )
    return FeatureView(
        name=feature_view_spec.name,
        entities=[vehicle],
        ttl=timedelta(hours=feature_view_spec.ttl_hours),
        schema=[_to_feast_field(field) for field in feature_view_spec.fields if field.online],
        source=source,
        online=True,
        description=feature_view_spec.description,
    )


FEATURE_VIEW_SPECS = get_feature_view_specs()
FEATURE_VIEW_BY_NAME = {spec.name: spec for spec in FEATURE_VIEW_SPECS}

sensor_features = _build_feature_view(FEATURE_VIEW_BY_NAME["sensor_features"])
image_features = _build_feature_view(FEATURE_VIEW_BY_NAME["image_features"])
audio_features = _build_feature_view(FEATURE_VIEW_BY_NAME["audio_features"])

__all__ = ["sensor_features", "image_features", "audio_features"]
