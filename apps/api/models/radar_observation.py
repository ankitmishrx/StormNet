"""Database model for gridded radar reflectivity observations."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class RadarObservationModel(Base):
    """Granular reflectivity observation associated with a specific radar frame and cell."""

    __tablename__ = "radar_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    frame_id = Column(UUID(as_uuid=True), ForeignKey("radar_frames.id", ondelete="CASCADE"), nullable=False, index=True)
    grid_cell_id = Column(String(64), nullable=True, index=True)

    timestamp = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    reflectivity = Column(Float, nullable=False)  # dBZ
    quality_flag = Column(String(32), nullable=False, default="VALID")

    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

    __table_args__ = (
        Index("idx_radar_obs_time_reflectivity", timestamp, reflectivity),
        Index("idx_radar_obs_geometry_gist", geometry, postgresql_using="gist"),
    )
