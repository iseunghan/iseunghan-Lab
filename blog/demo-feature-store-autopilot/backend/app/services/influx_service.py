"""InfluxDB Service for time-series sensor data storage and retrieval."""

import logging
from datetime import datetime, timezone
from typing import Optional

from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class InfluxService:
    """Service for interacting with InfluxDB for time-series data."""

    def __init__(self, url: str, token: str, org: str, bucket: str = 'features'):
        """
        Initialize InfluxDB client.

        Args:
            url: InfluxDB URL (e.g., 'http://localhost:8086')
            token: Authentication token
            org: Organization name
            bucket: Bucket name (default: 'features')
        """
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket

        self._client = InfluxDBClient(url=url, token=token, org=org)
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
        self._query_api = self._client.query_api()

    def write_sensor_data(self, measurement: str, data: dict, tags: dict = None) -> bool:
        """
        Write sensor data to InfluxDB.

        Args:
            measurement: Measurement name (e.g., 'vehicle-sensors')
            data: Dictionary of field values (e.g., {'speed': 50.0, 'acceleration': 2.0})
            tags: Dictionary of tag values (e.g., {'vehicle_id': 'vehicle-1'})

        Returns:
            True on success, False on failure
        """
        try:
            tags = tags or {}
            point = {
                "measurement": measurement,
                "tags": tags,
                "fields": data
            }
            self._write_api.write(bucket=self.bucket, record=point)
            return True
        except Exception:
            return False

    def query_sensor_data(
        self,
        vehicle_id: str,
        limit: int = 10000,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> list:
        """
        Query sensor data for a specific vehicle.

        Args:
            vehicle_id: Vehicle identifier to filter by
            limit: Maximum number of records to return (default: 100)
            start_time: Start time for data retrieval (default: last 1 hour)
            end_time: End time for data retrieval (default: now)

        Returns:
            List of dictionaries containing sensor data records
        """
        try:
            # Build range clause based on time parameters
            # Ensure timezone-aware UTC timestamps for InfluxDB
            if start_time:
                if start_time.tzinfo is None:
                    # If naive datetime, assume UTC and add timezone
                    start_time = start_time.replace(tzinfo=timezone.utc)
                start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
                range_clause = f'start: {start_str}'
            else:
                range_clause = 'start: -1h'  # Default to last hour

            if end_time:
                if end_time.tzinfo is None:
                    # If naive datetime, assume UTC and add timezone
                    end_time = end_time.replace(tzinfo=timezone.utc)
                stop_str = end_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
                range_clause += f', stop: {stop_str}'

            query = f'''
                from(bucket: "{self.bucket}")
                    |> range({range_clause})
                    |> filter(fn: (r) => r["_measurement"] == "vehicle-sensors")
                    |> filter(fn: (r) => r["vehicle_id"] == "{vehicle_id}")
                    |> limit(n: {limit})
            '''
            logger.info(f"Executing InfluxDB query: {query.strip()}")
            result = self._query_api.query(query)
            logger.info(f"Query returned {len(result)} table(s)")

            records = []
            for table in result:
                for record in table.records:
                    # InfluxDB returns records with _field, _value, _time, etc.
                    # Build a clean dictionary from the record
                    record_data = {}
                    for key, value in record.values.items():
                        # Skip internal InfluxDB fields
                        if key.startswith('_') and key not in ['_value', '_field', '_time', '_start', '_stop', '_measurement']:
                            continue
                        # Map _value to the actual field name
                        if key == '_value':
                            # Use values dict to access _field
                            field_name = record.values.get('_field')
                            if field_name:
                                record_data[field_name] = value
                        elif key not in ['_field', '_start', '_stop', '_measurement']:
                            record_data[key] = value
                    if record_data:
                        records.append(record_data)
            return records
        except Exception as e:
            logger.error(f"InfluxDB query error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def get_sensor_count(self) -> int:
        """
        Get total count of sensor records.

        Returns:
            Integer count of sensor records
        """
        try:
            # count() returns count per field (speed, acceleration, etc.)
            # Sum all _value fields to get total record count
            query = f'''
                from(bucket: "{self.bucket}")
                    |> range(start: -1h)
                    |> filter(fn: (r) => r["_measurement"] == "vehicle-sensors")
                    |> count()
            '''
            logger.info(f"Executing sensor count query")
            result = self._query_api.query(query)

            total = 0
            for table in result:
                for record in table.records:
                    value = None
                    if hasattr(record, "values") and isinstance(record.values, dict):
                        value = record.values.get("_value")
                    if value is None:
                        value = getattr(record, "value", 0)
                    try:
                        total += int(value)
                    except (TypeError, ValueError):
                        continue
            logger.info(f"Sensor count: {total}")
            return total
        except Exception as e:
            logger.error(f"InfluxDB count error: {e}")
            return 0

    def close(self):
        """Close the InfluxDB client connection."""
        self._client.close()
