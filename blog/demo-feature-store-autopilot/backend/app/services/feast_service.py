"""Feast Service for feature store operations (online feature retrieval, materialization, historical features)."""

import logging
import json
import os
import io
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import pandas as pd
from feast import FeatureStore
from app.services.minio_service import MinIOService
from app.services.feature_registry import (
    get_catalog_items,
    get_feature_ref_map,
    get_feature_refs,
    get_feature_view_names,
    get_feature_view_spec,
)

logger = logging.getLogger(__name__)
DEFAULT_HISTORICAL_LOOKBACK_HOURS = 24
AUTO_WINDOW_PROBE_DAYS = 30
MAX_ENTITY_ROWS = int(os.getenv("MAX_ENTITY_ROWS", "5000"))


class HistoricalFeatureLookupError(RuntimeError):
    """Raised when Feast historical feature lookup fails."""


class FeastService:
    """Service for interacting with Feast feature store."""

    def __init__(self, repo_path: str = "./feast_repo"):
        """Initialize Feast feature store.

        Args:
            repo_path: Path to Feast repository containing feature_store.yaml
        """
        self.repo_path = repo_path
        self._store = FeatureStore(repo_path=repo_path)
        self._materialization_state_path = (
            Path(repo_path) / "data" / "materialization_state.json"
        )
        feast_data_path = os.getenv("FEAST_DATA_PATH", "s3://mlops-features")
        logger.info(
            "FeastService initialized: repo_path=%s FEAST_DATA_PATH=%s source_patterns=%s",
            repo_path,
            feast_data_path,
            {
                item["name"]: item["source"]
                for item in get_catalog_items(feast_data_path=feast_data_path)
            },
        )

    def _write_materialization_state(self, end_date: datetime) -> None:
        """Persist last successful materialization timestamp for observability."""
        payload = {
            "last_materialization_end_date": end_date.astimezone(timezone.utc).isoformat()
        }
        self._materialization_state_path.parent.mkdir(parents=True, exist_ok=True)
        self._materialization_state_path.write_text(
            json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8"
        )

    def get_materialization_state(self) -> Dict[str, Optional[str]]:
        """Return persisted materialization status."""
        if not self._materialization_state_path.exists():
            return {"last_materialization_end_date": None}

        try:
            payload = json.loads(
                self._materialization_state_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as error:
            logger.warning("Failed to read materialization state: %s", error)
            return {"last_materialization_end_date": None}

        last_end_date = payload.get("last_materialization_end_date")
        if not isinstance(last_end_date, str):
            last_end_date = None

        return {"last_materialization_end_date": last_end_date}

    def _resolve_feature_refs(self, feature_views: List[str]) -> List[str]:
        """Build feature refs in 'feature_view:feature' format."""
        return get_feature_refs(feature_views)

    def _find_latest_feature_timestamp(
        self,
        vehicle_id: str,
        feature_views: List[str],
        end_time: datetime,
        interval_minutes: int,
    ) -> Optional[datetime]:
        """Find latest entity timestamp from real feature-view event timestamps."""
        probe_start = end_time - timedelta(days=AUTO_WINDOW_PROBE_DAYS)
        probe_df = self._build_entity_df_from_feature_views(
            vehicle_id=vehicle_id,
            feature_views=feature_views,
            start_time=probe_start,
            end_time=end_time,
            interval_minutes=interval_minutes,
        )
        if probe_df.empty:
            return None
        latest = probe_df["event_timestamp"].max()
        if pd.isna(latest):
            return None
        return latest.to_pydatetime()

    def _feature_view_source_pattern(self, feature_view: str) -> str:
        spec = get_feature_view_spec(feature_view)
        if spec is None:
            return ""
        return spec.resolve_source_path()

    def _build_minio_service(self) -> MinIOService:
        return MinIOService(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "admin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "admin123"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
        )

    def _parse_s3_path(self, path: str) -> tuple[str, str]:
        normalized = path.replace("s3://", "", 1)
        bucket, _, key = normalized.partition("/")
        return bucket, key

    def _load_view_entity_df(
        self,
        vehicle_id: str,
        feature_view: str,
        start_time: datetime,
        end_time: datetime,
    ) -> pd.DataFrame:
        pattern = self._feature_view_source_pattern(feature_view)
        if not pattern:
            return pd.DataFrame(columns=["vehicle_id", "event_timestamp"])

        if not pattern.startswith("s3://"):
            logger.warning(
                "Unsupported source pattern for entity timeline: feature_view=%s pattern=%s",
                feature_view,
                pattern,
            )
            return pd.DataFrame(columns=["vehicle_id", "event_timestamp"])

        bucket, key_pattern = self._parse_s3_path(pattern)
        prefix = key_pattern.split("*", 1)[0]

        try:
            minio_service = self._build_minio_service()
            object_names = minio_service.list_objects(bucket_name=bucket, prefix=prefix)
        except Exception as error:
            logger.warning(
                "Failed listing feature view parquet objects: vehicle_id=%s feature_view=%s pattern=%s error=%s",
                vehicle_id,
                feature_view,
                pattern,
                error,
            )
            return pd.DataFrame(columns=["vehicle_id", "event_timestamp"])

        parquet_objects = [name for name in object_names if name.endswith(".parquet")]
        if not parquet_objects:
            logger.info(
                "Entity timeline source empty: vehicle_id=%s feature_view=%s bucket=%s prefix=%s objects=0",
                vehicle_id,
                feature_view,
                bucket,
                prefix,
            )
            return pd.DataFrame(columns=["vehicle_id", "event_timestamp"])

        frames: List[pd.DataFrame] = []
        raw_rows = 0
        for object_name in parquet_objects:
            payload = minio_service.get_object_bytes(bucket_name=bucket, object_name=object_name)
            if payload is None:
                continue
            try:
                part_df = pd.read_parquet(
                    io.BytesIO(payload), columns=["vehicle_id", "event_timestamp"]
                )
            except Exception as error:
                logger.warning(
                    "Failed reading parquet object for entity timeline: vehicle_id=%s feature_view=%s object=%s error=%s",
                    vehicle_id,
                    feature_view,
                    object_name,
                    error,
                )
                continue
            if not part_df.empty:
                raw_rows += len(part_df)
                frames.append(part_df)

        if not frames:
            logger.info(
                "Entity timeline parquet read yielded no rows: vehicle_id=%s feature_view=%s bucket=%s prefix=%s parquet_objects=%d",
                vehicle_id,
                feature_view,
                bucket,
                prefix,
                len(parquet_objects),
            )
            return pd.DataFrame(columns=["vehicle_id", "event_timestamp"])

        source_df = pd.concat(frames, ignore_index=True)
        vehicle_filtered_df = source_df[source_df["vehicle_id"] == vehicle_id].copy()
        if vehicle_filtered_df.empty:
            logger.info(
                "Entity timeline vehicle filter empty: vehicle_id=%s feature_view=%s raw_rows=%d parquet_objects=%d",
                vehicle_id,
                feature_view,
                raw_rows,
                len(parquet_objects),
            )
            return pd.DataFrame(columns=["vehicle_id", "event_timestamp"])

        vehicle_filtered_df["event_timestamp"] = pd.to_datetime(
            vehicle_filtered_df["event_timestamp"], errors="coerce", utc=True
        )
        valid_ts_df = vehicle_filtered_df[vehicle_filtered_df["event_timestamp"].notna()].copy()
        window_df = valid_ts_df[
            (valid_ts_df["event_timestamp"] >= start_time)
            & (valid_ts_df["event_timestamp"] <= end_time)
        ].copy()
        logger.info(
            "Entity timeline view stats: vehicle_id=%s feature_view=%s parquet_objects=%d raw_rows=%d vehicle_rows=%d valid_ts_rows=%d window_rows=%d window_start=%s window_end=%s min_ts=%s max_ts=%s",
            vehicle_id,
            feature_view,
            len(parquet_objects),
            raw_rows,
            len(vehicle_filtered_df),
            len(valid_ts_df),
            len(window_df),
            start_time.isoformat(),
            end_time.isoformat(),
            window_df["event_timestamp"].min().isoformat() if not window_df.empty else None,
            window_df["event_timestamp"].max().isoformat() if not window_df.empty else None,
        )
        return window_df[["vehicle_id", "event_timestamp"]]

    def _build_entity_df_from_feature_views(
        self,
        vehicle_id: str,
        feature_views: List[str],
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int,
    ) -> pd.DataFrame:
        union_rows = []
        view_row_counts: Dict[str, int] = {}
        for feature_view in feature_views:
            view_df = self._load_view_entity_df(
                vehicle_id=vehicle_id,
                feature_view=feature_view,
                start_time=start_time,
                end_time=end_time,
            )
            if not view_df.empty:
                union_rows.append(view_df)
            view_row_counts[feature_view] = len(view_df)

        if not union_rows:
            logger.info(
                "Entity timeline union empty: vehicle_id=%s feature_views=%s view_row_counts=%s",
                vehicle_id,
                feature_views,
                view_row_counts,
            )
            return pd.DataFrame(columns=["vehicle_id", "event_timestamp"])

        entity_df = pd.concat(union_rows, ignore_index=True)
        entity_df["event_timestamp"] = pd.to_datetime(
            entity_df["event_timestamp"], errors="coerce", utc=True
        )
        entity_df = entity_df[entity_df["event_timestamp"].notna()].copy()
        entity_df = entity_df.drop_duplicates(subset=["vehicle_id", "event_timestamp"])
        entity_df = entity_df.sort_values("event_timestamp").reset_index(drop=True)
        deduped_count = len(entity_df)

        before_count = len(entity_df)
        reduced = False
        if before_count > MAX_ENTITY_ROWS:
            bucket_minutes = max(1, int(interval_minutes))
            entity_df["_bucket"] = entity_df["event_timestamp"].dt.floor(
                f"{bucket_minutes}min"
            )
            entity_df = (
                entity_df.sort_values("event_timestamp")
                .groupby(["vehicle_id", "_bucket"], as_index=False)
                .tail(1)
                .drop(columns=["_bucket"])
                .sort_values("event_timestamp")
                .reset_index(drop=True)
            )
            reduced = True

        logger.info(
            "Historical entity timeline built: vehicle_id=%s feature_views=%s view_row_counts=%s rows_after_dedup=%d rows_before_downsample=%d rows_after=%d reduced=%s max_rows=%d",
            vehicle_id,
            feature_views,
            view_row_counts,
            deduped_count,
            before_count,
            len(entity_df),
            reduced,
            MAX_ENTITY_ROWS,
        )
        return entity_df

    def get_historical_features(
        self,
        vehicle_id: str,
        feature_views: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval_minutes: int = 60,
        drop_all_null_rows: bool = True,
    ) -> List[Dict]:
        """Get historical features from DuckDB offline store.

        Args:
            vehicle_id: Vehicle identifier
            feature_views: List of feature view names (default: all)
            start_time: Start of time range for historical features
            end_time: End of time range for historical features
            interval_minutes: Step size for entity timestamps in minutes
            drop_all_null_rows: If True, drop rows where all requested feature values are null

        Returns:
            List of feature dictionaries
        """
        try:
            # Default feature views if not specified
            if feature_views is None:
                feature_views = get_feature_view_names()

            feature_refs = self._resolve_feature_refs(feature_views)
            if not feature_refs:
                logger.warning(
                    "No valid feature refs resolved: vehicle_id=%s feature_views=%s",
                    vehicle_id,
                    feature_views,
                )
                return []

            auto_window_requested = start_time is None and end_time is None

            # Set default time range if not provided.
            # For explicit ranges we preserve caller-provided timestamps.
            # For fully automatic mode we avoid flooring so the latest point-in-time
            # can include freshly built rows with second-level timestamps.
            if end_time is None and auto_window_requested:
                end_time = datetime.now(timezone.utc)
            elif end_time is None:
                now_utc = datetime.now(timezone.utc)
                interval_seconds = interval_minutes * 60
                floored_epoch = int(now_utc.timestamp() // interval_seconds) * interval_seconds
                end_time = datetime.fromtimestamp(floored_epoch, tz=timezone.utc)

            if start_time is None:
                start_time = end_time - timedelta(hours=DEFAULT_HISTORICAL_LOOKBACK_HOURS)

            if auto_window_requested:
                latest_ts = self._find_latest_feature_timestamp(
                    vehicle_id=vehicle_id,
                    feature_views=feature_views,
                    end_time=end_time,
                    interval_minutes=interval_minutes,
                )
                if latest_ts is not None:
                    end_time = latest_ts
                    start_time = end_time - timedelta(hours=DEFAULT_HISTORICAL_LOOKBACK_HOURS)
                    logger.info(
                        "Historical lookup auto-window aligned to latest data: vehicle_id=%s start_time=%s end_time=%s lookback_hours=%d",
                        vehicle_id,
                        start_time.isoformat(),
                        end_time.isoformat(),
                        DEFAULT_HISTORICAL_LOOKBACK_HOURS,
                    )
                else:
                    logger.info(
                        "Historical lookup auto-window fallback to default: vehicle_id=%s start_time=%s end_time=%s lookback_hours=%d",
                        vehicle_id,
                        start_time.isoformat(),
                        end_time.isoformat(),
                        DEFAULT_HISTORICAL_LOOKBACK_HOURS,
                    )

            if interval_minutes <= 0:
                raise ValueError("interval_minutes must be greater than 0")

            logger.info(
                "Building historical feature lookup: vehicle_id=%s feature_views=%s start_time=%s end_time=%s interval_minutes=%s",
                vehicle_id,
                feature_views,
                start_time.isoformat(),
                end_time.isoformat(),
                interval_minutes,
            )

            entity_df = self._build_entity_df_from_feature_views(
                vehicle_id=vehicle_id,
                feature_views=feature_views,
                start_time=start_time,
                end_time=end_time,
                interval_minutes=interval_minutes,
            )
            if entity_df.empty:
                logger.info(
                    "Historical feature lookup produced no entity rows: vehicle_id=%s start_time=%s end_time=%s interval_minutes=%s",
                    vehicle_id,
                    start_time.isoformat(),
                    end_time.isoformat(),
                    interval_minutes,
                )
                return []
            logger.info(
                "Historical feature lookup entity rows=%d first=%s last=%s",
                len(entity_df),
                entity_df["event_timestamp"].min().isoformat(),
                entity_df["event_timestamp"].max().isoformat(),
            )

            logger.info(
                "Historical feature lookup feature refs count=%d refs=%s",
                len(feature_refs),
                feature_refs,
            )

            # Get historical features from Feast
            # Returns RetrievalJob which has .to_df() method
            retrieval_job = self._store.get_historical_features(
                entity_df=entity_df,
                features=feature_refs,
            )

            # Get DataFrame from RetrievalJob
            feature_data = retrieval_job.to_df()
            logger.info(
                "Historical feature lookup raw result rows=%d columns=%s isna=%s tail=%s",
                len(feature_data),
                list(feature_data.columns),
                feature_data.isna().sum(),
                feature_data.tail(10),
            )

            if "event_timestamp" in feature_data.columns:
                feature_data["event_timestamp"] = pd.to_datetime(
                    feature_data["event_timestamp"], errors="coerce", utc=True
                )
                feature_data = feature_data[feature_data["event_timestamp"].notna()]
                logger.info(
                    "Historical feature lookup rows after timestamp coercion=%d",
                    len(feature_data),
                )
                feature_data = feature_data[feature_data["event_timestamp"] <= datetime.now(timezone.utc)]
                logger.info(
                    "Historical feature lookup rows after future filter=%d",
                    len(feature_data),
                )

            if drop_all_null_rows and feature_refs and not feature_data.empty:
                feature_columns = [ref.split(":", 1)[1] for ref in feature_refs]
                existing_feature_columns = [
                    col for col in feature_columns if col in feature_data.columns
                ]
                if existing_feature_columns:
                    before_rows = len(feature_data)
                    feature_non_null_counts = (
                        feature_data[existing_feature_columns].notna().sum(axis=1)
                    )
                    all_null_mask = feature_data[existing_feature_columns].isna().all(axis=1)
                    dropped_rows = int(all_null_mask.sum())
                    if dropped_rows > 0:
                        feature_data = feature_data[~all_null_mask].copy()
                    logger.info(
                        "Historical feature lookup null-only filter: before=%d dropped=%d after=%d feature_columns=%s non_null_features_min=%d non_null_features_p50=%d non_null_features_max=%d",
                        before_rows,
                        dropped_rows,
                        len(feature_data),
                        existing_feature_columns,
                        int(feature_non_null_counts.min()) if len(feature_non_null_counts) > 0 else 0,
                        int(feature_non_null_counts.median()) if len(feature_non_null_counts) > 0 else 0,
                        int(feature_non_null_counts.max()) if len(feature_non_null_counts) > 0 else 0,
                    )

            # Reset index to make vehicle_id a column if it's the index
            feature_data = feature_data.reset_index(drop=True)

            # Convert to list of dictionaries
            result = feature_data.to_dict(orient="records")
            logger.info(
                "Retrieved %d historical feature records for vehicle_id=%s",
                len(result),
                vehicle_id,
            )
            return result

        except Exception as e:
            message = (
                "Failed to get historical features: "
                f"vehicle_id={vehicle_id} "
                f"feature_views={feature_views} "
                f"start_time={start_time.isoformat() if start_time else None} "
                f"end_time={end_time.isoformat() if end_time else None} "
                f"interval_minutes={interval_minutes} "
                f"error={e}"
            )
            logger.error(message, exc_info=True)
            raise HistoricalFeatureLookupError(message) from e

    def get_online_features(
        self, vehicle_id: str, features: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Get online features from Redis for a specific vehicle.

        Args:
            vehicle_id: Vehicle identifier to retrieve features for
            features: Optional list of feature names to retrieve.
                    If None, retrieves all features for the entity.

        Returns:
            Dictionary containing feature values, or None if retrieval failed
        """
        try:
            # Canonical online feature refs. Keep one source of truth so callers can
            # pass either short feature names or fully-qualified refs.
            default_feature_refs = get_feature_refs()
            short_to_ref = get_feature_ref_map()

            if features is None:
                feature_refs = default_feature_refs
            else:
                feature_refs = []
                for feature in features:
                    if ":" in feature:
                        feature_refs.append(feature)
                    elif feature in short_to_ref:
                        feature_refs.append(short_to_ref[feature])
                    else:
                        # Preserve unknown feature names to keep behavior backward-compatible.
                        feature_refs.append(feature)

            result = self._store.get_online_features(
                features=feature_refs,
                entity_rows=[{"vehicle_id": vehicle_id}],
            )

            # Convert result to dictionary
            # Handle both mock responses (dict) and real Feast responses (ResultSet)
            if isinstance(result, dict):
                feature_dict = result
            else:
                feature_dict = {}
                data = result.to_dict()
                for key, value in data.items():
                    output_key = key.split(":")[-1] if ":" in key else key
                    # Handle nested structure from Feast response
                    if isinstance(value, list):
                        if len(value) > 0:
                            feature_dict[output_key] = value[0]
                        else:
                            feature_dict[output_key] = None
                    else:
                        feature_dict[output_key] = value

            logger.info(f"Retrieved online features for vehicle_id: {vehicle_id}")
            return feature_dict

        except Exception as e:
            logger.error(f"Failed to get online features for vehicle_id '{vehicle_id}': {e}")
            return None

    def materialize_incremental(
        self, end_date: Optional[datetime] = None
    ) -> bool:
        """Materialize features from offline store to online store (Redis).

        Args:
            end_date: End date for incremental materialization.
                     If None, uses current time.

        Returns:
            True if materialization was successful, False otherwise
        """
        try:
            if end_date is None:
                end_date = datetime.now(timezone.utc)
            elif end_date.tzinfo is None:
                logger.warning(
                    "Naive end_date was provided; treating it as UTC: %s", end_date
                )
                end_date = end_date.replace(tzinfo=timezone.utc)
            else:
                end_date = end_date.astimezone(timezone.utc)

            self._store.materialize_incremental(end_date=end_date)
            self._write_materialization_state(end_date=end_date)
            logger.info(
                f"Materialization completed up to: {end_date}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to materialize features: {e}")
            return False

    def apply(self) -> bool:
        """Apply Feast configuration (register feature views, entities).

        Returns:
            True if apply was successful, False otherwise
        """
        try:
            self._store.apply()
            logger.info("Feast configuration applied successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to apply Feast configuration: {e}")
            return False
