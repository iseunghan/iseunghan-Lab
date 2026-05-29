"""Single source of truth for feature view definitions and derived metadata."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class FeatureFieldSpec:
    """Specification for a single feature field."""

    name: str
    dtype: str
    description: str = ""
    online: bool = True
    prediction_default: Any = None


@dataclass(frozen=True)
class FeatureViewSpec:
    """Specification for a Feast feature view and its derived consumers."""

    name: str
    entity: str
    source_path_template: str
    ttl_hours: int
    fields: Tuple[FeatureFieldSpec, ...]
    timestamp_field: str = "event_timestamp"
    raw_input_kind: str = ""
    mock_fallback_policy: str = "default_row"
    build_bucket: str = "mlops-features"
    build_prefix_template: str = "{name}/{vehicle_id}/{date}.parquet"
    description: str = ""

    def resolve_source_path(self, feast_data_path: Optional[str] = None) -> str:
        base_path = (
            feast_data_path
            or os.getenv("FEAST_DATA_PATH", "s3://mlops-features")
        ).rstrip("/")
        return self.source_path_template.format(feast_data_path=base_path)

    @property
    def feature_names(self) -> List[str]:
        return [field.name for field in self.fields if field.online]

    @property
    def online_feature_refs(self) -> List[str]:
        return [f"{self.name}:{field.name}" for field in self.fields if field.online]

    def resolve_build_prefix(
        self,
        vehicle_id: str,
        built_at: Optional[datetime] = None,
    ) -> str:
        timestamp = built_at or datetime.now(timezone.utc)
        build_date = timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d")
        return self.build_prefix_template.format(
            name=self.name,
            feature_view_name=self.name,
            vehicle_id=vehicle_id,
            date=build_date,
            build_date=build_date,
        )


class FeatureRegistry:
    """Registry of feature view specs plus derived helper methods."""

    def __init__(self, feature_views: Sequence[FeatureViewSpec]):
        self._feature_views: Tuple[FeatureViewSpec, ...] = tuple(feature_views)
        self._by_name: Dict[str, FeatureViewSpec] = {
            feature_view.name: feature_view for feature_view in self._feature_views
        }

    def get_feature_view_specs(self) -> Tuple[FeatureViewSpec, ...]:
        return self._feature_views

    def get_feature_view_spec(self, feature_view_name: str) -> Optional[FeatureViewSpec]:
        return self._by_name.get(feature_view_name)

    def get_feature_view_names(self) -> List[str]:
        return [feature_view.name for feature_view in self._feature_views]

    def get_buildable_feature_view_specs(self) -> Tuple[FeatureViewSpec, ...]:
        return tuple(
            feature_view
            for feature_view in self._feature_views
            if feature_view.raw_input_kind
        )

    def iter_build_specs(self) -> Iterable[FeatureViewSpec]:
        yield from self.get_buildable_feature_view_specs()

    def get_feature_refs(
        self,
        feature_view_names: Optional[Sequence[str]] = None,
        online_only: bool = True,
    ) -> List[str]:
        refs: List[str] = []
        selected = (
            self._feature_views
            if feature_view_names is None
            else [self._by_name[name] for name in feature_view_names if name in self._by_name]
        )
        for feature_view in selected:
            for field in feature_view.fields:
                if online_only and not field.online:
                    continue
                refs.append(f"{feature_view.name}:{field.name}")
        return refs

    def get_feature_ref_map(self) -> Dict[str, str]:
        return {
            field.name: f"{feature_view.name}:{field.name}"
            for feature_view in self._feature_views
            for field in feature_view.fields
            if field.online
        }

    def get_training_feature_columns(self) -> List[str]:
        return [ref.split(":", 1)[1] for ref in self.get_feature_refs()]

    def get_prediction_feature_names(self) -> List[str]:
        return [
            field.name
            for feature_view in self._feature_views
            for field in feature_view.fields
            if field.online and field.prediction_default is not None
        ]

    def get_prediction_fallback_defaults(self) -> Dict[str, Any]:
        defaults: Dict[str, Any] = {}
        for feature_view in self._feature_views:
            for field in feature_view.fields:
                if field.online and field.prediction_default is not None:
                    defaults[field.name] = field.prediction_default
        return defaults

    def get_catalog_items(self, feast_data_path: Optional[str] = None) -> List[Dict[str, object]]:
        items: List[Dict[str, object]] = []
        for feature_view in self._feature_views:
            items.append(
                {
                    "name": feature_view.name,
                    "source": feature_view.resolve_source_path(feast_data_path),
                    "ttl_hours": feature_view.ttl_hours,
                    "online": True,
                    "features": feature_view.feature_names,
                }
            )
        return items


FEATURE_REGISTRY = FeatureRegistry(
    feature_views=(
        FeatureViewSpec(
            name="sensor_features",
            entity="vehicle",
            source_path_template="{feast_data_path}/sensor_features/*/*.parquet",
            ttl_hours=168,
            raw_input_kind="sensor_timeseries",
            mock_fallback_policy="none",
            build_bucket="mlops-features",
            build_prefix_template="{name}/{vehicle_id}/{date}.parquet",
            description="Sensor features from time-series data",
            fields=(
                FeatureFieldSpec(
                    name="avg_speed_10s",
                    dtype="Float32",
                    description="Average speed over 10-second windows",
                    prediction_default=0.0,
                ),
                FeatureFieldSpec(
                    name="accel_std_10s",
                    dtype="Float32",
                    description="Acceleration standard deviation over 10-second windows",
                ),
                FeatureFieldSpec(
                    name="obstacle_distance_min",
                    dtype="Float32",
                    description="Minimum obstacle distance over 10-second windows",
                    prediction_default=100.0,
                ),
                FeatureFieldSpec(
                    name="lidar_point_count",
                    dtype="Int64",
                    description="Total lidar point count over 10-second windows",
                ),
                FeatureFieldSpec(
                    name="sensor_missing_rate",
                    dtype="Float32",
                    description="Rate of missing sensor data",
                    prediction_default=0.0,
                ),
            ),
        ),
        FeatureViewSpec(
            name="image_features",
            entity="vehicle",
            source_path_template="{feast_data_path}/image_features/*/*.parquet",
            ttl_hours=168,
            raw_input_kind="image_metadata",
            mock_fallback_policy="default_row",
            build_bucket="mlops-features",
            build_prefix_template="{name}/{vehicle_id}/{date}.parquet",
            description="Demo image features derived from metadata, not raw-image inference",
            fields=(
                FeatureFieldSpec(
                    name="object_count",
                    dtype="Int64",
                    description="Detected object count",
                ),
                FeatureFieldSpec(
                    name="pedestrian_count",
                    dtype="Int64",
                    description="Detected pedestrian count",
                    prediction_default=0,
                ),
                FeatureFieldSpec(
                    name="lane_detect_score",
                    dtype="Float32",
                    description="Lane detection confidence score",
                ),
            ),
        ),
        FeatureViewSpec(
            name="audio_features",
            entity="vehicle",
            source_path_template="{feast_data_path}/audio_features/*/*.parquet",
            ttl_hours=168,
            raw_input_kind="audio_metadata",
            mock_fallback_policy="default_row",
            build_bucket="mlops-features",
            build_prefix_template="{name}/{vehicle_id}/{date}.parquet",
            description="Demo audio features derived from metadata, not raw-audio inference",
            fields=(
                FeatureFieldSpec(
                    name="noise_level",
                    dtype="Float32",
                    description="Estimated noise level",
                ),
                FeatureFieldSpec(
                    name="siren_detected",
                    dtype="Bool",
                    description="Whether a siren was detected",
                    prediction_default=False,
                ),
            ),
        ),
    )
)


def get_feature_view_specs() -> Tuple[FeatureViewSpec, ...]:
    return FEATURE_REGISTRY.get_feature_view_specs()


def get_feature_view_spec(feature_view_name: str) -> Optional[FeatureViewSpec]:
    return FEATURE_REGISTRY.get_feature_view_spec(feature_view_name)


def get_feature_view_names() -> List[str]:
    return FEATURE_REGISTRY.get_feature_view_names()


def get_buildable_feature_view_specs() -> Tuple[FeatureViewSpec, ...]:
    return FEATURE_REGISTRY.get_buildable_feature_view_specs()


def iter_build_specs() -> Iterable[FeatureViewSpec]:
    return FEATURE_REGISTRY.iter_build_specs()


def get_feature_refs(
    feature_view_names: Optional[Sequence[str]] = None,
    online_only: bool = True,
) -> List[str]:
    return FEATURE_REGISTRY.get_feature_refs(
        feature_view_names=feature_view_names,
        online_only=online_only,
    )


def get_feature_ref_map() -> Dict[str, str]:
    return FEATURE_REGISTRY.get_feature_ref_map()


def get_training_feature_columns() -> List[str]:
    return FEATURE_REGISTRY.get_training_feature_columns()


def get_prediction_feature_names() -> List[str]:
    return FEATURE_REGISTRY.get_prediction_feature_names()


def get_prediction_fallback_defaults() -> Dict[str, Any]:
    return FEATURE_REGISTRY.get_prediction_fallback_defaults()


def get_catalog_items(feast_data_path: Optional[str] = None) -> List[Dict[str, object]]:
    return FEATURE_REGISTRY.get_catalog_items(feast_data_path=feast_data_path)
