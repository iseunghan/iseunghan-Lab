import os
import uuid
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from app.services import KafkaProducerService

router = APIRouter()
logger = logging.getLogger(__name__)

# Lazy initialization for Kafka producer
_kafka_producer: Optional[KafkaProducerService] = None
BACKFILL_DEFAULT_VEHICLE_IDS = [f"V{index:03d}" for index in range(1, 8)]
BACKFILL_SCENARIOS = [
    "normal",
    "heavy_traffic",
    "pedestrian_nearby",
    "sensor_missing",
    "emergency_vehicle",
]

# Scenario-specific media data templates
MEDIA_DATA_BY_SCENARIO = {
    "normal": {
        "camera_frames": {
            "front": {"objects_detected": 3, "pedestrians": 0, "vehicles": 2, "lane_detected": True, "lane_confidence": 0.90},
            "rear": {"objects_detected": 2, "pedestrians": 0, "vehicles": 1, "lane_detected": True, "lane_confidence": 0.85},
        },
        "audio": {"noise_level_db": 50.0, "siren_detected": False, "horn_detected": False},
    },
    "heavy_traffic": {
        "camera_frames": {
            "front": {"objects_detected": 12, "pedestrians": 1, "vehicles": 8, "lane_detected": True, "lane_confidence": 0.65},
            "rear": {"objects_detected": 8, "pedestrians": 0, "vehicles": 5, "lane_detected": True, "lane_confidence": 0.55},
        },
        "audio": {"noise_level_db": 75.0, "siren_detected": False, "horn_detected": True},
    },
    "pedestrian_nearby": {
        "camera_frames": {
            "front": {"objects_detected": 7, "pedestrians": 4, "vehicles": 2, "lane_detected": True, "lane_confidence": 0.82},
            "rear": {"objects_detected": 3, "pedestrians": 0, "vehicles": 1, "lane_detected": True, "lane_confidence": 0.78},
        },
        "audio": {"noise_level_db": 58.0, "siren_detected": False, "horn_detected": False},
    },
    "sensor_missing": {
        "camera_frames": {
            "front": {"objects_detected": 0, "pedestrians": 0, "vehicles": 0, "lane_detected": False, "lane_confidence": 0.0},
            "rear": {"objects_detected": 0, "pedestrians": 0, "vehicles": 0, "lane_detected": False, "lane_confidence": 0.0},
        },
        "audio": {"noise_level_db": 52.0, "siren_detected": False, "horn_detected": False},
    },
    "emergency_vehicle": {
        "camera_frames": {
            "front": {"objects_detected": 5, "pedestrians": 0, "vehicles": 3, "lane_detected": True, "lane_confidence": 0.88},
            "rear": {"objects_detected": 4, "pedestrians": 0, "vehicles": 2, "lane_detected": True, "lane_confidence": 0.82},
        },
        "audio": {"noise_level_db": 80.0, "siren_detected": True, "horn_detected": False},
    },
}

# Scenario-specific sensor data templates
SENSOR_DATA_BY_SCENARIO = {
    "normal": {
        "speed": 42.0,
        "acceleration": 0.2,
        "obstacle_distance": 65.0,
        "lidar_points": 1300,
    },
    "heavy_traffic": {
        "speed": 18.0,
        "acceleration": -0.8,
        "obstacle_distance": 9.0,
        "lidar_points": 980,
    },
    "pedestrian_nearby": {
        "speed": 24.0,
        "acceleration": -1.8,
        "obstacle_distance": 6.5,
        "lidar_points": 1050,
    },
    "sensor_missing": {
        "speed": 32.0,
        "acceleration": 0.0,
        "obstacle_distance": 22.0,
        "lidar_points": 0,
    },
    "emergency_vehicle": {
        "speed": 55.0,
        "acceleration": -2.5,
        "obstacle_distance": 18.0,
        "lidar_points": 1180,
    },
}


def get_kafka_producer() -> KafkaProducerService:
    """Get or create Kafka producer instance (lazy initialization)."""
    global _kafka_producer
    if _kafka_producer is None:
        broker = os.getenv("KAFKA_BROKER", "localhost:9092")
        _kafka_producer = KafkaProducerService(broker=broker)
    return _kafka_producer


