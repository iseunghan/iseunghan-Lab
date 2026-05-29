#!/usr/bin/env python3
"""
Vehicle Event Simulator for MLOps Feature Store Demo

Generates mock vehicle events for different scenarios to feed into the
Kafka pipeline for feature store processing.
"""

import json
import random
import argparse
from datetime import datetime, timedelta, timezone
from typing import Optional


class VehicleEventSimulator:
    """Generates vehicle sensor and media events for different driving scenarios."""

    def __init__(self, vehicle_id: str):
        """Initialize the simulator with a vehicle ID.

        Args:
            vehicle_id: Unique identifier for the vehicle
        """
        self.vehicle_id = vehicle_id
        self.base_time = datetime.now(timezone.utc)

    def _generate_base_event(self) -> dict:
        """Generate base event structure."""
        return {
            "vehicle_id": self.vehicle_id,
            "timestamp": self.base_time.isoformat(),
            "event_id": f"{self.vehicle_id}-{int(self.base_time.timestamp() * 1000)}",
        }

    def generate_event(self, scenario: str) -> dict:
        """Generate an event for the specified scenario.

        Args:
            scenario: One of: normal, heavy_traffic, pedestrian_nearby,
                     sensor_missing, emergency_vehicle

        Returns:
            dict: Complete event payload with sensor and media data
        """
        event = self._generate_base_event()
        event["scenario"] = scenario

        if scenario == "normal":
            event.update(self._generate_normal_scenario())
        elif scenario == "heavy_traffic":
            event.update(self._generate_heavy_traffic_scenario())
        elif scenario == "pedestrian_nearby":
            event.update(self._generate_pedestrian_nearby_scenario())
        elif scenario == "sensor_missing":
            event.update(self._generate_sensor_missing_scenario())
        elif scenario == "emergency_vehicle":
            event.update(self._generate_emergency_vehicle_scenario())
        else:
            raise ValueError(f"Unknown scenario: {scenario}")

        return event

    def _generate_normal_scenario(self) -> dict:
        """Generate normal driving conditions."""
        return {
            "sensor_data": {
                "speed_kmh": random.uniform(30, 50),
                "acceleration_mps2": random.uniform(-0.5, 0.5),
                "obstacle_distance_m": random.uniform(50, 100),
                "lidar_points": random.randint(1000, 1500),
                "gps": {
                    "latitude": random.uniform(37.4, 37.5),
                    "longitude": random.uniform(-122.1, -122.0),
                    "accuracy_m": random.uniform(1, 3),
                },
                "sensor_status": {
                    "lidar": "active",
                    "camera": "active",
                    "radar": "active",
                    "ultrasonic": "active",
                },
                "missing_sensors": [],
            },
            "media_data": {
                "camera_frames": {
                    "front": {
                        "objects_detected": random.randint(2, 5),
                        "pedestrians": 0,
                        "vehicles": random.randint(1, 3),
                        "lane_detected": True,
                        "lane_confidence": random.uniform(0.85, 0.95),
                    },
                    "rear": {
                        "objects_detected": random.randint(1, 3),
                        "pedestrians": 0,
                        "vehicles": random.randint(0, 2),
                        "lane_detected": True,
                        "lane_confidence": random.uniform(0.8, 0.9),
                    },
                },
                "audio": {
                    "noise_level_db": random.uniform(45, 55),
                    "siren_detected": False,
                    "horn_detected": False,
                },
            },
            "context": {
                "location_type": "highway",
                "weather": "clear",
                "time_of_day": "day",
                "traffic_density": "low",
            },
        }

    def _generate_heavy_traffic_scenario(self) -> dict:
        """Generate heavy traffic conditions."""
        return {
            "sensor_data": {
                "speed_kmh": random.uniform(10, 25),
                "acceleration_mps2": random.uniform(-2, 1),
                "obstacle_distance_m": random.uniform(5, 15),
                "lidar_points": random.randint(800, 1200),
                "gps": {
                    "latitude": random.uniform(37.4, 37.5),
                    "longitude": random.uniform(-122.1, -122.0),
                    "accuracy_m": random.uniform(2, 5),
                },
                "sensor_status": {
                    "lidar": "active",
                    "camera": "active",
                    "radar": "active",
                    "ultrasonic": "active",
                },
                "missing_sensors": [],
            },
            "media_data": {
                "camera_frames": {
                    "front": {
                        "objects_detected": random.randint(8, 15),
                        "pedestrians": random.randint(0, 2),
                        "vehicles": random.randint(5, 10),
                        "lane_detected": random.choice([True, False]),
                        "lane_confidence": random.uniform(0.5, 0.8),
                    },
                    "rear": {
                        "objects_detected": random.randint(5, 10),
                        "pedestrians": 0,
                        "vehicles": random.randint(3, 7),
                        "lane_detected": random.choice([True, False]),
                        "lane_confidence": random.uniform(0.4, 0.7),
                    },
                },
                "audio": {
                    "noise_level_db": random.uniform(65, 80),
                    "siren_detected": False,
                    "horn_detected": random.choice([True, False]),
                },
            },
            "context": {
                "location_type": "urban",
                "weather": "clear",
                "time_of_day": "rush_hour",
                "traffic_density": "high",
            },
        }

    def _generate_pedestrian_nearby_scenario(self) -> dict:
        """Generate scenario with pedestrians nearby."""
        return {
            "sensor_data": {
                "speed_kmh": random.uniform(15, 30),
                "acceleration_mps2": random.uniform(-3, 0.5),
                "obstacle_distance_m": random.uniform(3, 10),
                "lidar_points": random.randint(900, 1300),
                "gps": {
                    "latitude": random.uniform(37.4, 37.5),
                    "longitude": random.uniform(-122.1, -122.0),
                    "accuracy_m": random.uniform(1, 3),
                },
                "sensor_status": {
                    "lidar": "active",
                    "camera": "active",
                    "radar": "active",
                    "ultrasonic": "active",
                },
                "missing_sensors": [],
            },
            "media_data": {
                "camera_frames": {
                    "front": {
                        "objects_detected": random.randint(5, 10),
                        "pedestrians": random.randint(2, 5),
                        "vehicles": random.randint(1, 3),
                        "lane_detected": True,
                        "lane_confidence": random.uniform(0.75, 0.9),
                    },
                    "rear": {
                        "objects_detected": random.randint(2, 5),
                        "pedestrians": random.randint(0, 1),
                        "vehicles": random.randint(0, 2),
                        "lane_detected": True,
                        "lane_confidence": random.uniform(0.7, 0.85),
                    },
                },
                "audio": {
                    "noise_level_db": random.uniform(50, 65),
                    "siren_detected": False,
                    "horn_detected": False,
                },
            },
            "context": {
                "location_type": "crosswalk",
                "weather": "clear",
                "time_of_day": "day",
                "traffic_density": "medium",
            },
        }

    def _generate_sensor_missing_scenario(self) -> dict:
        """Generate scenario with missing/failing sensors."""
        missing_sensor = random.choice(["lidar", "camera", "radar", "ultrasonic"])

        sensor_status = {
            "lidar": "active" if missing_sensor != "lidar" else "failed",
            "camera": "active" if missing_sensor != "camera" else "failed",
            "radar": "active" if missing_sensor != "radar" else "failed",
            "ultrasonic": "active" if missing_sensor != "ultrasonic" else "failed",
        }

        lidar_points = 0 if missing_sensor == "lidar" else random.randint(500, 1000)

        return {
            "sensor_data": {
                "speed_kmh": random.uniform(20, 40),
                "acceleration_mps2": random.uniform(-1.5, 1),
                "obstacle_distance_m": random.uniform(10, 30) if missing_sensor != "radar" else None,
                "lidar_points": lidar_points,
                "gps": {
                    "latitude": random.uniform(37.4, 37.5),
                    "longitude": random.uniform(-122.1, -122.0),
                    "accuracy_m": random.uniform(3, 8),
                },
                "sensor_status": sensor_status,
                "missing_sensors": [missing_sensor],
            },
            "media_data": {
                "camera_frames": {
                    "front": {
                        "objects_detected": 0 if missing_sensor == "camera" else random.randint(3, 7),
                        "pedestrians": 0,
                        "vehicles": 0 if missing_sensor == "camera" else random.randint(1, 4),
                        "lane_detected": False if missing_sensor == "camera" else random.choice([True, False]),
                        "lane_confidence": 0.0 if missing_sensor == "camera" else random.uniform(0.5, 0.85),
                    },
                    "rear": {
                        "objects_detected": 0 if missing_sensor == "camera" else random.randint(1, 4),
                        "pedestrians": 0,
                        "vehicles": 0 if missing_sensor == "camera" else random.randint(0, 2),
                        "lane_detected": False if missing_sensor == "camera" else random.choice([True, False]),
                        "lane_confidence": 0.0 if missing_sensor == "camera" else random.uniform(0.4, 0.75),
                    },
                },
                "audio": {
                    "noise_level_db": random.uniform(45, 60),
                    "siren_detected": False,
                    "horn_detected": False,
                },
            },
            "context": {
                "location_type": "highway",
                "weather": "clear",
                "time_of_day": "day",
                "traffic_density": "low",
                "warning": f"Sensor failure detected: {missing_sensor}",
            },
        }

    def _generate_emergency_vehicle_scenario(self) -> dict:
        """Generate scenario with emergency vehicle approaching."""
        return {
            "sensor_data": {
                "speed_kmh": random.uniform(40, 60),
                "acceleration_mps2": random.uniform(-4, -1),  # Braking
                "obstacle_distance_m": random.uniform(20, 40),
                "lidar_points": random.randint(1000, 1400),
                "gps": {
                    "latitude": random.uniform(37.4, 37.5),
                    "longitude": random.uniform(-122.1, -122.0),
                    "accuracy_m": random.uniform(1, 3),
                },
                "sensor_status": {
                    "lidar": "active",
                    "camera": "active",
                    "radar": "active",
                    "ultrasonic": "active",
                },
                "missing_sensors": [],
            },
            "media_data": {
                "camera_frames": {
                    "front": {
                        "objects_detected": random.randint(3, 6),
                        "pedestrians": 0,
                        "vehicles": random.randint(2, 4),
                        "lane_detected": True,
                        "lane_confidence": random.uniform(0.8, 0.92),
                    },
                    "rear": {
                        "objects_detected": random.randint(2, 5),
                        "pedestrians": 0,
                        "vehicles": random.randint(1, 3),
                        "lane_detected": True,
                        "lane_confidence": random.uniform(0.75, 0.88),
                    },
                },
                "audio": {
                    "noise_level_db": random.uniform(70, 90),
                    "siren_detected": True,
                    "horn_detected": False,
                },
            },
            "context": {
                "location_type": "highway",
                "weather": "clear",
                "time_of_day": "day",
                "traffic_density": "medium",
                "emergency_vehicle_detected": True,
                "emergency_vehicle_direction": random.choice(["rear", "front", "side"]),
            },
        }


