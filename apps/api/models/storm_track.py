"""Database model for historical and extrapolated storm trajectory tracks."""

import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Float, DateTime, String, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class StormTrack(Base):
    """Historical centroid positions and projected future trajectory vectors."""

    __tablename__ = "storm_tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storm_id = Column(UUID(as_uuid=True), ForeignKey("storms.id", ondelete="CASCADE"), nullable=False, index=True)

    # Track classification: HISTORICAL, NOWCAST_PREDICTION
    track_type = Column(String(32), nullable=False, default="NOWCAST_PREDICTION")
    timestamp = Column(DateTime, nullable=False, index=True)
    lead_time_minutes = Column(Float, nullable=False, default=0.0)  # 0, 15, 30, 45, 60... 360

    # Spatial geometry
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    trajectory_segment = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=True)

    # Physical diagnostics along track
    predicted_max_dbz = Column(Float, nullable=True)
    uncertainty_radius_km = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_storm_tracks_location_gist", location, postgresql_using="gist"),
        Index("idx_storm_tracks_storm_timestamp", storm_id, timestamp),
        Index("idx_storm_tracks_lead_time", lead_time_minutes),
    )
