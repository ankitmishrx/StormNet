"""Database model for standard convective analysis grid cells."""

import uuid
from sqlalchemy import Column, String, Integer, Float, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class GridCell(Base):
    """Spatial grid tessellation (1km, 2km, or 3km) for nowcasting domains."""

    __tablename__ = "grid_cells"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_id = Column(String(64), nullable=True, unique=True, index=True)  # e.g., DEL-3KM-X024-Y031
    sector_id = Column(String(32), nullable=False, index=True)  # delhi-ncr, mumbai-konkan, etc.
    grid_size_km = Column(Float, nullable=False, default=3.0)

    grid_x = Column(Integer, nullable=False)
    grid_y = Column(Integer, nullable=False)
    center_lat = Column(Float, nullable=True)
    center_lon = Column(Float, nullable=True)

    elevation_m = Column(Float, nullable=True)
    geometry = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)

    __table_args__ = (
        Index("idx_grid_cells_geometry_gist", geometry, postgresql_using="gist"),
        Index("idx_grid_cells_sector_coords", sector_id, grid_x, grid_y),
    )
