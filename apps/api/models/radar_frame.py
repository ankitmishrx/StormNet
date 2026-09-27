"""Database model for ingested Doppler Weather Radar frames."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class RadarFrameModel(Base):
    """Processed Doppler Weather Radar sweep or Cartesian composite frame."""

    __tablename__ = "radar_frames"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    radar_id = Column(String(64), nullable=False, index=True)  # e.g., DWR-DEL-SAF
    source = Column(String(64), nullable=False, default="DEVELOPMENT_SAMPLE")
    timestamp = Column(DateTime, nullable=False, index=True)
    product_type = Column(String(32), nullable=False, default="COMPOSITE_REFLECTIVITY")

    resolution_km = Column(Float, nullable=False, default=3.0)
    source_resolution_km = Column(Float, nullable=True, default=0.5)
    crs = Column(String(32), nullable=False, default="EPSG:4326")
    bounding_box = Column(JSONB, nullable=True)  # [min_lon, min_lat, max_lon, max_lat]

    coverage_area = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)
    status = Column(String(32), nullable=False, default="VALIDATED")  # VALIDATED, SAMPLE, DEGRADED

    total_cells_processed = Column(Integer, nullable=True, default=0)
    max_dbz = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_radar_frames_time_radar", timestamp, radar_id),
        Index("idx_radar_frames_coverage_gist", coverage_area, postgresql_using="gist"),
    )
