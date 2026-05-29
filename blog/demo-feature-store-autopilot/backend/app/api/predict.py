from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services import FeastService, RiskModelService
from app.services.feature_registry import (
    get_prediction_fallback_defaults,
    get_prediction_feature_names,
)

router = APIRouter()

# Lazy initialization for services
_feast_service: Optional[FeastService] = None
_risk_model: Optional[RiskModelService] = None


def get_feast_service() -> FeastService:
    """Get or create Feast service instance (lazy initialization)."""
    global _feast_service
    if _feast_service is None:
        _feast_service = FeastService(repo_path="./feast_repo")
    return _feast_service


def get_risk_model() -> RiskModelService:
    """Get or create RiskModel service instance (lazy initialization)."""
    global _risk_model
    if _risk_model is None:
        _risk_model = RiskModelService()
    return _risk_model


class PredictRequest(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle ID for prediction")


class PredictResponse(BaseModel):
    vehicle_id: str
    features: dict
    risk_score: float
    risk_level: str


def _build_prediction_features(online_features: Optional[dict]) -> dict:
    """Build the feature payload used by the risk model.

    The payload keeps the registry-defined prediction feature subset stable even
    when Feast returns nothing or omits individual keys.
    """
    prediction_defaults = get_prediction_fallback_defaults()
    feature_names = get_prediction_feature_names()

    features = dict(prediction_defaults)
    if online_features:
        for feature_name in feature_names:
            value = online_features.get(feature_name)
            if value is not None:
                features[feature_name] = value

    return features


@router.post("", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """Predict risk score for a vehicle"""
    try:
        # Get online features from Feast
        feast_service = get_feast_service()
        online_features = feast_service.get_online_features(vehicle_id=request.vehicle_id)
        features = _build_prediction_features(online_features)

        # Calculate risk score using RiskModelService
        risk_model = get_risk_model()
        prediction = risk_model.predict(vehicle_id=request.vehicle_id, features=features)

        return PredictResponse(
            vehicle_id=request.vehicle_id,
            features=features,
            risk_score=prediction["risk_score"],
            risk_level=prediction["risk_level"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making prediction: {str(e)}")
