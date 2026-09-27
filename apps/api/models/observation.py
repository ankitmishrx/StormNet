"""Database model for ingested meteorological observation sweeps."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class Observation(Base):
    """Raw and preprocessed multi-source meteorological observations."""

    __tablename__ = "observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(32), nullable=False)  # RADAR_DWR, SATELLITE_INSAT, LIGHTNING_LLN, SURFACE_AWS
    station_code = Column(String(64), nullable=True)  # e.g., DWR-DEL-SAF, DWR-MUM-CLB

    observation_time = Column(DateTime, nullable=False, index=True)
    ingested_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Coverage footprint polygon or sensor point location
    coverage_area = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)

    # File storage references & quality metadata
    file_path = Column(String(512), nullable=True)
    metadata_payload = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_observations_time_source", observation_time, source_type),
        Index("idx_observations_coverage_gist", coverage_area, postgresql_using="gist"),
    )
