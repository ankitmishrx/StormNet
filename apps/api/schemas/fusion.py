"""Pydantic schemas for Multi-Source Meteorological Fusion API."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FusedCellFeatureDTO(BaseModel):
    """Normalized multi-sensor feature values for a single grid cell."""
    grid_id: str
    latitude: float
    longitude: float
    grid_size_km: float = 3.0

    radar_reflectivity_dbz: Optional[float] = None
    radar_max_dbz: Optional[float] = None
    radar_precip_rate_mm_hr: Optional[float] = None

    satellite_brightness_temp_k: Optional[float] = None
    satellite_cooling_rate_k_hr: Optional[float] = None

    lightning_strike_count: int = 0
    lightning_density_per_km2: float = 0.0
    lightning_rate_per_min: float = 0.0
    lightning_trend: str = "STABLE"

    atmospheric_temp_c: Optional[float] = None
    atmospheric_humidity_pct: Optional[float] = None
    atmospheric_pressure_hpa: Optional[float] = None
    atmospheric_wind_speed_kmh: Optional[float] = None

    composite_quality: str = "VALID"


class FusedFrameDetailResponse(BaseModel):
    """Complete detail response for a synchronized multi-source observation frame."""
    id: uuid.UUID
    sector_id: str
    timestamp: datetime
    window_start: datetime
    window_end: datetime
    resolution_km: float
    data_freshness: str
    radar_available: bool
    satellite_available: bool
    lightning_available: bool
    atmospheric_available: bool
    completeness_score: float
    total_cells: int
    cells: List[FusedCellFeatureDTO] = Field(default_factory=list)
    lineage_metadata: Optional[Dict[str, Any]] = None


class FusedGridCellHistoryResponse(BaseModel):
    """Historical time-series features for an individual grid cell."""
    grid_id: str
    latitude: float
    longitude: float
    history: List[FusedCellFeatureDTO] = Field(default_factory=list)


class DataSourceStatusDTO(BaseModel):
    """Diagnostic health status for a single physical data stream."""
    source_type: str  # RADAR, SATELLITE, LIGHTNING, AWS
    provider_name: str
    status: str  # ONLINE, DEGRADED, OFFLINE, SAMPLE
    latency_seconds: Optional[float] = 0.0
    last_received_at: Optional[datetime] = None
    is_available: bool = True
    data_freshness: str = "SAMPLE"
    metadata_payload: Optional[Dict[str, Any]] = None


class FusionNetworkStatusResponse(BaseModel):
    """Aggregate multi-sensor network health and overall completeness."""
    sector_id: str
    active_sources_count: int
    total_sources_count: int = 4
    network_completeness_ratio: float
    data_freshness: str
    last_fusion_timestamp: Optional[datetime] = None
    sources: List[DataSourceStatusDTO] = Field(default_factory=list)
    disclaimer: str = "DEVELOPMENT / SAMPLE MULTI-SOURCE FEEDS ONLY (SIH26084)"
