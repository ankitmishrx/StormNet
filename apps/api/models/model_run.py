"""Database model for ML nowcasting execution runs and provenance tracking."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from apps.api.core.database import Base


class ModelRun(Base):
    """Provenance and telemetry logs for ML nowcasting execution cycles."""

    __tablename__ = "model_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(64), nullable=False)  # e.g., StormNet-ConvLSTM-v1, OpticalFlow-Baseline
    model_version = Column(String(32), nullable=False)
    sector_id = Column(String(32), nullable=False, index=True)

    base_time = Column(DateTime, nullable=False, index=True)  # Radar T-0 time used for input
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    execution_duration_sec = Column(Float, nullable=True)
    status = Column(String(32), nullable=False, default="RUNNING")  # RUNNING, COMPLETED, FAILED

    parameters = Column(JSONB, nullable=True)
    metrics = Column(JSONB, nullable=True)
    error_message = Column(String(1024), nullable=True)

    __table_args__ = (
        Index("idx_model_runs_sector_base", sector_id, base_time),
        Index("idx_model_runs_status", status),
    )
