"""Pydantic schemas for the Spatiotemporal U-Net Nowcasting API."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class NowcastPredictRequest(BaseModel):
    """Request payload to trigger nowcast inference."""
    sector_id: str = Field("delhi-ncr", description="Sector identifier")
    lead_times_minutes: List[int] = Field(
        default_factory=lambda: [5, 10, 15, 20, 25, 30],
        description="Forecast lead times in minutes (validated up to 30 min)",
    )
    anchor_timestamp: Optional[datetime] = Field(None, description="Anchor observation time T-0")
    model_version: str = Field("1.0.0", description="Model architecture version")


class NowcastFrameDTO(BaseModel):
    """Forecast frame for a single future lead step."""
    lead_time_minutes: int
    forecast_timestamp: datetime
    domain_max_dbz: float
    confidence_score: float
    validated_horizon: bool = Field(True, description="True if within validated <=30m empirical horizon")
    sample_grid_predictions: Optional[List[Dict[str, Any]]] = Field(
        None, description="Drilldown grid cell predictions for key monitored nodes"
    )


class NowcastResponse(BaseModel):
    """Complete response container from the nowcasting inference engine."""
    run_id: str
    model_name: str
    model_version: str
    dataset_version: str
    feature_version: str
    grid_version: str
    sector_id: str
    anchor_timestamp: datetime
    inference_duration_ms: float
    data_source_status: Dict[str, Any]
    validated_horizon_minutes: int
    frames: List[NowcastFrameDTO]
    disclaimer: str = Field(
        "DEVELOPMENT PROTOTYPE: Validated empirical horizon is 30 minutes. Extrapolations beyond 30 min are experimental.",
        description="Scientific validation disclaimer",
    )
