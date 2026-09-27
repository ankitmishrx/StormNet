"""Database model for cell-level multi-source fused features."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class FusedGridFeatureModel(Base):
    """Normalized multi-sensor feature vector assigned to an individual 1–3 km grid cell."""

    __tablename__ = "fused_grid_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    frame_id = Column(UUID(as_uuid=True), ForeignKey("fused_grid_frames.id", ondelete="CASCADE"), nullable=False, index=True)
    grid_cell_id = Column(UUID(as_uuid=True), ForeignKey("grid_cells.id", ondelete="SET NULL"), nullable=True)
    grid_id = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    # Radar
    radar_reflectivity_dbz = Column(Float, nullable=True)
    radar_max_dbz = Column(Float, nullable=True)
    radar_precip_rate_mm_hr = Column(Float, nullable=True)

    # Satellite
    satellite_brightness_temp_k = Column(Float, nullable=True)
    satellite_cooling_rate_k_hr = Column(Float, nullable=True)

    # Lightning
    lightning_strike_count = Column(Integer, nullable=False, default=0)
    lightning_density_per_km2 = Column(Float, nullable=False, default=0.0)
    lightning_rate_per_min = Column(Float, nullable=False, default=0.0)
    lightning_trend = Column(String(32), nullable=False, default="STABLE")

    # Atmospheric
    atmospheric_temp_c = Column(Float, nullable=True)
    atmospheric_humidity_pct = Column(Float, nullable=True)
    atmospheric_pressure_hpa = Column(Float, nullable=True)
    atmospheric_wind_speed_kmh = Column(Float, nullable=True)

    composite_quality = Column(String(32), nullable=False, default="VALID")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_fused_features_grid_time", grid_id, timestamp.desc()),
        Index("idx_fused_features_geom_gist", geom, postgresql_using="gist"),
    )
