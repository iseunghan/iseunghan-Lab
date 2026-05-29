import os
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import pandas as pd

from app.services import FeatureBuilderService, InfluxService, MinIOService, FeastService
from app.services.risk_model import RiskModelService
from app.services.feature_registry import (
    get_catalog_items,
    get_feature_view_names,
    get_training_feature_columns,
)

logger = logging.getLogger(__name__)

router = APIRouter()
TRAINING_DEFAULT_VEHICLE_IDS = ["V001", "V002", "V003"]
TRAINING_LABEL_SOURCE = "synthetic_rule_v1"
DEFAULT_BUILD_LOOKBACK_DAYS = 7
DEFAULT_FEATURE_VIEW_NAMES = get_feature_view_names()
TRAINING_FEATURE_COLUMNS = get_training_feature_columns()

# Lazy initialization for services
_influx_service: Optional[InfluxService] = None
_minio_service: Optional[MinIOService] = None
_feature_builder: Optional[FeatureBuilderService] = None
_feast_service: Optional[FeastService] = None


def get_influx_service() -> InfluxService:
    """Get or create InfluxDB service instance (lazy initialization)."""
    global _influx_service
    if _influx_service is None:
        _influx_service = InfluxService(
            url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
            token=os.getenv("INFLUXDB_TOKEN", "mytoken"),
            org=os.getenv("INFLUXDB_ORG", "myorg"),
            bucket=os.getenv("INFLUXDB_BUCKET", "features")
        )
    return _influx_service


def get_minio_service() -> MinIOService:
    """Get or create MinIO service instance (lazy initialization)."""
    global _minio_service
    if _minio_service is None:
        _minio_service = MinIOService(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "admin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "admin123"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true"
        )
    return _minio_service


def get_feature_builder() -> FeatureBuilderService:
    """Get or create FeatureBuilder service instance (lazy initialization)."""
    global _feature_builder
    if _feature_builder is None:
        influx_svc = get_influx_service()
        minio_svc = get_minio_service()
        _feature_builder = FeatureBuilderService(influx_svc, minio_svc)
    return _feature_builder


def get_feast_service() -> FeastService:
    """Get or create Feast service instance (lazy initialization)."""
    global _feast_service
    if _feast_service is None:
        _feast_service = FeastService(repo_path="./feast_repo")
    return _feast_service


class BuildFeatureRequest(BaseModel):
    vehicle_id: Optional[str] = Query(None, description="Specific vehicle ID")
    start_date: Optional[str] = Query(None, description="Start date for feature building")
    end_date: Optional[str] = Query(None, description="End date for feature building")


class BuildFeatureResponse(BaseModel):
    success: bool
    message: str
    features_built: List[str]


class FeatureResponse(BaseModel):
    vehicle_id: str
    features: dict
    timestamp: str


class TrainingDatasetRequest(BaseModel):
    output_path: str = "./data/training_dataset.parquet"
    hours: int = 168
    interval_minutes: int = 60
    vehicle_ids: List[str] = Field(
        default_factory=lambda: TRAINING_DEFAULT_VEHICLE_IDS.copy()
    )


class TrainingDatasetResponse(BaseModel):
    success: bool
    message: str
    output_path: str
    row_count: int
    feature_count: int
    label_distribution: dict


class MaterializeRequest(BaseModel):
    end_date: Optional[str] = None


class MaterializeResponse(BaseModel):
    success: bool
    message: str
    end_date: str
    materialized_feature_views: List[str]


class FeatureStoreStatusResponse(BaseModel):
    vehicle_id: str
    lookback_hours: int
    last_materialization_end_date: Optional[str]
    offline_latest_feature_timestamp: Optional[str]
    offline_feature_age_seconds: Optional[int]
    online_feature_available: bool


class FeatureViewCatalogItem(BaseModel):
    name: str
    source: str
    ttl_hours: int
    online: bool
    features: List[str]


class FeatureCatalogResponse(BaseModel):
    entity_name: str
    entity_join_keys: List[str]
    feature_views: List[FeatureViewCatalogItem]


def _parse_iso_datetime_to_utc(dt_str: str) -> datetime:
    normalized = dt_str.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _get_raw_media_bucket_name() -> str:
    """Get MinIO bucket name used by media consumer metadata."""
    return (
        os.getenv("MINIO_RAW_MEDIA_BUCKET")
        or os.getenv("MINIO_BUCKET")
        or "mlops-raw-media"
    )


