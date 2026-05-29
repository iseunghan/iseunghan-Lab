"""Tests for jobs/build_features.py contracts."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.feature_registry import get_feature_view_spec, get_buildable_feature_view_specs
from jobs import build_features as build_job


def test_build_and_store_feature_view_uses_registry_prefix_and_bucket():
    feature_builder = MagicMock()
    feature_builder.build_sensor_features.return_value = [
        {
            "vehicle_id": "V001",
            "event_timestamp": "2026-05-24T00:00:00Z",
            "avg_speed_10s": 42.0,
        }
    ]
    feature_builder.save_features_to_parquet.return_value = True
    minio_service = MagicMock()

    spec = get_feature_view_spec("sensor_features")
    assert spec is not None

    success = build_job.build_and_store_feature_view(
        feature_builder=feature_builder,
        minio_service=minio_service,
        feature_view_spec=spec,
        vehicle_id="V001",
        start_time=datetime(2026, 5, 24, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 5, 24, 1, 0, tzinfo=timezone.utc),
    )

    assert success is True
    feature_builder.build_sensor_features.assert_called_once_with(
        vehicle_id="V001",
        start_time=datetime(2026, 5, 24, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 5, 24, 1, 0, tzinfo=timezone.utc),
    )
    save_call = feature_builder.save_features_to_parquet.call_args.kwargs
    assert save_call["bucket"] == "mlops-features"
    assert save_call["prefix"].startswith("sensor_features/V001/")
    assert save_call["prefix"].endswith(".parquet")


@pytest.mark.parametrize(
    "feature_view_name,builder_method,uri_kwarg,media_type",
    [
        ("image_features", "build_image_features", "image_uris", "images"),
        ("audio_features", "build_audio_features", "audio_uris", "audio"),
    ],
)
def test_build_and_store_feature_view_uses_registry_media_dispatch(
    feature_view_name, builder_method, uri_kwarg, media_type
):
    feature_builder = MagicMock()
    feature_builder.save_features_to_parquet.return_value = True
    getattr(feature_builder, builder_method).return_value = [
        {
            "vehicle_id": "V001",
            "event_timestamp": "2026-05-24T00:00:00Z",
        }
    ]
    minio_service = MagicMock()
    minio_service.list_objects.return_value = [f"{media_type}/V001/frame_001.json"]

    spec = get_feature_view_spec(feature_view_name)
    assert spec is not None

    with patch(
        "jobs.build_features._get_media_metadata_uris",
        return_value=[f"{media_type}/V001/frame_001.json"],
    ) as mock_get_uris:
        success = build_job.build_and_store_feature_view(
            feature_builder=feature_builder,
            minio_service=minio_service,
            feature_view_spec=spec,
            vehicle_id="V001",
            start_time=datetime(2026, 5, 24, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 5, 24, 1, 0, tzinfo=timezone.utc),
        )

    assert success is True
    mock_get_uris.assert_called_once_with(minio_service, "V001", media_type)
    getattr(feature_builder, builder_method).assert_called_once_with(
        vehicle_id="V001",
        **{uri_kwarg: [f"{media_type}/V001/frame_001.json"]},
        start_time=datetime(2026, 5, 24, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 5, 24, 1, 0, tzinfo=timezone.utc),
    )


@patch("jobs.build_features.build_and_store_feature_view")
@patch("jobs.build_features.FeatureBuilderService")
@patch("jobs.build_features.MinIOService")
@patch("jobs.build_features.InfluxService")
def test_main_iterates_over_registry_build_specs(
    mock_influx_service_class,
    mock_minio_service_class,
    mock_feature_builder_class,
    mock_build_and_store_feature_view,
    monkeypatch,
):
    mock_influx_service = MagicMock()
    mock_minio_service = MagicMock()
    mock_feature_builder = MagicMock()
    mock_minio_service.create_bucket.return_value = True

    mock_influx_service_class.return_value = mock_influx_service
    mock_minio_service_class.return_value = mock_minio_service
    mock_feature_builder_class.return_value = mock_feature_builder
    mock_build_and_store_feature_view.return_value = True

    monkeypatch.setattr(
        build_job.sys,
        "argv",
        [
            "build_features.py",
            "--vehicle-ids",
            "V001,V002",
            "--start-date",
            "2026-05-24T00:00:00Z",
            "--end-date",
            "2026-05-24T01:00:00Z",
        ],
    )

    exit_code = build_job.main()

    assert exit_code == 0
    build_specs = get_buildable_feature_view_specs()
    assert mock_minio_service.create_bucket.call_count == len({spec.build_bucket for spec in build_specs})
    assert mock_build_and_store_feature_view.call_count == len(build_specs) * 2
    called_specs = [
        call.kwargs["feature_view_spec"].name
        for call in mock_build_and_store_feature_view.call_args_list
    ]
    assert called_specs == [spec.name for _ in range(2) for spec in build_specs]
