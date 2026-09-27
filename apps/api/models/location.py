"""Database model for geographical and administrative reference locations."""

import uuid
from sqlalchemy import Column, String, Integer, Float, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class Location(Base):
    """Administrative and strategic reference points (Districts, Airports, Cities)."""

    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False, index=True)
    location_type = Column(String(32), nullable=False)  # DISTRICT, TALUK, AIRPORT, RADAR_SITE, AWS_STATION
    state = Column(String(64), nullable=False, index=True)
    district = Column(String(64), nullable=True, index=True)

    elevation_m = Column(Float, nullable=True)
    population = Column(Integer, nullable=True)

    # Geometry: Point location or district boundary polygon
    point = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    boundary = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)

    __table_args__ = (
        Index("idx_locations_point_gist", point, postgresql_using="gist"),
        Index("idx_locations_boundary_gist", boundary, postgresql_using="gist"),
        Index("idx_locations_type_state", location_type, state),
    )
