from feast import Entity
from feast.value_type import ValueType

# Simple entity for demo - starts with single vehicle_id
# Can be extended to drive_session_id, sensor_id, camera_id later
vehicle = Entity(
    name="vehicle",
    join_keys=["vehicle_id"],
    description="Vehicle entity for feature serving",
    value_type=ValueType.STRING,
)
