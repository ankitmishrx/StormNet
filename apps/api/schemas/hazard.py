"""Pydantic schemas for convective hazard probabilities and risk scoring."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class HazardCardSchema(BaseModel):
    """Schema for individual hazard probability cards in the UI."""
    hazard_type: str  # CLOUDBURST, HAIL, SQUALL, LIGHTNING
    title: str
    probability: float = Field(..., ge=0.0, le=1.0)
    warning_level: str  # GREEN, YELLOW, ORANGE, RED
    metric_value: Optional[float] = None
    metric_unit: Optional[str] = None
    threshold_alert: str
    time_to_impact_minutes: Optional[int] = None


class HazardPredictionDetailSchema(BaseModel):
    """Comprehensive hazard prediction model."""
    id: UUID
    storm_id: Optional[UUID] = None
    forecast_id: Optional[UUID] = None
    timestamp: datetime
    lead_time_minutes: float

    # Core hazard probabilities
    cloudburst_probability: float
    hail_probability: float
    severe_wind_probability: float
    lightning_density_score: float

    # Physical estimates
    max_hail_diameter_cm: Optional[float] = None
    peak_wind_gust_kmh: Optional[float] = None
    estimated_rainfall_rate_mmh: Optional[float] = None

    cards: List[HazardCardSchema] = []