def print_event(event: dict):
    """Pretty print an event."""
    print("\n" + "=" * 60)
    print("VEHICLE EVENT")
    print("=" * 60)
    print(json.dumps(event, indent=2))
    print("=" * 60 + "\n")


def save_event(event: dict, filepath: str):
    """Save event to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(event, f, indent=2)
    print(f"Event saved to: {filepath}")


def interactive_mode(vehicle_id: str):
    """Run the simulator in interactive mode."""
    simulator = VehicleEventSimulator(vehicle_id)

    scenarios = [
        "normal",
        "heavy_traffic",
        "pedestrian_nearby",
        "sensor_missing",
        "emergency_vehicle",
    ]

    print("\n" + "=" * 60)
    print("VEHICLE EVENT SIMULATOR")
    print("=" * 60)
    print(f"Vehicle ID: {vehicle_id}")
    print("=" * 60)

    while True:
        print("\nSelect scenario:")
        for i, scenario in enumerate(scenarios, 1):
            print(f"  {i}. {scenario}")
        print("  0. Exit")

        choice = input("\nEnter choice (0-5): ").strip()

        if choice == "0":
            print("Exiting simulator...")
            break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(scenarios):
                scenario = scenarios[idx]
                event = simulator.generate_event(scenario)
                print_event(event)

                save = input("Save to file? (y/n): ").strip().lower()
                if save == "y":
                    filepath = f"sample_payloads/{scenario}_{int(datetime.now().timestamp())}.json"
                    save_event(event, filepath)
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Vehicle Event Simulator for MLOps Feature Store Demo"
    )
    parser.add_argument(
        "--vehicle-id",
        "-v",
        default="vehicle-001",
        help="Vehicle ID (default: vehicle-001)",
    )
    parser.add_argument(
        "--scenario",
        "-s",
        choices=[
            "normal",
            "heavy_traffic",
            "pedestrian_nearby",
            "sensor_missing",
            "emergency_vehicle",
        ],
        help="Generate a specific scenario (default: interactive mode)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (if not specified, prints to stdout)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )

    args = parser.parse_args()

    simulator = VehicleEventSimulator(args.vehicle_id)

    if args.interactive or not args.scenario:
        interactive_mode(args.vehicle_id)
    else:
        event = simulator.generate_event(args.scenario)

        if args.output:
            save_event(event, args.output)
        else:
            print_event(event)


if __name__ == "__main__":
    main()
