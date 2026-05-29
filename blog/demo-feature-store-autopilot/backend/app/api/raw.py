import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services import InfluxService, MinIOService

router = APIRouter()

# Lazy initialization for services
_influx_service: Optional[InfluxService] = None
_minio_service: Optional[MinIOService] = None


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


class RawDataStatus(BaseModel):
    influx_sensor_count: int
    minio_image_count: int
    minio_audio_count: int


@router.get("/status", response_model=RawDataStatus)
async def get_raw_data_status():
    """Get status of raw data storage"""
    try:
        # Get actual counts from InfluxDB and MinIO
        influx_service = get_influx_service()
        minio_service = get_minio_service()

        influx_count = influx_service.get_sensor_count()
        image_count = minio_service.get_object_count("mlops-raw-media", prefix="images/")
        audio_count = minio_service.get_object_count("mlops-raw-media", prefix="audio/")

        return RawDataStatus(
            influx_sensor_count=influx_count,
            minio_image_count=image_count,
            minio_audio_count=audio_count,
        )
    except Exception as e:
        # Return zeros on error to avoid breaking the API
        return RawDataStatus(
            influx_sensor_count=0,
            minio_image_count=0,
            minio_audio_count=0,
        )
