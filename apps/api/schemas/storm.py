"""Pydantic schemas for convective storms and cell tracking."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class StormTrackPointSchema(BaseModel):
    """A single spatial point along a storm track."""
    timestamp: datetime
    lead_time_minutes: float
    coordinates: List[float] = Field(..., description="[longitude, latitude]")
    predicted_max_dbz: Optional[float] = None
    uncertainty_radius_km: Optional[float] = None


class StormBaseSchema(BaseModel):
    """Base convective cell attributes."""
    cell_code: str
    status: str
    severity_level: str
    max_reflectivity_dbz: Optional[float] = None
    vertically_integrated_liquid: Optional[float] = None
    echo_top_height_km: Optional[float] = None
    cell_speed_kmh: Optional[float] = None
    cell_bearing_deg: Optional[float] = None


class StormSummarySchema(StormBaseSchema):
    """Summary schema for storm list views and map markers."""
    id: UUID
    centroid_coordinates: List[float]
    first_detected_at: datetime
    last_updated_at: datetime


class StormDetailSchema(StormSummarySchema):
    """Comprehensive storm cell detail with boundary polygon and forecast track."""
    boundary_coordinates: Optional[List[List[List[float]]]] = None
    tracks: List[StormTrackPointSchema] = []
    hazard_summary: Optional[Dict[str, Any]] = None


class StormFilterParams(BaseModel):
    """Query filter parameters for storm listing."""
    sector_id: Optional[str] = None
    min_severity: Optional[str] = None
    min_dbz: Optional[float] = None
    status: Optional[str] = "ACTIVE"
