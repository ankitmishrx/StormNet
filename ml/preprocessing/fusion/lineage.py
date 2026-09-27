"""Data Lineage and Provenance Tracking for Multi-Source Meteorological Fusion."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class LineageManifest(BaseModel):
    """Immutable audit record capturing source provenance, transformations, and versions."""
    manifest_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    fused_frame_id: uuid.UUID
    pipeline_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sector_id: str = "delhi-ncr"
    grid_version: str = "3km_grid_v1"
    grid_size_km: float = 3.0
    crs: str = "EPSG:4326"

    # Temporal Window details
    window_start: datetime
    window_end: datetime
    window_duration_seconds: int = 300

    # Sensor specifics
    sources_lineage: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    sensor_availability: Dict[str, bool] = Field(default_factory=dict)
    completeness_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serializes lineage manifest to JSON-compatible dictionary."""
        return {
            "manifest_id": str(self.manifest_id),
            "fused_frame_id": str(self.fused_frame_id),
            "pipeline_version": self.pipeline_version,
            "created_at": self.created_at.isoformat(),
            "sector_id": self.sector_id,
            "grid_version": self.grid_version,
            "grid_size_km": self.grid_size_km,
            "crs": self.crs,
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "window_duration_seconds": self.window_duration_seconds,
            "sources_lineage": self.sources_lineage,
            "sensor_availability": self.sensor_availability,
            "completeness_score": self.completeness_score,
        }
