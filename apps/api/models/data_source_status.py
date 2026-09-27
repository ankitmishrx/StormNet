"""Database model for tracking operational status and freshness of meteorological data sources."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from apps.api.core.database import Base


class DataSourceStatusModel(Base):
    """Operational health status, latency, and freshness tier for a registered data stream."""

    __tablename__ = "data_source_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(32), unique=True, nullable=False, index=True)  # RADAR, SATELLITE, LIGHTNING, AWS
    provider_name = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="ONLINE")  # ONLINE, DEGRADED, OFFLINE, SAMPLE
    latency_seconds = Column(Float, nullable=True, default=0.0)
    last_received_at = Column(DateTime, nullable=True)
    is_available = Column(Boolean, nullable=False, default=True)
    data_freshness = Column(String(32), nullable=False, default="SAMPLE")
    metadata_payload = Column(JSONB, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
