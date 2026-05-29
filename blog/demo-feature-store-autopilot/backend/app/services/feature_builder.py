"""Feature Builder Service for feature engineering."""

import logging
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from app.services.influx_service import InfluxService
from app.services.minio_service import MinIOService

logger = logging.getLogger(__name__)


class FeatureBuilderService:
    """Service for building features from raw sensor/media data."""

    def __init__(self, influx_service: InfluxService, minio_service: MinIOService):
        """
        Initialize FeatureBuilderService.

        Args:
            influx_service: InfluxService instance for querying raw sensor data
            minio_service: MinIOService instance for storing feature Parquet files
        """
        self._influx_service = influx_service
        self._minio_service = minio_service

    def build_sensor_features(
        self,
        vehicle_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Build sensor features from InfluxDB data.

        Computes aggregated features from raw sensor data:
        - avg_speed_10s: Average speed over 10-second window
        - accel_std_10s: Standard deviation of acceleration over 10-second window
        - obstacle_distance_min: Minimum obstacle distance in window
        - lidar_point_count: Total lidar point count in window
        - sensor_missing_rate: Rate of missing sensor data

        Args:
            vehicle_id: Vehicle identifier
            start_time: Start time for data retrieval
            end_time: End time for data retrieval

        Returns:
            List of dictionaries containing computed features
        """
        logger.info(f"Building sensor features for vehicle {vehicle_id}")

        # Query raw sensor data from InfluxDB
        raw_data = self._influx_service.query_sensor_data(
            vehicle_id=vehicle_id,
            limit=1000,
            start_time=start_time,
            end_time=end_time
        )

        if not raw_data:
            logger.warning(f"No sensor data found for vehicle {vehicle_id}")
            return []

        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(raw_data)

        # InfluxDB returns _time field, map it to timestamp for consistency
        if '_time' in df.columns:
            df['timestamp'] = df['_time']
        elif 'timestamp' not in df.columns:
            # Fallback to current time if no timestamp field exists
            df['timestamp'] = pd.Timestamp.now(timezone.utc)

        # Group by time windows (10-second intervals) and compute features
        df['time_window'] = pd.to_datetime(df['timestamp'], utc=True).dt.floor('10s')
        grouped = df.groupby('time_window')

        features = []
        for window_time, group in grouped:
            # Calculate obstacle_distance_min with safe default (0.0 instead of inf)
            obstacle_min = group['obstacle_distance'].min() if 'obstacle_distance' in group.columns else None
            obstacle_distance_value = float(obstacle_min) if obstacle_min is not None else 0.0

            feature = {
                "vehicle_id": vehicle_id,
                "event_timestamp": window_time.isoformat(),
                "avg_speed_10s": group['speed'].mean() if 'speed' in group.columns else 0.0,
                "accel_std_10s": group['acceleration'].std() if 'acceleration' in group.columns else 0.0,
                "obstacle_distance_min": obstacle_distance_value,
                "lidar_point_count": group['lidar_points'].sum() if 'lidar_points' in group.columns else 0,
                "sensor_missing_rate": self._calculate_missing_rate(group)
            }
            features.append(self._sanitize_sensor_feature(feature))

        logger.info(f"Built {len(features)} sensor feature windows for vehicle {vehicle_id}")
        return features

    def _calculate_missing_rate(self, df: pd.DataFrame) -> float:
        """
        Calculate the rate of missing sensor data.

        Args:
            df: DataFrame with sensor data

        Returns:
            Float between 0 and 1 representing missing data rate
        """
        if df.empty:
            return 1.0

        sensor_columns = ['speed', 'acceleration', 'obstacle_distance', 'lidar_points']
        # Treat columns that are entirely null in this window as "not present".
        available_columns = [
            col for col in sensor_columns
            if col in df.columns and not df[col].isnull().all()
        ]

        if not available_columns:
            return 1.0

        total_cells = len(df) * len(available_columns)
        missing_cells = df[available_columns].isnull().sum().sum()

        return float(missing_cells / total_cells) if total_cells > 0 else 1.0

    def _to_float(self, value: Any, default: float) -> float:
        """Best-effort float parsing with a safe default."""
        try:
            if pd.isna(value):
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _to_int(self, value: Any, default: int) -> int:
        """Best-effort int parsing with a safe default."""
        try:
            if pd.isna(value):
                return default
            return int(value)
        except (TypeError, ValueError):
            return default

    def _sanitize_sensor_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize feature values to expected domains and log corrections."""
        sanitized = dict(feature)
        corrections: List[str] = []

        avg_speed = self._to_float(sanitized.get("avg_speed_10s"), 0.0)
        if avg_speed < 0:
            corrections.append(f"avg_speed_10s={avg_speed} -> 0.0")
            avg_speed = 0.0
        sanitized["avg_speed_10s"] = avg_speed

        accel_std = self._to_float(sanitized.get("accel_std_10s"), 0.0)
        if accel_std < 0:
            corrections.append(f"accel_std_10s={accel_std} -> 0.0")
            accel_std = 0.0
        sanitized["accel_std_10s"] = accel_std

        obstacle_distance = self._to_float(sanitized.get("obstacle_distance_min"), 0.0)
        if obstacle_distance < 0:
            corrections.append(f"obstacle_distance_min={obstacle_distance} -> 0.0")
            obstacle_distance = 0.0
        sanitized["obstacle_distance_min"] = obstacle_distance

        lidar_points = self._to_int(sanitized.get("lidar_point_count"), 0)
        if lidar_points < 0:
            corrections.append(f"lidar_point_count={lidar_points} -> 0")
            lidar_points = 0
        sanitized["lidar_point_count"] = lidar_points

        missing_rate = self._to_float(sanitized.get("sensor_missing_rate"), 1.0)
        clamped_missing_rate = min(max(missing_rate, 0.0), 1.0)
        if clamped_missing_rate != missing_rate:
            corrections.append(
                f"sensor_missing_rate={missing_rate} -> {clamped_missing_rate}"
            )
        sanitized["sensor_missing_rate"] = clamped_missing_rate

        if corrections:
            logger.warning(
                "Sensor feature corrected for vehicle_id=%s at %s: %s",
                sanitized.get("vehicle_id"),
                sanitized.get("event_timestamp"),
                "; ".join(corrections),
            )

        return sanitized

    def _load_media_metadata(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """
        Load media metadata JSON from MinIO.

        Attempts to find metadata JSON file for the given vehicle.
        Expected path format: media_metadata/{vehicle_id}/metadata.json

        Args:
            vehicle_id: Vehicle identifier

        Returns:
            Parsed metadata dictionary, or None if not found
        """
        # Try common metadata path patterns
        possible_paths = [
            f"media_metadata/{vehicle_id}/metadata.json",
            f"metadata/{vehicle_id}/metadata.json",
            f"{vehicle_id}/metadata.json",
            f"media/{vehicle_id}/metadata.json"
        ]

        for path in possible_paths:
            metadata = self._minio_service.get_object_as_json(
                bucket_name="mlops-features",
                object_name=path
            )
            if metadata:
                logger.info(f"Loaded metadata from {path}")
                return metadata

        logger.warning(f"No metadata JSON found for vehicle {vehicle_id} in any expected path")
        return None

    def build_image_features(
        self,
        vehicle_id: str,
        image_uris: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Build image features from media metadata.

        This is a demo path, not a true raw-image feature pipeline.
        Unimplemented pieces:
        - raw image decoding / preprocessing
        - object detection / segmentation / lane inference
        - model output normalization into the feature schema

        Current behavior:
        - read metadata JSON from MinIO and extract already-available values
        - fall back to a mock row when metadata cannot be read

        Args:
            vehicle_id: Vehicle identifier
            image_uris: List of image URIs to process

        Returns:
            List of dictionaries containing computed features
        """
        logger.info(f"Building image features for vehicle {vehicle_id}")

        features = []

        # Demo path: build one row per readable metadata JSON.
        if image_uris:
            metadata_found = False
            for uri in image_uris:
                # Extract filename from URI for metadata lookup
                try:
                    filename = uri.split("/")[-1]
                    metadata = self._load_metadata_for_uri_or_file(uri)

                    if metadata:
                        metadata_found = True
                        feature = self._extract_image_features_from_metadata(
                            vehicle_id=vehicle_id,
                            uri=uri,
                            metadata=metadata
                        )
                        features.append(feature)
                        logger.debug(f"Built feature from metadata for {filename}")
                except Exception as e:
                    logger.warning(f"Error processing {uri}: {e}")

            if features:
                features = self._filter_records_by_time_range(features, start_time, end_time)
            elif not metadata_found:
                # No raw-image pipeline exists yet, so missing metadata falls back to mock data.
                features = [self._create_mock_image_feature(vehicle_id, "mock_image")]
                logger.debug("Built mock image feature (metadata not found)")
        else:
            # No URIs provided - generate default mock feature.
            features.append(self._create_mock_image_feature(vehicle_id, "mock_image"))
            logger.info(f"Built default mock image feature for vehicle {vehicle_id}")

        logger.info(f"Built {len(features)} image feature rows for vehicle {vehicle_id}")
        return features

    def _extract_event_timestamp(self, metadata: Dict[str, Any]) -> datetime:
        """Extract event timestamp from metadata and normalize to 10-second UTC buckets."""
        ts_value = metadata.get("timestamp")
        parsed: Optional[datetime] = None
        if isinstance(ts_value, str):
            try:
                parsed = datetime.fromisoformat(ts_value.replace("Z", "+00:00")).astimezone(timezone.utc)
            except ValueError:
                parsed = None

        if parsed is None:
            parsed = datetime.now(timezone.utc)

        # Align media timestamps to the same 10-second bucket granularity as sensor features.
        normalized = pd.Timestamp(parsed).floor("10s")
        return normalized.to_pydatetime().astimezone(timezone.utc)

    def _filter_records_by_time_range(
        self,
        records: List[Dict[str, Any]],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        """Keep records within [start_time, end_time] in UTC when bounds are provided."""
        if not records:
            return records

        normalized_start = pd.to_datetime(start_time, utc=True) if start_time else None
        normalized_end = pd.to_datetime(end_time, utc=True) if end_time else None

        filtered: List[Dict[str, Any]] = []
        for record in records:
            parsed = pd.to_datetime(record.get("event_timestamp"), errors="coerce", utc=True)
            if pd.isna(parsed):
                continue
            if normalized_start is not None and parsed < normalized_start:
                continue
            if normalized_end is not None and parsed > normalized_end:
                continue
            filtered.append(record)

        return filtered

    def _load_metadata_for_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load metadata JSON for a given filename.

        Tries multiple bucket/path combinations to find the metadata.

        Args:
            filename: The metadata filename (e.g., "frame_001.json")

        Returns:
            Parsed metadata dictionary, or None if not found
        """
        # Try different bucket and path combinations
        locations = [
            ("mlops-features", f"media_metadata/{filename}"),
            ("mlops-features", filename),
            ("mlops-raw-media", f"metadata/{filename}"),
            ("mlops-raw-media", filename),
        ]

        for bucket, path in locations:
            metadata = self._minio_service.get_object_as_json(bucket, path)
            if metadata:
                logger.debug(f"Loaded metadata from {bucket}/{path}")
                return metadata

        return None

    def _load_metadata_for_uri_or_file(self, uri: str) -> Optional[Dict[str, Any]]:
        """Load metadata JSON from full object key first, then filename fallback."""
        if not uri:
            return None

        exact_locations = [
            ("mlops-raw-media", uri),
            ("mlops-features", uri),
        ]
        for bucket, path in exact_locations:
            metadata = self._minio_service.get_object_as_json(bucket, path)
            if metadata:
                logger.debug(f"Loaded metadata from {bucket}/{path}")
                return metadata

        filename = uri.split("/")[-1]
        return self._load_metadata_for_file(filename)

    def _extract_image_features_from_metadata(self, vehicle_id: str, uri: str, metadata: Dict[str, Any]) -> Dict:
        """
        Extract demo image features from metadata JSON.

        Unimplemented raw-image flow:
        - image file read from MinIO
        - decode / preprocess
        - CV inference
        - feature schema normalization

        Handles multiple metadata formats:
        1. camera_frames format: {"camera_frames": {"front": {...}}}
        2. Per-frame format: {"detected_objects": [...], "lane_detection": {...}}

        Args:
            vehicle_id: Vehicle identifier
            uri: Image URI
            metadata: Parsed metadata JSON

        Returns:
            Feature dictionary with extracted values
        """
        event_dt = self._extract_event_timestamp(metadata)

        # Check if this is camera_frames format (aggregated)
        if 'camera_frames' in metadata:
            camera_frames = metadata['camera_frames']
            if isinstance(camera_frames, dict) and camera_frames:
                object_count = 0
                pedestrian_count = 0
                lane_scores: List[float] = []
                for frame_data in camera_frames.values():
                    if not isinstance(frame_data, dict):
                        continue
                    object_count += int(frame_data.get('objects_detected', 0) or 0)
                    pedestrian_count += int(frame_data.get('pedestrians', 0) or 0)
                    lane_scores.append(float(frame_data.get('lane_confidence', 0.0) or 0.0))

                lane_detect_score = float(sum(lane_scores) / len(lane_scores)) if lane_scores else 0.0
                return {
                    "vehicle_id": vehicle_id,
                    "image_uri": uri,
                    "event_timestamp": event_dt.isoformat(),
                    "object_count": object_count,
                    "pedestrian_count": pedestrian_count,
                    "lane_detect_score": lane_detect_score
                }

        # Per-frame format
        detected_objects = metadata.get('detected_objects', [])
        object_count = len(detected_objects)
        pedestrian_count = sum(1 for obj in detected_objects if obj.get('class') == 'pedestrian')

        # Get lane confidence from various possible locations
        lane_detect_score = 0.0
        if 'lane_detection' in metadata:
            lane_detect_score = metadata['lane_detection'].get('confidence', 0.0)
        elif 'lane_confidence' in metadata:
            lane_detect_score = metadata['lane_confidence']

        return {
            "vehicle_id": vehicle_id,
            "image_uri": uri,
            "event_timestamp": event_dt.isoformat(),
            "object_count": object_count,
            "pedestrian_count": pedestrian_count,
            "lane_detect_score": lane_detect_score
        }

    def _create_mock_image_feature(self, vehicle_id: str, uri: str) -> Dict:
        """Create a mock image feature for fallback."""
        return {
            "vehicle_id": vehicle_id,
            "image_uri": uri,
            "event_timestamp": datetime.now(timezone.utc).isoformat(),
            "object_count": 5,
            "pedestrian_count": 2,
            "lane_detect_score": 0.85
        }

    def build_audio_features(
        self,
        vehicle_id: str,
        audio_uris: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Build audio features from media metadata.

        This is a demo path, not a true raw-audio feature pipeline.
        Unimplemented pieces:
        - raw audio decoding / resampling
        - spectral feature extraction (MFCC, STFT, etc.)
        - siren detector inference
        - model output normalization into the feature schema

        Current behavior:
        - read metadata JSON from MinIO and extract already-available values
        - fall back to a mock row when metadata cannot be read

        Args:
            vehicle_id: Vehicle identifier
            audio_uris: List of audio URIs to process

        Returns:
            List of dictionaries containing computed features
        """
        logger.info(f"Building audio features for vehicle {vehicle_id}")

        features = []

        # Demo path: build one row per readable metadata JSON.
        if audio_uris:
            metadata_found = False
            for uri in audio_uris:
                # Extract filename from URI for metadata lookup
                try:
                    filename = uri.split("/")[-1]
                    metadata = self._load_metadata_for_uri_or_file(uri)

                    if metadata:
                        metadata_found = True
                        feature = self._extract_audio_features_from_metadata(
                            vehicle_id=vehicle_id,
                            uri=uri,
                            metadata=metadata
                        )
                        features.append(feature)
                        logger.debug(f"Built audio feature from metadata for {filename}")
                except Exception as e:
                    logger.warning(f"Error processing {uri}: {e}")

            if features:
                features = self._filter_records_by_time_range(features, start_time, end_time)
            elif not metadata_found:
                # No raw-audio pipeline exists yet, so missing metadata falls back to mock data.
                features = [self._create_mock_audio_feature(vehicle_id, "mock_audio")]
                logger.debug("Built mock audio feature (metadata not found)")
        else:
            # No URIs provided - generate default mock feature.
            features.append(self._create_mock_audio_feature(vehicle_id, "mock_audio"))
            logger.info(f"Built default mock audio feature for vehicle {vehicle_id}")

        logger.info(f"Built {len(features)} audio feature rows for vehicle {vehicle_id}")
        return features

    def _extract_audio_features_from_metadata(self, vehicle_id: str, uri: str, metadata: Dict[str, Any]) -> Dict:
        """
        Extract demo audio features from metadata JSON.

        Unimplemented raw-audio flow:
        - waveform decode
        - signal processing / spectral features
        - siren detector inference
        - feature schema normalization

        Args:
            vehicle_id: Vehicle identifier
            uri: Audio URI
            metadata: Parsed metadata JSON

        Returns:
            Feature dictionary with extracted values
        """
        # Support both flattened audio metadata and media-consumer format.
        audio_block = metadata.get("audio", {}) if isinstance(metadata.get("audio"), dict) else {}

        # Get noise level from known fields.
        noise_level = metadata.get("noise_level")
        if noise_level is None:
            noise_level = audio_block.get("noise_level")
        if noise_level is None:
            noise_level = audio_block.get("noise_level_db", 0.0)

        # Check if siren was detected.
        events = metadata.get("events_detected", [])
        siren_detected = any(event.get("class") == "siren" for event in events)
        if not siren_detected:
            siren_detected = bool(audio_block.get("siren_detected", False))

        event_dt = self._extract_event_timestamp(metadata)

        return {
            "vehicle_id": vehicle_id,
            "audio_uri": uri,
            "event_timestamp": event_dt.isoformat(),
            "noise_level": noise_level,
            "siren_detected": siren_detected
        }

    def _create_mock_audio_feature(self, vehicle_id: str, uri: str) -> Dict:
        """Create a mock audio feature for fallback."""
        return {
            "vehicle_id": vehicle_id,
            "audio_uri": uri,
            "event_timestamp": datetime.now(timezone.utc).isoformat(),
            "noise_level": 65.0,
            "siren_detected": False
        }

    def save_features_to_parquet(
        self,
        features: List[Dict],
        bucket: str,
        prefix: str
    ) -> bool:
        """
        Save features as Parquet file to MinIO.

        Args:
            features: List of feature dictionaries to save
            bucket: Target MinIO bucket name
            prefix: Object key prefix (e.g., 'sensor_features/vehicle-1/2026-05-21.parquet')

        Returns:
            True if save was successful, False otherwise
        """
        if not features:
            logger.warning("No features to save")
            return False

        try:
            # Convert to DataFrame
            df = pd.DataFrame(features)
            if "event_timestamp" in df.columns:
                df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], errors="coerce", utc=True)
                df = df[df["event_timestamp"].notna()].copy()
                if df.empty:
                    logger.warning("All feature rows had invalid event_timestamp")
                    return False

            # Ensure bucket exists
            self._minio_service.create_bucket(bucket)

            # Convert DataFrame to Parquet bytes
            table = pa.Table.from_pandas(df)
            parquet_buffer = io.BytesIO()
            pq.write_table(table, parquet_buffer)
            parquet_bytes = parquet_buffer.getvalue()

            # Upload to MinIO
            success = self._minio_service.upload_bytes(
                bucket_name=bucket,
                object_name=prefix,
                data=parquet_bytes,
                content_type="application/octet-stream"
            )

            if success:
                logger.info(f"Saved {len(df)} feature rows to {bucket}/{prefix}")
            else:
                logger.error(f"Failed to save features to {bucket}/{prefix}")

            return success

        except Exception as e:
            logger.error(f"Error saving features to parquet: {e}")
            return False