def _get_media_metadata_uris(minio_service: MinIOService, vehicle_id: str, media_type: str) -> List[str]:
    """List metadata JSON object keys for a vehicle by media type."""
    if media_type not in {"images", "audio"}:
        return []

    bucket = _get_raw_media_bucket_name()
    prefix = f"{media_type}/{vehicle_id}/"
    object_names = minio_service.list_objects(bucket_name=bucket, prefix=prefix)
    return [name for name in object_names if name.endswith(".json")]


def _save_training_dataset(df: pd.DataFrame, output_path: str) -> None:
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if output_path.lower().endswith(".csv"):
        df.to_csv(output_path, index=False)
    else:
        df.to_parquet(output_path, index=False)


def _apply_synthetic_labels(df: pd.DataFrame) -> pd.DataFrame:
    risk_model = RiskModelService()

    risk_scores = []
    risk_levels = []
    for row in df.to_dict(orient="records"):
        score, level = risk_model.calculate_risk_score(row)
        risk_scores.append(score)
        risk_levels.append(level)

    df["risk_score"] = risk_scores
    df["risk_level"] = risk_levels
    df["label_source"] = TRAINING_LABEL_SOURCE
    return df


@router.post("/build", response_model=BuildFeatureResponse)
async def build_features(request: BuildFeatureRequest):
    """Trigger feature engineering job"""
    try:
        feature_builder = get_feature_builder()

        vehicle_id = request.vehicle_id or "V001"

        # Use provided dates or default to last 7 days
        if request.start_date:
            start_time = _parse_iso_datetime_to_utc(request.start_date)
        else:
            # Default: 7 days ago (UTC timezone-aware)
            start_time = datetime.now(timezone.utc) - timedelta(days=DEFAULT_BUILD_LOOKBACK_DAYS)

        if request.end_date:
            end_time = _parse_iso_datetime_to_utc(request.end_date)
        else:
            # Default: now (UTC timezone-aware)
            end_time = datetime.now(timezone.utc)

        logger.info(
            "Build features request: vehicle_id=%s start_time=%s end_time=%s",
            vehicle_id,
            start_time.isoformat(),
            end_time.isoformat(),
        )

        # Build sensor features
        sensor_features = feature_builder.build_sensor_features(
            vehicle_id=vehicle_id,
            start_time=start_time,
            end_time=end_time
        )

        features_built = []
        if sensor_features:
            features_built.append("sensor_features")
            sensor_ts = pd.to_datetime(
                [row.get("event_timestamp") for row in sensor_features],
                errors="coerce",
                utc=True,
            )
            sensor_ts = sensor_ts[sensor_ts.notna()]
            logger.info(
                "Sensor features built: vehicle_id=%s rows=%d ts_min=%s ts_max=%s",
                vehicle_id,
                len(sensor_features),
                sensor_ts.min().isoformat() if len(sensor_ts) > 0 else None,
                sensor_ts.max().isoformat() if len(sensor_ts) > 0 else None,
            )

            # Save to Parquet in MinIO
            prefix = f"sensor_features/{vehicle_id}/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.parquet"
            sensor_saved = feature_builder.save_features_to_parquet(
                sensor_features,
                bucket="mlops-features",
                prefix=prefix
            )
            logger.info(
                "Sensor features saved: vehicle_id=%s success=%s target=%s",
                vehicle_id,
                sensor_saved,
                f"mlops-features/{prefix}",
            )

        # 미구현: raw image 파일을 직접 읽어 CV inference를 돌리는 경로는 아직 없다.
        # 현재는 MinIO metadata JSON 기반의 demo feature만 생성한다.
        minio_service = get_minio_service()
        image_uris = _get_media_metadata_uris(minio_service, vehicle_id, "images")
        logger.info(
            "Image metadata inputs: vehicle_id=%s uri_count=%d",
            vehicle_id,
            len(image_uris),
        )
        image_features = feature_builder.build_image_features(
            vehicle_id=vehicle_id,
            image_uris=image_uris,
            start_time=start_time,
            end_time=end_time,
        )
        if image_features:
            image_ts = pd.to_datetime(
                [row.get("event_timestamp") for row in image_features],
                errors="coerce",
                utc=True,
            )
            image_ts = image_ts[image_ts.notna()]
            logger.info(
                "Image features built: vehicle_id=%s rows=%d ts_min=%s ts_max=%s",
                vehicle_id,
                len(image_features),
                image_ts.min().isoformat() if len(image_ts) > 0 else None,
                image_ts.max().isoformat() if len(image_ts) > 0 else None,
            )
            features_built.append("image_features")
            image_prefix = f"image_features/{vehicle_id}/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.parquet"
            image_saved = feature_builder.save_features_to_parquet(
                image_features,
                bucket="mlops-features",
                prefix=image_prefix
            )
            logger.info(
                "Image features saved: vehicle_id=%s success=%s target=%s",
                vehicle_id,
                image_saved,
                f"mlops-features/{image_prefix}",
            )

        # 미구현: raw audio 파일을 직접 읽어 signal processing / detector inference를 수행하지 않는다.
        # 현재는 MinIO metadata JSON 기반의 demo feature만 생성한다.
        audio_uris = _get_media_metadata_uris(minio_service, vehicle_id, "audio")
        logger.info(
            "Audio metadata inputs: vehicle_id=%s uri_count=%d",
            vehicle_id,
            len(audio_uris),
        )
        audio_features = feature_builder.build_audio_features(
            vehicle_id=vehicle_id,
            audio_uris=audio_uris,
            start_time=start_time,
            end_time=end_time,
        )
        if audio_features:
            audio_ts = pd.to_datetime(
                [row.get("event_timestamp") for row in audio_features],
                errors="coerce",
                utc=True,
            )
            audio_ts = audio_ts[audio_ts.notna()]
            logger.info(
                "Audio features built: vehicle_id=%s rows=%d ts_min=%s ts_max=%s",
                vehicle_id,
                len(audio_features),
                audio_ts.min().isoformat() if len(audio_ts) > 0 else None,
                audio_ts.max().isoformat() if len(audio_ts) > 0 else None,
            )
            features_built.append("audio_features")
            audio_prefix = f"audio_features/{vehicle_id}/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.parquet"
            audio_saved = feature_builder.save_features_to_parquet(
                audio_features,
                bucket="mlops-features",
                prefix=audio_prefix
            )
            logger.info(
                "Audio features saved: vehicle_id=%s success=%s target=%s",
                vehicle_id,
                audio_saved,
                f"mlops-features/{audio_prefix}",
            )

        return BuildFeatureResponse(
            success=True,
            message=f"Feature engineering completed for {vehicle_id}",
            features_built=features_built,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building features: {str(e)}")


@router.get("/catalog", response_model=FeatureCatalogResponse)
async def get_feature_catalog():
    """Get feature view catalog shown in the demo UI."""
    return FeatureCatalogResponse(
        entity_name="vehicle",
        entity_join_keys=["vehicle_id"],
        feature_views=[FeatureViewCatalogItem(**item) for item in get_catalog_items()],
    )


@router.get("/offline", response_model=List[FeatureResponse])
async def get_offline_features(
    vehicle_id: str = Query(..., description="Vehicle ID to query"),
    start_date: Optional[str] = Query(None, description="Start date for feature range (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date for feature range (ISO format)"),
    interval_minutes: int = Query(10, ge=1, le=1440, description="Interval between historical rows in minutes"),
):
    """Get historical features from offline store (DuckDB/Parquet)"""
    try:
        feast_service = get_feast_service()

        # Parse date range if provided
        start_time = None
        end_time = None

        try:
            if start_date:
                start_time = _parse_iso_datetime_to_utc(start_date)

            if end_date:
                end_time = _parse_iso_datetime_to_utc(end_date)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Invalid ISO datetime: {e}") from e

        if start_time and end_time and start_time > end_time:
            raise HTTPException(
                status_code=400,
                detail="start_date must be less than or equal to end_date",
            )

        features = feast_service.get_historical_features(
            vehicle_id=vehicle_id,
            feature_views=DEFAULT_FEATURE_VIEW_NAMES,
            start_time=start_time,
            end_time=end_time,
            interval_minutes=interval_minutes,
            drop_all_null_rows=True,
        )

        if not features:
            logger.info(
                "Offline feature lookup returned no rows: vehicle_id=%s start_date=%s end_date=%s interval_minutes=%s",
                vehicle_id,
                start_date,
                end_date,
                interval_minutes,
            )
            return []

        feature_df = pd.DataFrame(features)
        view_non_null = {
            "sensor_non_null_rows": 0,
            "image_non_null_rows": 0,
            "audio_non_null_rows": 0,
        }
        if not feature_df.empty:
            sensor_cols = [
                "avg_speed_10s",
                "accel_std_10s",
                "obstacle_distance_min",
                "lidar_point_count",
                "sensor_missing_rate",
            ]
            image_cols = ["object_count", "pedestrian_count", "lane_detect_score"]
            audio_cols = ["noise_level", "siren_detected"]

            present_sensor = [col for col in sensor_cols if col in feature_df.columns]
            present_image = [col for col in image_cols if col in feature_df.columns]
            present_audio = [col for col in audio_cols if col in feature_df.columns]

            if present_sensor:
                view_non_null["sensor_non_null_rows"] = int(
                    (~feature_df[present_sensor].isna().all(axis=1)).sum()
                )
            if present_image:
                view_non_null["image_non_null_rows"] = int(
                    (~feature_df[present_image].isna().all(axis=1)).sum()
                )
            if present_audio:
                view_non_null["audio_non_null_rows"] = int(
                    (~feature_df[present_audio].isna().all(axis=1)).sum()
                )

        result = []
        now_utc = datetime.now(timezone.utc)
        for f in features:
            event_timestamp = f.get("event_timestamp")
            timestamp_dt = pd.to_datetime(event_timestamp, errors="coerce", utc=True)
            if pd.isna(timestamp_dt):
                logger.warning(f"Skipping record with invalid event_timestamp: {event_timestamp}")
                continue

            timestamp_py = timestamp_dt.to_pydatetime()
            if timestamp_py > now_utc:
                continue

            timestamp_str = timestamp_py.isoformat()
            feature_row = dict(f)
            feature_row["event_timestamp"] = timestamp_str

            result.append(
                FeatureResponse(
                    vehicle_id=feature_row.get("vehicle_id", vehicle_id),
                    features=feature_row,
                    timestamp=timestamp_str,
                )
            )

        logger.info(
            "Offline feature lookup response rows=%d vehicle_id=%s start_date=%s end_date=%s interval_minutes=%s diagnostics=%s",
            len(result),
            vehicle_id,
            start_date,
            end_date,
            interval_minutes,
            {
                "retrieved_rows": len(features),
                "returned_rows": len(result),
                **view_non_null,
            },
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting offline features for vehicle_id '{vehicle_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error getting offline features: {str(e)}"
        )


@router.post("/training-dataset", response_model=TrainingDatasetResponse)
async def generate_training_dataset(request: TrainingDatasetRequest):
    """Generate training dataset from historical Feast features."""
    try:
        if request.hours <= 0:
            raise HTTPException(status_code=422, detail="hours must be greater than 0")
        if request.interval_minutes <= 0:
            raise HTTPException(
                status_code=422, detail="interval_minutes must be greater than 0"
            )

        vehicle_ids = [vehicle_id for vehicle_id in request.vehicle_ids if vehicle_id]
        if not vehicle_ids:
            vehicle_ids = TRAINING_DEFAULT_VEHICLE_IDS

        feast_service = get_feast_service()
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=request.hours)

        all_rows = []
        for vehicle_id in vehicle_ids:
            rows = feast_service.get_historical_features(
                vehicle_id=vehicle_id,
                feature_views=DEFAULT_FEATURE_VIEW_NAMES,
                start_time=start_time,
                end_time=end_time,
                interval_minutes=request.interval_minutes,
            )
            if not rows:
                logger.warning(
                    "No historical rows returned for training dataset vehicle_id=%s",
                    vehicle_id,
                )
                continue
            all_rows.extend(rows)

        if not all_rows:
            raise HTTPException(
                status_code=500,
                detail="Training dataset generation failed: no historical features found",
            )

        df = pd.DataFrame(all_rows)
        df["event_timestamp"] = pd.to_datetime(
            df["event_timestamp"], errors="coerce", utc=True
        )
        df = df[df["event_timestamp"].notna()]

        for column in TRAINING_FEATURE_COLUMNS:
            if column not in df.columns:
                df[column] = None

        ordered_columns = ["vehicle_id", "event_timestamp"] + TRAINING_FEATURE_COLUMNS
        df = df[ordered_columns]
        df = _apply_synthetic_labels(df)
        _save_training_dataset(df, request.output_path)

        label_distribution = df["risk_level"].value_counts(dropna=False).to_dict()
        return TrainingDatasetResponse(
            success=True,
            message="Training dataset generated successfully",
            output_path=request.output_path,
            row_count=len(df),
            feature_count=len(TRAINING_FEATURE_COLUMNS),
            label_distribution=label_distribution,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating training dataset: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error generating training dataset: {str(e)}"
        )


