"""Pydantic schemas for 0-6 hour nowcast frames."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class ForecastFrameSchema(BaseModel):
    """A single discrete nowcast frame along the 0-6 hr timeline."""
    id: UUID
    sector_id: str
    base_time: datetime
    forecast_time: datetime
    lead_time_minutes: int
    raster_tile_path: Optional[str] = None
    domain_max_dbz: Optional[float] = None
    confidence_index: float = Field(..., ge=0.0, le=1.0)
    extent_bbox: Optional[List[float]] = None
    metrics_summary: Optional[Dict[str, Any]] = None


class ForecastTimelineResponse(BaseModel):
    """Collection of nowcast steps from T-0 to T+6h."""
    sector_id: str
    base_time: datetime
    frames: List[ForecastFrameSchema]
    total_steps: int
    cadence_minutes: int
