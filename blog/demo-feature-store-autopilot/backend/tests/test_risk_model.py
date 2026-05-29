"""Tests for Risk Model Service."""

import pytest
from app.services.risk_model import RiskModelService
from app.services.feature_registry import get_prediction_feature_names
from app.services.risk_model import RULES


class TestRiskModelService:
    """Test suite for RiskModelService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = RiskModelService()

    def test_low_risk_calculation(self):
        """Test that low risk scenario returns score < 0.4 and level LOW."""
        features = {
            "obstacle_distance_min": 50.0,
            "avg_speed_10s": 30.0,
            "pedestrian_count": 0,
            "siren_detected": False,
            "sensor_missing_rate": 0.0
        }

        score, level = self.service.calculate_risk_score(features)

        assert 0 <= score <= 1
        assert level == "LOW"
        assert score < 0.4

    def test_high_risk_calculation(self):
        """Test that high risk scenario returns score >= 0.7 and level HIGH."""
        features = {
            "obstacle_distance_min": 5.0,
            "avg_speed_10s": 70.0,
            "pedestrian_count": 3,
            "siren_detected": True,
            "sensor_missing_rate": 0.5
        }

        score, level = self.service.calculate_risk_score(features)

        assert 0 <= score <= 1
        assert level == "HIGH"
        assert score >= 0.7

    def test_medium_risk_calculation(self):
        """Test that medium risk scenario returns score >= 0.4 and < 0.7 and level MEDIUM."""
        features = {
            "obstacle_distance_min": 15.0,
            "avg_speed_10s": 45.0,
            "pedestrian_count": 2,
            "siren_detected": True,
            "sensor_missing_rate": 0.2
        }

        score, level = self.service.calculate_risk_score(features)

        assert 0 <= score <= 1
        assert level == "MEDIUM"
        assert 0.4 <= score < 0.7

    def test_predict_returns_correct_structure(self):
        """Test that predict method returns dict with required fields."""
        features = {
            "obstacle_distance_min": 50.0,
            "avg_speed_10s": 30.0,
            "pedestrian_count": 0,
            "siren_detected": False,
            "sensor_missing_rate": 0.0
        }

        result = self.service.predict(vehicle_id="vehicle-1", features=features)

        assert isinstance(result, dict)
        assert "vehicle_id" in result
        assert "risk_score" in result
        assert "risk_level" in result
        assert "timestamp" in result
        assert result["vehicle_id"] == "vehicle-1"

    def test_risk_score_normalized_to_0_1(self):
        """Test that risk score is always normalized between 0 and 1."""
        # Extreme low risk
        features_low = {
            "obstacle_distance_min": 100.0,
            "avg_speed_10s": 0.0,
            "pedestrian_count": 0,
            "siren_detected": False,
            "sensor_missing_rate": 0.0
        }

        # Extreme high risk
        features_high = {
            "obstacle_distance_min": 0.0,
            "avg_speed_10s": 120.0,
            "pedestrian_count": 10,
            "siren_detected": True,
            "sensor_missing_rate": 1.0
        }

        score_low, _ = self.service.calculate_risk_score(features_low)
        score_high, _ = self.service.calculate_risk_score(features_high)

        assert 0 <= score_low <= 1
        assert 0 <= score_high <= 1

    def test_obstacle_distance_contribution(self):
        """Test obstacle distance risk contribution."""
        # Very close obstacle should add significant risk
        features_close = {
            "obstacle_distance_min": 5.0,
            "avg_speed_10s": 0.0,
            "pedestrian_count": 0,
            "siren_detected": False,
            "sensor_missing_rate": 0.0
        }

        # Far obstacle should add minimal risk
        features_far = {
            "obstacle_distance_min": 100.0,
            "avg_speed_10s": 0.0,
            "pedestrian_count": 0,
            "siren_detected": False,
            "sensor_missing_rate": 0.0
        }

        score_close, _ = self.service.calculate_risk_score(features_close)
        score_far, _ = self.service.calculate_risk_score(features_far)

        assert score_close > score_far

    def test_speed_contribution(self):
        """Test speed risk contribution."""
        # High speed should add risk
        features_high_speed = {
            "obstacle_distance_min": 100.0,
            "avg_speed_10s": 70.0,
            "pedestrian_count": 0,
            "siren_detected": False,
            "sensor_missing_rate": 0.0
        }

        # Low speed should add minimal risk
        features_low_speed = {
            "obstacle_distance_min": 100.0,
            "avg_speed_10s": 20.0,
            "pedestrian_count": 0,
            "siren_detected": False,
            "sensor_missing_rate": 0.0
        }

        score_high_speed, _ = self.service.calculate_risk_score(features_high_speed)
        score_low_speed, _ = self.service.calculate_risk_score(features_low_speed)

        assert score_high_speed > score_low_speed

    def test_siren_detected_contribution(self):
        """Test siren detected risk contribution."""
        features_with_siren = {
            "obstacle_distance_min": 100.0,
            "avg_speed_10s": 30.0,
            "pedestrian_count": 0,
            "siren_detected": True,
            "sensor_missing_rate": 0.0
        }

        features_without_siren = {
            "obstacle_distance_min": 100.0,
            "avg_speed_10s": 30.0,
            "pedestrian_count": 0,
            "siren_detected": False,
            "sensor_missing_rate": 0.0
        }

        score_with_siren, _ = self.service.calculate_risk_score(features_with_siren)
        score_without_siren, _ = self.service.calculate_risk_score(features_without_siren)

        assert score_with_siren > score_without_siren

    def test_rule_fields_match_prediction_feature_names(self):
        """Risk rules should stay aligned with the registry prediction subset."""
        assert {rule["field"] for rule in RULES} == set(get_prediction_feature_names())