@router.post("/materialize", response_model=MaterializeResponse)
async def materialize_features(request: Optional[MaterializeRequest] = None):
    """Materialize features to online store (Redis)"""
    try:
        feast_service = get_feast_service()
        end_date = datetime.now(timezone.utc)
        if request and request.end_date:
            end_date = _parse_iso_datetime_to_utc(request.end_date)

        success = feast_service.materialize_incremental(end_date=end_date)

        if success:
            return MaterializeResponse(
                success=True,
                message="Materialization completed successfully",
                end_date=end_date.isoformat().replace("+00:00", "Z"),
                materialized_feature_views=DEFAULT_FEATURE_VIEW_NAMES,
            )
        else:
            raise HTTPException(status_code=500, detail="Materialization failed")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid end_date: {e}") from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error materializing features: {str(e)}")


@router.get("/online", response_model=FeatureResponse)
async def get_online_features(
    vehicle_id: str = Query(..., description="Vehicle ID to query"),
):
    """Get real-time features from online store (Redis)"""
    try:
        feast_service = get_feast_service()

        features = feast_service.get_online_features(vehicle_id=vehicle_id)

        if features is None:
            # Return default features if online store is empty
            features = {
                "avg_speed_10s": 0.0,
                "accel_std_10s": 0.0,
                "obstacle_distance_min": 100.0,
                "lidar_point_count": 0,
                "sensor_missing_rate": 0.0,
            }

        return FeatureResponse(
            vehicle_id=vehicle_id,
            features=features,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting online features: {str(e)}")


@router.get("/status", response_model=FeatureStoreStatusResponse)
async def get_feature_store_status(
    vehicle_id: str = Query("V001", description="Vehicle ID to query for freshness"),
    lookback_hours: int = Query(
        24, ge=1, le=24 * 30, description="Historical lookback window in hours"
    ),
):
    """Get feature store freshness and materialization status."""
    try:
        feast_service = get_feast_service()
        state = feast_service.get_materialization_state()

        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=lookback_hours)
        rows = feast_service.get_historical_features(
            vehicle_id=vehicle_id,
            feature_views=DEFAULT_FEATURE_VIEW_NAMES,
            start_time=start_time,
            end_time=end_time,
            interval_minutes=10,
        )

        latest_timestamp: Optional[datetime] = None
        for row in rows:
            parsed = pd.to_datetime(row.get("event_timestamp"), errors="coerce", utc=True)
            if pd.isna(parsed):
                continue
            ts = parsed.to_pydatetime().astimezone(timezone.utc)
            if latest_timestamp is None or ts > latest_timestamp:
                latest_timestamp = ts

        offline_latest_feature_timestamp = (
            latest_timestamp.isoformat().replace("+00:00", "Z")
            if latest_timestamp is not None
            else None
        )
        offline_feature_age_seconds = (
            int((end_time - latest_timestamp).total_seconds())
            if latest_timestamp is not None
            else None
        )

        online_features = feast_service.get_online_features(vehicle_id=vehicle_id)
        online_feature_available = False
        if isinstance(online_features, dict):
            online_feature_available = any(value is not None for value in online_features.values())

        return FeatureStoreStatusResponse(
            vehicle_id=vehicle_id,
            lookback_hours=lookback_hours,
            last_materialization_end_date=state.get("last_materialization_end_date"),
            offline_latest_feature_timestamp=offline_latest_feature_timestamp,
            offline_feature_age_seconds=offline_feature_age_seconds,
            online_feature_available=online_feature_available,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting feature store status: {str(e)}"
        )
