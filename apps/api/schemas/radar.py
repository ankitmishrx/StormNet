"""Pydantic schemas for Doppler Weather Radar API endpoints."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class RadarGridCellPoint(BaseModel):
    """Discrete gridded reflectivity point for web rendering."""

    latitude: float
    longitude: float
    reflectivity_dbz: float
    quality_flag: str = "VALID"


class RadarContourLevel(BaseModel):
    """Vector contour interval for calibrated dBZ rendering."""

    dbz_level: int
    color: str
    geometry: Dict[str, Any]  # GeoJSON Polygon / MultiPolygon


class RadarFrameSummary(BaseModel):
    """High-level summary of a radar observation frame."""

    id: UUID
    radar_id: str = Field(..., description="Radar Station Identifier (e.g. DWR-DEL-SAF)")
    source: str = Field(..., description="Data Source (e.g. DEVELOPMENT_SAMPLE, IMD_DWR)")
    timestamp: datetime
    product_type: str = "COMPOSITE_REFLECTIVITY"
    resolution_km: float = 3.0
    source_resolution_km: float = 0.5
    crs: str = "EPSG:4326"
    bounding_box: List[float]
    status: str = "VALIDATED"
    total_cells_processed: int
    max_dbz: float
    data_freshness: str = "SAMPLE"  # LIVE, HISTORICAL, REPLAY, SAMPLE, STALE, UNAVAILABLE


class RadarFrameDetail(RadarFrameSummary):
    """Detailed radar frame metadata and vector contours."""

    station_name: Optional[str] = "IMD Safdarjung DWR"
    contours: List[RadarContourLevel] = Field(default_factory=list)
    metadata_payload: Dict[str, Any] = Field(default_factory=dict)


class RadarGridResponse(BaseModel):
    """Gridded radar reflectivity observations for a specific frame."""

    frame_id: UUID
    timestamp: datetime
    resolution_km: float
    cells_count: int
    cells: List[RadarGridCellPoint]
    contours: List[RadarContourLevel] = Field(default_factory=list)


class RadarStatusResponse(BaseModel):
    """Radar network connectivity and data freshness status."""

    radar_id: str
    station_name: str
    status: str  # LIVE, HISTORICAL, REPLAY, SAMPLE, STALE, UNAVAILABLE
    latency_seconds: int
    last_observation_time: datetime
    active_sector: str
    resolution_km: float
    frequency_band: str
    is_live: bool = False
    disclaimer: str = "DEVELOPMENT / SAMPLE DATA ONLY (SIH26084)"
