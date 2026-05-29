"""Risk Model Service for calculating risk scores based on vehicle features."""

from datetime import datetime, timezone
from typing import Any, Dict, Tuple


RULES = (
    {
        "field": "avg_speed_10s",
        "type": "threshold",
        "default": 0.0,
        "bands": (
            {"operator": "gt", "threshold": 60, "weight": 0.25},
            {"operator": "gt", "threshold": 40, "weight": 0.15},
        ),
    },
    {
        "field": "obstacle_distance_min",
        "type": "threshold",
        "default": float("inf"),
        "bands": (
            {"operator": "lt", "threshold": 10, "weight": 0.4},
            {"operator": "lt", "threshold": 20, "weight": 0.25},
            {"operator": "lt", "threshold": 30, "weight": 0.1},
        ),
    },
    {
        "field": "pedestrian_count",
        "type": "linear",
        "default": 0.0,
        "weight": 0.15,
    },
    {
        "field": "siren_detected",
        "type": "boolean",
        "default": False,
        "weight": 0.2,
    },
    {
        "field": "sensor_missing_rate",
        "type": "linear",
        "default": 0.0,
        "weight": 0.3,
    },
)

NORMALIZATION_MAX_SCORE = 1.5
HIGH_RISK_THRESHOLD = 0.7
MEDIUM_RISK_THRESHOLD = 0.4


class RiskModelService:
    """Service for calculating vehicle risk scores using rule-based scoring."""

    def _coerce_number(self, value: Any, default: float) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _apply_threshold_rule(self, feature_value: Any, rule: Dict[str, Any]) -> float:
        value = self._coerce_number(feature_value, rule["default"])
        for band in rule["bands"]:
            operator = band["operator"]
            threshold = band["threshold"]
            if operator == "lt" and value < threshold:
                return band["weight"]
            if operator == "gt" and value > threshold:
                return band["weight"]
        return 0.0

    def _apply_linear_rule(self, feature_value: Any, rule: Dict[str, Any]) -> float:
        value = self._coerce_number(feature_value, rule["default"])
        return value * rule["weight"]

    def _apply_boolean_rule(self, feature_value: Any, rule: Dict[str, Any]) -> float:
        return rule["weight"] if bool(feature_value) else 0.0

    def calculate_risk_score(self, features: Dict) -> Tuple[float, str]:
        """
        Calculate risk score and level based on vehicle features.

        Risk factors:
        - Obstacle distance: <10m = +0.4, <20m = +0.25, <30m = +0.1
        - Speed: >60 = +0.25, >40 = +0.15
        - Pedestrian count: +0.15 per pedestrian
        - Siren detected: +0.2
        - Sensor missing rate: +rate * 0.3

        Args:
            features: Dictionary containing vehicle features

        Returns:
            Tuple of (risk_score, risk_level) where:
            - risk_score: float between 0 and 1
            - risk_level: "HIGH" (>=0.7), "MEDIUM" (>=0.4), or "LOW" (<0.4)
        """
        raw_score = 0.0

        for rule in RULES:
            feature_value = features.get(rule["field"], rule["default"])
            if rule["type"] == "threshold":
                raw_score += self._apply_threshold_rule(feature_value, rule)
            elif rule["type"] == "linear":
                raw_score += self._apply_linear_rule(feature_value, rule)
            elif rule["type"] == "boolean":
                raw_score += self._apply_boolean_rule(feature_value, rule)

        normalized_score = min(raw_score / NORMALIZATION_MAX_SCORE, 1.0)

        if normalized_score >= HIGH_RISK_THRESHOLD:
            risk_level = "HIGH"
        elif normalized_score >= MEDIUM_RISK_THRESHOLD:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return (normalized_score, risk_level)

    def predict(self, vehicle_id: str, features: Dict) -> Dict:
        """
        Make risk prediction for a vehicle.

        Args:
            vehicle_id: Unique identifier for the vehicle
            features: Dictionary containing vehicle features

        Returns:
            Dictionary with prediction results including:
            - vehicle_id: The vehicle identifier
            - risk_score: Calculated risk score (0-1)
            - risk_level: Risk level (HIGH, MEDIUM, LOW)
            - timestamp: UTC timestamp of the prediction
        """
        risk_score, risk_level = self.calculate_risk_score(features)

        return {
            "vehicle_id": vehicle_id,
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
