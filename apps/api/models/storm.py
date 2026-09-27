"""Database model for convective storm entities."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class Storm(Base):
    """Represents an identified, segmented convective storm cell."""

    __tablename__ = "storms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cell_code = Column(String(64), unique=True, nullable=False, index=True)  # e.g. CNV-26084-DEL-01
    status = Column(String(32), nullable=False, default="ACTIVE")  # ACTIVE, DISSIPATING, MERGED, SPLIT
    severity_level = Column(String(16), nullable=False, default="YELLOW")  # GREEN, YELLOW, ORANGE, RED

    # Spatial geometry: Centroid and 2D bounding polygon boundary
    centroid = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    boundary = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)

    # Core physical diagnostics
    max_reflectivity_dbz = Column(Float, nullable=True)
    vertically_integrated_liquid = Column(Float, nullable=True)  # kg/m^2
    echo_top_height_km = Column(Float, nullable=True)  # km MSL
    cell_speed_kmh = Column(Float, nullable=True)
    cell_bearing_deg = Column(Float, nullable=True)

    # Lifecycle tracking
    first_detected_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_storms_centroid_gist", centroid, postgresql_using="gist"),
        Index("idx_storms_boundary_gist", boundary, postgresql_using="gist"),
        Index("idx_storms_status_severity", status, severity_level),
    )