class EventRequest(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle identifier")
    scenario: Optional[str] = Field(None, description="Scenario type")
    timestamp: Optional[str] = Field(
        None, description="Event timestamp (ISO-8601 UTC). If omitted, server uses current UTC time."
    )


class EventResponse(BaseModel):
    success: bool
    vehicle_id: str
    event_id: str
    timestamp: str
    payload: dict


class Backfill24hRequest(BaseModel):
    vehicle_ids: List[str] = Field(default_factory=lambda: BACKFILL_DEFAULT_VEHICLE_IDS.copy())
    interval_minutes: int = Field(10, ge=1, le=1440)
    end_time: Optional[str] = Field(
        None, description="Backfill window end time (ISO-8601 UTC). If omitted, current UTC time is used."
    )


class Backfill24hResponse(BaseModel):
    success: bool
    requested_vehicles: List[str]
    interval_minutes: int
    start_time: str
    end_time: str
    planned_events: int
    published_events: int
    failed_events: int


def _parse_iso_datetime_to_utc(dt_str: str) -> datetime:
    normalized = dt_str.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _build_event_payload(vehicle_id: str, scenario: str, timestamp: datetime) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "vehicle_id": vehicle_id,
        "timestamp": timestamp.isoformat(),
        "scenario": scenario,
        "sensor_data": SENSOR_DATA_BY_SCENARIO.get(scenario, SENSOR_DATA_BY_SCENARIO["normal"]),
        "media_data": MEDIA_DATA_BY_SCENARIO.get(scenario, MEDIA_DATA_BY_SCENARIO["normal"]),
    }


@router.post("/simulate", response_model=EventResponse)
async def simulate_event(request: EventRequest):
    """Generate a vehicle event and publish to Kafka"""
    try:
        scenario = request.scenario or "normal"
        if request.timestamp:
            try:
                event_time = _parse_iso_datetime_to_utc(request.timestamp)
            except ValueError as error:
                raise HTTPException(status_code=422, detail=f"Invalid ISO datetime: {error}") from error
        else:
            event_time = datetime.now(timezone.utc)

        payload = _build_event_payload(
            vehicle_id=request.vehicle_id,
            scenario=scenario,
            timestamp=event_time,
        )

        # Publish to Kafka
        kafka_producer = get_kafka_producer()
        success = kafka_producer.publish("vehicle-events", payload, key=request.vehicle_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to publish event to Kafka")

        return EventResponse(
            success=True,
            vehicle_id=request.vehicle_id,
            event_id=payload["event_id"],
            timestamp=payload["timestamp"],
            payload=payload,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing event: {str(e)}")


@router.post("/backfill-24h", response_model=Backfill24hResponse)
async def backfill_events_24h(request: Optional[Backfill24hRequest] = None):
    """Generate and publish historical events for the last 24 hours."""
    try:
        payload = request or Backfill24hRequest()
        vehicle_ids = [vehicle_id.strip() for vehicle_id in payload.vehicle_ids if vehicle_id.strip()]
        if not vehicle_ids:
            vehicle_ids = BACKFILL_DEFAULT_VEHICLE_IDS.copy()

        if payload.end_time:
            try:
                end_time = _parse_iso_datetime_to_utc(payload.end_time)
            except ValueError as error:
                raise HTTPException(status_code=422, detail=f"Invalid end_time: {error}") from error
        else:
            end_time = datetime.now(timezone.utc)

        start_time = end_time - timedelta(hours=24)
        step = timedelta(minutes=payload.interval_minutes)
        kafka_producer = get_kafka_producer()
        per_vehicle_planned = {
            vehicle_id: 0 for vehicle_id in vehicle_ids
        }
        per_vehicle_published = {
            vehicle_id: 0 for vehicle_id in vehicle_ids
        }
        per_vehicle_failed = {
            vehicle_id: 0 for vehicle_id in vehicle_ids
        }

        planned_events = 0
        published_events = 0
        failed_events = 0
        scenario_index = 0

        event_time = start_time
        while event_time <= end_time:
            for vehicle_id in vehicle_ids:
                scenario = BACKFILL_SCENARIOS[scenario_index % len(BACKFILL_SCENARIOS)]
                scenario_index += 1
                event_payload = _build_event_payload(
                    vehicle_id=vehicle_id,
                    scenario=scenario,
                    timestamp=event_time,
                )
                planned_events += 1
                per_vehicle_planned[vehicle_id] += 1
                success = kafka_producer.publish(
                    "vehicle-events", event_payload, key=vehicle_id
                )
                if success:
                    published_events += 1
                    per_vehicle_published[vehicle_id] += 1
                else:
                    failed_events += 1
                    per_vehicle_failed[vehicle_id] += 1
            event_time += step

        logger.info(
            "Backfill24h summary: vehicles=%s interval_minutes=%d start_time=%s end_time=%s planned=%d published=%d failed=%d per_vehicle_planned=%s per_vehicle_published=%s per_vehicle_failed=%s",
            vehicle_ids,
            payload.interval_minutes,
            start_time.isoformat(),
            end_time.isoformat(),
            planned_events,
            published_events,
            failed_events,
            per_vehicle_planned,
            per_vehicle_published,
            per_vehicle_failed,
        )

        return Backfill24hResponse(
            success=failed_events == 0,
            requested_vehicles=vehicle_ids,
            interval_minutes=payload.interval_minutes,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            planned_events=planned_events,
            published_events=published_events,
            failed_events=failed_events,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating backfill events: {str(e)}")
