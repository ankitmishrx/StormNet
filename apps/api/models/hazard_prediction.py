"""Database model for cell-level and grid-level convective hazard probabilities."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class HazardPrediction(Base):
    """Categorical and probabilistic predictions for severe convective phenomena."""

    __tablename__ = "hazard_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storm_id = Column(UUID(as_uuid=True), ForeignKey("storms.id", ondelete="CASCADE"), nullable=True, index=True)
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("forecasts.id", ondelete="CASCADE"), nullable=True, index=True)

    timestamp = Column(DateTime, nullable=False, index=True)
    lead_time_minutes = Column(Float, nullable=False, default=0.0)

    # Core hazard probabilities (0.0 to 1.0)
    cloudburst_probability = Column(Float, nullable=False, default=0.0)  # >100mm/hr trigger
    hail_probability = Column(Float, nullable=False, default=0.0)  # Hail core probability
    severe_wind_probability = Column(Float, nullable=False, default=0.0)  # Squall / microburst
    lightning_density_score = Column(Float, nullable=False, default=0.0)

    # Physical expected severity
    max_hail_diameter_cm = Column(Float, nullable=True)
    peak_wind_gust_kmh = Column(Float, nullable=True)
    estimated_rainfall_rate_mmh = Column(Float, nullable=True)

    # Spatial impact footprint
    impact_zone = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)
    details = Column(JSONB, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_hazard_predictions_storm_time", storm_id, timestamp),
        Index("idx_hazard_predictions_impact_gist", impact_zone, postgresql_using="gist"),
        Index("idx_hazard_predictions_cloudburst_prob", cloudburst_probability),
    )
