"""Database model for cached vector contours and tile products."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from apps.api.core.database import Base


class RadarProductModel(Base):
    """Cached derivative radar product (e.g. vector contours, pre-rendered surfaces)."""

    __tablename__ = "radar_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    frame_id = Column(UUID(as_uuid=True), ForeignKey("radar_frames.id", ondelete="CASCADE"), nullable=False, index=True)

    product_type = Column(String(32), nullable=False, default="VECTOR_CONTOURS")
    min_dbz = Column(Float, nullable=True)
    max_dbz = Column(Float, nullable=True)
    mean_dbz = Column(Float, nullable=True)

    geojson_contours = Column(JSONB, nullable=True)
    tile_url = Column(String(512), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
