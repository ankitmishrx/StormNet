"""Database model for Spatio-Temporally Fused Multi-Source Observation Frames."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from apps.api.core.database import Base


class FusedGridFrameModel(Base):
    """Spatio-temporally aligned composite frame combining Radar, Satellite, Lightning, and AWS."""

    __tablename__ = "fused_grid_frames"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sector_id = Column(String(64), nullable=False, default="delhi-ncr", index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    resolution_km = Column(Float, nullable=False, default=3.0)

    data_freshness = Column(String(32), nullable=False, default="SAMPLE")  # LIVE, HISTORICAL, SAMPLE, STALE

    # Sensor availability tracking
    radar_available = Column(Boolean, nullable=False, default=False)
    satellite_available = Column(Boolean, nullable=False, default=False)
    lightning_available = Column(Boolean, nullable=False, default=False)
    atmospheric_available = Column(Boolean, nullable=False, default=False)
    completeness_score = Column(Float, nullable=False, default=0.0)

    total_cells = Column(Integer, nullable=False, default=0)
    quality_flag = Column(String(32), nullable=False, default="VALID")
    metadata_payload = Column(JSONB, nullable=True)  # Lineage manifest
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_fused_frames_sector_time", sector_id, timestamp.desc()),
    )
